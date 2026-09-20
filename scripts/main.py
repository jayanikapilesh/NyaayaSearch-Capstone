from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search_core import SearchEngine
from rag_core import generate_explanation, translate_to_english, translate_explanation, detect_language
from citations_core import find_related_cases
from pdf_core import extract_text_from_pdf, answer_question_about_document, summarize_document, extract_dates_and_deadlines
from dictionary_core import define_term
from drafter_core import draft_document, DOCUMENT_TYPES
import groq

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


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


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


@app.get("/")
def root():
    return {"status": "NyaayaSearch API is running"}


@app.post("/search")
def search(request: SearchRequest):
    validate_query(request.query)
    try:
        results = engine.search(request.query, top_k=request.top_k)
        results = attach_related_cases(results)
        return {"query": request.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search failed unexpectedly. Please try again.")


@app.post("/explain")
def explain(request: SearchRequest):
    validate_query(request.query)

    try:
        search_query = translate_to_english(request.query)
    except groq.RateLimitError:
        raise HTTPException(
            status_code=503,
            detail="Our AI explanation service has hit its usage limit for now. You can still search for relevant sections, but plain-language explanations are temporarily unavailable. Please try again later."
        )
    except Exception:
        search_query = request.query  # fall back to using the original query untranslated

    try:
        results = engine.search(search_query, top_k=request.top_k)
        results = attach_related_cases(results)
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed unexpectedly. Please try again.")

    detected_language = detect_language(request.query)

    if not results:
        return {
            "query": request.query,
            "translated_query": search_query,
            "results": [],
            "explanation": "No relevant legal sections were found for this query. Try rephrasing with more specific details.",
            "language": detected_language,
        }

    try:
        explanation = generate_explanation(request.query, results)
    except groq.RateLimitError:
        explanation = "Plain-language explanation is temporarily unavailable due to a service usage limit. Here are the relevant legal sections we found - please review them directly below."
    except Exception:
        explanation = "We couldn't generate an explanation right now, but here are the relevant legal sections we found below."

    return {
        "query": request.query,
        "translated_query": search_query,
        "results": results,
        "explanation": explanation,
        "language": detected_language,
    }


@app.post("/translate-explanation")
def translate_explanation_endpoint(request: TranslateExplanationRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="No text provided to translate.")
    if request.target_language not in ("en", "hi", "kn"):
        raise HTTPException(status_code=400, detail="Unsupported target language.")

    try:
        translated = translate_explanation(request.text, request.target_language)
    except groq.RateLimitError:
        raise HTTPException(status_code=503, detail="Translation service is temporarily unavailable due to a usage limit. Please try again later.")
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong translating this. Please try again.")

    return {"translation": translated, "language": request.target_language}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
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
def ask_document(request: DocumentQuestionRequest):
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
def define(request: DefineRequest):
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


@app.post("/draft-document")
def draft_document_endpoint(request: DraftRequest):
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
