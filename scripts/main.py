from collections import defaultdict
import logging
import re
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import groq
from search_core import SearchEngine, IPC_TO_BNS, IPC_OMITTED, extract_ipc_sections
from rag_core import (
    generate_explanation,
    translate_to_english,
    translate_explanation,
    detect_language,
    verify_citations,
    get_static_message,
    get_cached_explanation,
    save_cached_explanation,
)
from citations_core import find_related_cases, load_citations
from pdf_core import extract_text_from_pdf, answer_question_about_document, summarize_document, extract_dates_and_deadlines
from dictionary_core import define_term
from drafter_core import draft_document, DOCUMENT_TYPES
from case_simplifier_core import simplify_case
from bns_decoder_core import explain_bns_section

logger = logging.getLogger(__name__)

# Per-IP in-memory rate limiting for Groq-calling endpoints (20 req/min)
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 60  # 1 minute

_ip_timestamps: dict[str, list[float]] = defaultdict(list)

RATE_LIMIT_MESSAGES = {
    "en": "Too many requests. Please wait a minute before trying again (limit: 20 requests per minute).",
    "hi": "बहुत अधिक अनुरोध। कृपया एक मिनट बाद पुनः प्रयास करें (सीमा: प्रति मिनट 20 अनुरोध)।",
    "kn": "ಹೆಚ್ಚಿನ ವಿನಂತಿಗಳು ಬಂದಿವೆ. ದಯವಿಟ್ಟು ಒಂದು ನಿಮಿಷದ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ (ಮಿತಿ: ನಿಮಿಷಕ್ಕೆ 20 ವಿನಂತಿಗಳು).",
}


def get_client_ip(request: Request) -> str:
    """Extract client IP behind Azure reverse proxy (first value of X-Forwarded-For), falling back to request.client.host."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


def check_rate_limit(request: Request, language: str = "en") -> None:
    """Checks and records a request for the client IP.
    Raises HTTPException(429) if the client has exceeded RATE_LIMIT_REQUESTS within RATE_LIMIT_WINDOW_SECONDS.
    """
    ip = get_client_ip(request)
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS

    history = [t for t in _ip_timestamps[ip] if t > cutoff]
    if len(history) >= RATE_LIMIT_REQUESTS:
        _ip_timestamps[ip] = history
        lang = language if language in RATE_LIMIT_MESSAGES else "en"
        msg = RATE_LIMIT_MESSAGES[lang]
        raise HTTPException(status_code=429, detail=msg)

    history.append(now)
    _ip_timestamps[ip] = history


def reset_rate_limits() -> None:
    """Reset all stored timestamps (primarily for tests)."""
    _ip_timestamps.clear()


app = FastAPI(title="NyaayaSearch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = None

document_store = {}


@app.on_event("startup")
def load_engine():
    global engine
    engine = SearchEngine()


class SectionReference(BaseModel):
    act_name: str
    section_number: str | int


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    rerank: bool | None = None
    language: str | None = None
    sections: list[SectionReference] | None = None


class DocumentQuestionRequest(BaseModel):
    document_id: str
    question: str


class DefineRequest(BaseModel):
    term: str


class TranslateExplanationRequest(BaseModel):
    text: str
    target_language: str  # "en", "hi", or "kn"


def attach_related_cases(results):
    for r in results:
        try:
            r["related_cases"] = find_related_cases(r["act_name"], r["section_number"])
        except Exception:
            r["related_cases"] = []
    return results


def validate_query(query):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Please enter a question or describe your situation to search.")
    if len(query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Please enter a more complete question - a few words isn't enough to search well.")
    if len(query) > 2000:
        raise HTTPException(status_code=400, detail="That question is too long. Please shorten it to under 2000 characters.")


# Common romanized Hindi and Kannada words (excluding common English words like me, do, to, so, is, in, on, he)
ROMANIZED_HINDI_WORDS = {
    "hai", "hain", "nahi", "nahin", "kya", "karu", "karun", "mera", "meri", "mujhe",
    "raha", "rahi", "wapas", "vapas", "pati", "kaise", "kyun", "chahiye",
}
ROMANIZED_KANNADA_WORDS = {
    "nanna", "nanage", "illa", "kodtilla", "maadi", "hege", "enu", "beku", "beda", "mane",
}
ROMANIZED_VERNACULAR_WORDS = ROMANIZED_HINDI_WORDS | ROMANIZED_KANNADA_WORDS

ROMANIZED_HINDI_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in sorted(ROMANIZED_HINDI_WORDS)) + r")\b",
    re.IGNORECASE,
)
ROMANIZED_KANNADA_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in sorted(ROMANIZED_KANNADA_WORDS)) + r")\b",
    re.IGNORECASE,
)
ROMANIZED_VERNACULAR_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in sorted(ROMANIZED_VERNACULAR_WORDS)) + r")\b",
    re.IGNORECASE,
)


def resolve_search_query(query: str, raw_request: Request = None):
    """Detect language and only call translate_to_english() when query is not English
    or contains common romanized Hindi/Kannada words.
    If translation fails (rate limit, error), log it clearly and return a clear error.
    """
    detected_language = detect_language(query)
    is_romanized_hi = False
    is_romanized_kn = False

    if detected_language == "en":
        hi_matches = len(ROMANIZED_HINDI_PATTERN.findall(query))
        kn_matches = len(ROMANIZED_KANNADA_PATTERN.findall(query))
        if kn_matches > hi_matches:
            detected_language = "kn"
            is_romanized_kn = True
        elif hi_matches > 0:
            detected_language = "hi"
            is_romanized_hi = True

    is_romanized = is_romanized_hi or is_romanized_kn

    if detected_language != "en" or is_romanized:
        if raw_request is not None:
            check_rate_limit(raw_request, language=detected_language)
        try:
            search_query = translate_to_english(query)
        except groq.RateLimitError as e:
            logger.error(f"Translation rate limited for query '{query}': {e}")
            raise HTTPException(
                status_code=503,
                detail="Translation service is temporarily unavailable due to rate limits. Please try again shortly.",
            )
        except Exception as e:
            logger.error(f"Translation failed for query '{query}': {e}", exc_info=True)
            raise HTTPException(
                status_code=502,
                detail="Failed to translate query into English. Please try again or rephrase your question in English.",
            )
    else:
        search_query = query
    return search_query, detected_language


@app.get("/")
def root():
    return {"status": "NyaayaSearch API is running"}


@app.get("/stats")
def stats():
    acts = set()
    for record in engine.records:
        name = str(record.get("act_name") or "").strip()
        # Guard against a stray header-like row occasionally present in the
        # source workbook (act_name == "act_name"), which would otherwise
        # inflate the count by one.
        if name and name.lower() != "act_name":
            acts.add(name)

    try:
        citations_df = load_citations()
        supreme_court_cases = int(citations_df.loc[citations_df["low_confidence"] == False, "case_id"].nunique())
    except Exception:
        supreme_court_cases = 0

    return {
        "acts": len(acts),
        "sections": len(engine.records),
        "supreme_court_cases": supreme_court_cases,
    }


@app.post("/search")
def search(request: SearchRequest, raw_request: Request):
    validate_query(request.query)
    search_query, detected_language = resolve_search_query(request.query, raw_request=raw_request)
    target_language = request.language if request.language in ("en", "hi", "kn") else detected_language
    try:
        rerank = True if request.rerank is None else request.rerank
        results = engine.search(search_query, top_k=request.top_k, rerank=rerank)
        results = attach_related_cases(results)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search failed unexpectedly. Please try again.")

    CONFIDENCE_THRESHOLD = 0.30
    top_score = results[0].get("hybrid_score", 0) if results else 0
    low_confidence = bool(results and top_score < CONFIDENCE_THRESHOLD)

    explanation = None
    if not results:
        explanation = get_static_message("no_results", target_language)
    elif low_confidence:
        acts_seen = {}
        sec_prefix = get_static_message("section_label", target_language) + " "
        for r in results:
            act = r["act_name"]
            if act not in acts_seen:
                acts_seen[act] = []
            acts_seen[act].append(sec_prefix + str(r["section_number"]) + ": " + str(r["section_title"]))
        candidates_text = ""
        for act, sections in acts_seen.items():
            candidates_text += "\n" + act + ":\n" + "\n".join("  - " + s for s in sections)
        explanation = get_static_message("low_confidence_prefix", target_language) + candidates_text

    return {
        "query": request.query,
        "translated_query": search_query,
        "detected_language": detected_language,
        "results": results,
        "low_confidence": low_confidence,
        "explanation": explanation,
    }


@app.post("/explain")
def explain(request: SearchRequest, raw_request: Request):
    validate_query(request.query)

    detected_language = detect_language(request.query)
    target_language = request.language if request.language in ("en", "hi", "kn") else detected_language
    check_rate_limit(raw_request, language=target_language)

    search_query, detected_language = resolve_search_query(request.query)
    if not (request.language in ("en", "hi", "kn")):
        target_language = detected_language

    if request.sections is not None:
        record_map = getattr(engine, "record_map", None)
        if record_map is None:
            record_map = {
                (str(r.get("act_name") or "").strip().lower(), str(r.get("section_number") or "").strip().lower()): r
                for r in engine.records
            }
            engine.record_map = record_map

        results = []
        for s in request.sections:
            act = str(s.act_name or "").strip().lower()
            sec = str(s.section_number or "").strip().lower()
            rec = record_map.get((act, sec))
            if rec:
                results.append(dict(rec))
    else:
        try:
            rerank = True if request.rerank is None else request.rerank
            results = engine.search(search_query, top_k=request.top_k, rerank=rerank)
            results = attach_related_cases(results)
        except Exception:
            raise HTTPException(status_code=500, detail="Search failed unexpectedly. Please try again.")

    if not results:
        return {
            "query": request.query,
            "translated_query": search_query,
            "results": [],
            "explanation": get_static_message("no_results", target_language),
            "language": target_language,
            "model_used": None,
        }

    CONFIDENCE_THRESHOLD = 0.30
    top_score = results[0].get("hybrid_score", 0) if results else 0
    if request.sections is None and top_score < CONFIDENCE_THRESHOLD:
        acts_seen = {}
        sec_prefix = get_static_message("section_label", target_language) + " "
        for r in results:
            act = r["act_name"]
            if act not in acts_seen:
                acts_seen[act] = []
            acts_seen[act].append(sec_prefix + str(r["section_number"]) + ": " + str(r["section_title"]))
        candidates_text = ""
        for act, sections in acts_seen.items():
            candidates_text += "\n" + act + ":\n" + "\n".join("  - " + s for s in sections)
        return {
            "query": request.query,
            "translated_query": search_query,
            "results": results,
            "explanation": get_static_message("low_confidence_prefix", target_language) + candidates_text,
            "language": target_language,
            "low_confidence": True,
            "model_used": None,
        }

    cached = get_cached_explanation(request.query, target_language, results)
    if cached is not None:
        cached_exp = cached.get("explanation", cached) if isinstance(cached, dict) else str(cached)
        cached_model = cached.get("model_used", "openai/gpt-oss-120b") if isinstance(cached, dict) else "openai/gpt-oss-120b"
        return {
            "query": request.query,
            "translated_query": search_query,
            "results": results,
            "explanation": cached_exp,
            "language": target_language,
            "model_used": cached_model,
        }

    model_used = None
    try:
        explanation_query = request.query
        ipc_secs = extract_ipc_sections(explanation_query)
        for num in ipc_secs:
            bns_list = IPC_TO_BNS.get(num, [])
            num_display = num.upper()
            if bns_list:
                bns_str = ", ".join(bns_list) if len(bns_list) > 1 else bns_list[0]
                explanation_query += f" (Note: IPC Section {num_display} corresponds to BNS Section {bns_str} under the current law - please explain using the BNS section shown in the results below.)"
                break
            elif num in IPC_OMITTED or (num in IPC_TO_BNS and not bns_list):
                explanation_query += f" (Note: IPC Section {num_display} was not carried over into the BNS.)"
                break
        explanation, model_used = generate_explanation(
            explanation_query, results, language=target_language, return_model=True
        )
        is_valid, unverified_sections = verify_citations(explanation, results)
        if not is_valid:
            explanation += "\n\n[Note: this explanation may reference a section number not confirmed in our search results (" + ", ".join(unverified_sections) + "). Please cross-check with the original statutory text shown above.]"
        save_cached_explanation(request.query, target_language, results, explanation, model_used)
    except groq.RateLimitError:
        explanation = get_static_message("rate_limit", target_language)
        model_used = None
    except Exception:
        explanation = get_static_message("error", target_language)
        model_used = None

    return {
        "query": request.query,
        "translated_query": search_query,
        "results": results,
        "explanation": explanation,
        "language": target_language,
        "model_used": model_used,
    }


@app.post("/translate-explanation")
def translate_explanation_endpoint(request: TranslateExplanationRequest, raw_request: Request):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="No text provided to translate.")
    if request.target_language not in ("en", "hi", "kn"):
        raise HTTPException(status_code=400, detail="Unsupported target language.")
    check_rate_limit(raw_request, language=request.target_language)

    try:
        translated = translate_explanation(request.text, request.target_language)
    except groq.RateLimitError:
        raise HTTPException(status_code=503, detail="Translation service is temporarily unavailable due to a usage limit. Please try again later.")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong translating this. Please try again.")

    return {"translation": translated, "language": request.target_language}


@app.post("/upload-pdf")
async def upload_pdf(raw_request: Request, file: UploadFile = File(...)):
    check_rate_limit(raw_request, language="en")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file appears to be empty.")

    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File is too large. Please upload a PDF under 20MB.")

    try:
        text = extract_text_from_pdf(file_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this PDF. It may be corrupted or password-protected.")

    if not text or len(text.strip()) < 20:
        return {
            "document_id": None,
            "filename": file.filename,
            "character_count": 0,
            "summary": "We couldn't extract any readable text from this document. It may be a scanned image without selectable text (try a text-based PDF instead), or the file may be corrupted.",
            "dates": [],
        }

    document_id = file.filename + "_" + str(len(text))
    document_store[document_id] = text

    try:
        summary = summarize_document(text)
    except groq.RateLimitError:
        summary = "Document uploaded successfully, but AI summarization is temporarily unavailable due to a service usage limit. You can still ask questions about the document below."
    except Exception:
        summary = "Document uploaded, but we couldn't generate a summary right now."

    try:
        dates = extract_dates_and_deadlines(text)
    except Exception:
        dates = []

    return {
        "document_id": document_id,
        "filename": file.filename,
        "character_count": len(text),
        "summary": summary,
        "dates": dates,
    }


@app.post("/ask-document")
def ask_document(request: DocumentQuestionRequest, raw_request: Request):
    check_rate_limit(raw_request, language="en")
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Please enter a question about the document.")

    text = document_store.get(request.document_id)
    if not text:
        raise HTTPException(status_code=404, detail="Document not found. Please upload it again.")

    try:
        answer = answer_question_about_document(text, request.question)
    except groq.RateLimitError:
        raise HTTPException(status_code=503, detail="AI question-answering is temporarily unavailable due to a service usage limit. Please try again later.")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong answering your question. Please try again.")

    return {"answer": answer}


@app.post("/define")
def define(request: DefineRequest, raw_request: Request):
    check_rate_limit(raw_request, language="en")
    if not request.term or not request.term.strip():
        raise HTTPException(status_code=400, detail="Please enter a term to look up.")

    try:
        definition = define_term(request.term)
    except groq.RateLimitError:
        raise HTTPException(status_code=503, detail="The dictionary service is temporarily unavailable due to a usage limit. Please try again later.")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong looking up this term. Please try again.")

    return {"term": request.term, "definition": definition}

class DraftRequest(BaseModel):
    document_type: str
    details: dict = {}


class CaseSimplifyRequest(BaseModel):
    case_text: str


class BNSLookupRequest(BaseModel):
    section_number: str
    language: str | None = "en"


@app.post("/draft-document")
def draft_document_endpoint(request: DraftRequest, raw_request: Request):
    check_rate_limit(raw_request, language="en")
    if request.document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown document type. Supported types: {list(DOCUMENT_TYPES.keys())}")

    try:
        document_text = draft_document(request.document_type, request.details)
    except groq.RateLimitError:
        raise HTTPException(status_code=503, detail="Document drafting service is temporarily unavailable due to a usage limit. Please try again later.")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong generating this document. Please try again.")

    return {"document_type": request.document_type, "document_text": document_text}


@app.get("/document-types")
def get_document_types():
    return {"document_types": DOCUMENT_TYPES}


@app.post("/simplify-case")
def simplify_case_endpoint(request: CaseSimplifyRequest, raw_request: Request):
    check_rate_limit(raw_request, language="en")
    if not request.case_text or not request.case_text.strip():
        raise HTTPException(status_code=400, detail="Please paste the case text you want simplified.")
    if len(request.case_text) > 20000:
        raise HTTPException(status_code=400, detail="That text is too long. Please paste a shorter excerpt (under 20,000 characters).")

    try:
        simplified = simplify_case(request.case_text)
    except groq.RateLimitError:
        raise HTTPException(status_code=503, detail="The case simplifier is temporarily unavailable due to a usage limit. Please try again later.")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong simplifying this case. Please try again.")

    return {"simplified_explanation": simplified}


@app.post("/bns-lookup")
def bns_lookup_endpoint(request: BNSLookupRequest, raw_request: Request):
    lang = (request.language or "en").lower().strip()
    if lang not in ("en", "hi", "kn"):
        lang = "en"
    check_rate_limit(raw_request, language=lang)

    sec = (request.section_number or "").strip()
    if not sec:
        if lang == "hi":
            err_msg = "कृपया एक बीएनएस (BNS) धारा संख्या दर्ज करें।"
        elif lang == "kn":
            err_msg = "ದಯವಿಟ್ಟು ಬಿಎನ್‌ಎಸ್ (BNS) ವಿಭಾಗ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ."
        else:
            err_msg = "Please enter a BNS section number."
        raise HTTPException(status_code=400, detail=err_msg)

    record = engine.lookup_section("Bharatiya Nyaya Sanhita", sec)
    if not record:
        if lang == "hi":
            not_found_msg = f"भारतीय न्याय संहिता की धारा {sec} हमारे डेटाबेस में नहीं मिली।"
        elif lang == "kn":
            not_found_msg = f"ಭಾರತೀಯ ನ್ಯಾಯ ಸಂಹಿತೆಯ ವಿಭಾಗ {sec} ನಮ್ಮ ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಕಂಡುಬಂದಿಲ್ಲ."
        else:
            not_found_msg = f"Section {sec} of the Bharatiya Nyaya Sanhita was not found in our database."
        raise HTTPException(status_code=404, detail=not_found_msg)

    try:
        explanation = explain_bns_section(record["section_title"], record["legal_text"], language=lang)
    except groq.RateLimitError:
        if lang == "hi":
            explanation = "सेवा उपयोग सीमा के कारण सरल भाषा में व्याख्या अस्थायी रूप से अनुपलब्ध है। मूल धारा नीचे दी गई है।"
        elif lang == "kn":
            explanation = "ಸೇವಾ ಬಳಕೆಯ ಮಿತಿಯಿಂದಾಗಿ ಸರಳ ಭಾಷೆಯ ವಿವರಣೆಯು ತಾತ್ಕಾಲಿಕವಾಗಿ ಲಭ್ಯವಿಲ್ಲ. ಮೂಲ ವಿಭಾಗವನ್ನು ಕೆಳಗೆ ನೀಡಲಾಗಿದೆ."
        else:
            explanation = "Plain-language explanation is temporarily unavailable due to a usage limit. The section text is shown below."
    except Exception:
        if lang == "hi":
            explanation = "हम अभी व्याख्या तैयार नहीं कर सके, लेकिन मूल धारा नीचे दी गई है।"
        elif lang == "kn":
            explanation = "ನಾವು ಇದೀಗ ವಿವರಣೆಯನ್ನು ರಚಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ, ಆದರೆ ಮೂಲ ವಿಭಾಗವನ್ನು ಕೆಳಗೆ ನೀಡಲಾಗಿದೆ."
        else:
            explanation = "Could not generate an explanation right now, but the section text is shown below."

    return {
        "section_number": record["section_number"],
        "section_title": record["section_title"],
        "legal_text": record["legal_text"],
        "explanation": explanation,
    }






















