import os
import re
import time
import json
import string
import threading
import groq
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "cache"))
EXPLANATION_CACHE_PATH = os.path.join(CACHE_DIR, "explanation_cache.json")
TRANSLATION_CACHE_PATH = os.path.join(CACHE_DIR, "translation_cache.json")

_cache_lock = threading.Lock()


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _load_json_file(file_path):
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json_file(file_path, data):
    _ensure_cache_dir()
    tmp_path = file_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, file_path)


PUNCT_TO_STRIP = string.punctuation + "“”‘’।॥"


def normalize_text(text: str) -> str:
    """Normalize query text for caching: lowercase, collapse spaces, strip punctuation at ends."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    text = text.strip(PUNCT_TO_STRIP).strip()
    return text


# Bump the version whenever the prompt changes to invalidate old cache entries.
EXPLANATION_PROMPT_VERSION = "v4"


def make_explanation_cache_key(query: str, language: str, search_results: list, model: str = "openai/gpt-oss-120b") -> str:
    norm_q = normalize_text(query)
    lang = (language or "en").lower().strip()
    sec_list = [
        [str(r.get("act_name") or "").strip(), str(r.get("section_number") or "").strip()]
        for r in (search_results or [])
    ]
    return json.dumps([EXPLANATION_PROMPT_VERSION, model, norm_q, lang, sec_list], ensure_ascii=False)


def get_cached_explanation(query: str, language: str, search_results: list, model: str = "openai/gpt-oss-120b"):
    if os.environ.get("NYAAYA_DISABLE_CACHE") == "1":
        return None
    key = make_explanation_cache_key(query, language, search_results, model=model)
    with _cache_lock:
        data = _load_json_file(EXPLANATION_CACHE_PATH)
        hit = data.get(key)
        if hit is not None:
            return hit
        # If looking up default primary model, check if backup model answered it
        if model == "openai/gpt-oss-120b":
            backup_key = make_explanation_cache_key(query, language, search_results, model="openai/gpt-oss-20b")
            return data.get(backup_key)
        return None


def save_cached_explanation(query: str, language: str, search_results: list, explanation: str, model_used: str):
    if os.environ.get("NYAAYA_DISABLE_CACHE") == "1":
        return
    model = model_used or "openai/gpt-oss-120b"
    key = make_explanation_cache_key(query, language, search_results, model=model)
    with _cache_lock:
        data = _load_json_file(EXPLANATION_CACHE_PATH)
        data[key] = {
            "explanation": explanation,
            "model_used": model,
        }
        _save_json_file(EXPLANATION_CACHE_PATH, data)


def make_translation_cache_key(query: str, model: str = "openai/gpt-oss-120b", reasoning_effort: str = None) -> str:
    norm_q = normalize_text(query)
    if reasoning_effort is None:
        reasoning_effort = os.environ.get("TRANSLATION_REASONING", "low")
    reasoning_str = (reasoning_effort or "none").lower().strip()
    return json.dumps([model, reasoning_str, norm_q], ensure_ascii=False)


def get_cached_translation(query: str, model: str = "openai/gpt-oss-120b", reasoning_effort: str = None):
    if os.environ.get("NYAAYA_DISABLE_CACHE") == "1":
        return None
    key = make_translation_cache_key(query, model=model, reasoning_effort=reasoning_effort)
    with _cache_lock:
        data = _load_json_file(TRANSLATION_CACHE_PATH)
        return data.get(key)


def save_cached_translation(query: str, translation: str, model: str = "openai/gpt-oss-120b", reasoning_effort: str = None):
    if os.environ.get("NYAAYA_DISABLE_CACHE") == "1":
        return
    key = make_translation_cache_key(query, model=model, reasoning_effort=reasoning_effort)
    with _cache_lock:
        data = _load_json_file(TRANSLATION_CACHE_PATH)
        data[key] = translation
        _save_json_file(TRANSLATION_CACHE_PATH, data)


def _is_tokens_per_day_error(e: Exception) -> bool:
    """Check if an exception indicates a tokens-per-day (TPD) rate limit."""
    msg = str(e).lower()
    body_str = ""
    if hasattr(e, "body"):
        try:
            body_str = str(e.body).lower()
        except Exception:
            pass
    combined = f"{msg} {body_str}"
    tpd_indicators = (
        "tokens per day",
        "tokens-per-day",
        "tokens_per_day",
        "tpd",
        "daily limit",
        "daily-limit",
        "daily_limit",
        "day limit",
    )
    return any(ind in combined for ind in tpd_indicators)

SYSTEM_PROMPT = """You are a legal information assistant for Indian law. You explain laws in plain, simple language for ordinary people who are not lawyers.

STRICT RULES:
- Only use the legal sections provided to you below. Do not invent or assume any Act, Section, case, citation, or deadline that is not explicitly given.
- Only explain sections that directly apply to the user's situation. Omit any section that does not apply. Never write "this does not apply, but...".
- For procedural sections, state only what the section's text literally covers. If it applies only to specific other sections (e.g. "offence under section 67", "sections 81 to 84"), include it ONLY if the user's situation falls under those sections; otherwise omit it.
- Never speculate about suicide, self-harm or death of the user; omit such sections unless the user mentioned them.
- If the provided sections do not fully answer the question, say so clearly instead of guessing.
- Write in plain, everyday language, not legal jargon.
- Present the relevant sections in a markdown table with exactly these three columns, in this exact order, using these exact headers: "Section" | "What it says" | "What it means for you". Do not add, remove, rename, or reorder columns, and do not use any other table shape.
- The "What it means for you" column is mandatory and must never be left blank, empty, or filled with just a dash or "N/A". Every row must contain a specific sentence connecting that section to the person's situation.
- Do not give definitive legal advice or tell the person they will definitely win or lose - explain the law, not predict outcomes.
- Before writing each row, check: does the section's own text actually describe the user's specific situation (the same kind of payment, act, person or problem)? If not, OMIT that section entirely, even if it is about a related topic. It is better to show one relevant section, or none, than several stretched ones. If you omit every section, make the very first line of your answer exactly NOT_COVERED (in English capitals, even in Hindi or Kannada answers), then on the next line say, in the user's language, that none of the sections found directly covers this situation, and then give only general next steps.
- Only say a section gives the user a right or remedy if its text clearly covers the user's situation. Never reinterpret a section to fit (e.g. a section about a tenant depositing rent with the Controller is not a way to get a security deposit back). If no provided section clearly gives a remedy, say so plainly.
- Mention a time limit only if the section's text states it, and say exactly what the period runs from. Do not imply it fits the user's case unless it clearly does.
- If a section offers alternative remedies (e.g. withdraw and get a refund OR stay and get interest), present them as separate options. Never merge them.
- If the question could describe either side (e.g. "my cheque bounced" could mean the person issued it or received it), briefly explain both perspectives.
- End with a short "What you can do next" suggestion, grounded only in what the law sections say. If no section clearly applies, suggest sending a written notice or consulting free legal aid, without naming any Act or Section that was not provided.
- Add "emergency 112; women's helpline 181" (translated in hi/kn, numbers unchanged) ONLY when the user describes physical violence, sexual abuse, a threat to someone's safety, or immediate danger. Never add it for money, rent, deposit, property, consumer, banking, employment, document or other non-safety questions.
- In the "What it says" column, summarise the section in 1-2 short plain sentences; never paste the full legal text.
- Do not say where or with whom to file a case or complaint (police, court, magistrate, forum) unless the provided section text says so; otherwise suggest consulting free legal aid about where to file.
- Never quote or translate the section text word by word, and never use quotation marks in the "What it says" column. Write your own short summary with numbers as digits (e.g. write 30, never thirty, third or 3), not as words.
- Refer to the provided sections as "the sections found", never as sections the user listed or gave.
- If a section's text refers to another Act that is not among the provided sections, do not tell the user to use or invoke that other Act; say only that the section refers to it, and that older laws may have been replaced, so the user should check with free legal aid.
- Copy every number, time limit, amount and age EXACTLY from the section text (e.g. thirty days = 30 days, never 3). Write numbers as digits. Double-check them before answering.
- In Hindi or Kannada answers, write in that language; for a legal term, use the common Hindi/Kannada word and add the English term in brackets the first time only, e.g. the Hindi or Kannada word for offence followed by (offence). Do not leave whole English phrases untranslated.
- IMPORTANT: Respond entirely in the language specified in the user request (English, Hindi, or Kannada). Even though the legal section text provided to you will be in English, provide the explanation and translate the three table headers into the specified language, maintaining the exact same three-column structure and ensuring the third column is never blank.
"""

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
}

SCRIPT_RANGES = {
    # Bare ranges (no enclosing brackets) built via chr() rather than
    # backslash-u literal escapes in this source file, to sidestep an
    # editor/tooling issue that silently collapses such escapes into
    # their literal characters when this file gets written.
    "hi": chr(0x0900) + "-" + chr(0x097F),
    "kn": chr(0x0C80) + "-" + chr(0x0CFF),
}


def detect_language(text):
    """Detect which of English/Hindi/Kannada a piece of text is written in,
    using Unicode script ranges - cheap and reliable, no API call needed."""
    if re.search("[" + SCRIPT_RANGES["kn"] + "]", text):
        return "kn"
    if re.search("[" + SCRIPT_RANGES["hi"] + "]", text):
        return "hi"
    return "en"


def _looks_translated(text, target_language_code, original_length):
    """Sanity-check a translation before trusting it. The translation model
    occasionally returns a degenerate completion for hi/kn targets - echoing
    back a chunk of the original English (sometimes truncated mid-sentence)
    instead of translating it. Neither the API call nor the response itself
    raises an error in that case, so this is the only thing that catches it.

    This is a whole-text ratio check, so it cannot catch a single wrong-script
    word dropped into an otherwise-correct translation (e.g. a stray Greek
    word) - see find_stray_script_words() for that."""
    if not text:
        return False
    if target_language_code not in SCRIPT_RANGES:
        return True
    if len(text) < original_length * 0.5:
        return False
    script_chars = len(re.findall("[" + SCRIPT_RANGES[target_language_code] + "]", text))
    return script_chars >= len(text) * 0.2


def find_stray_script_words(text, target_language_code):
    """Find any run of characters that isn't in the target script, plain
    ASCII (English Act names, section numbers, digits, markdown/punctuation),
    or general punctuation/whitespace. Whitelisting the allowed scripts,
    rather than blacklisting known "bad" ones (Greek, Cyrillic, etc.), means
    a hallucinated word from ANY unrelated script is caught, not just the
    ones we thought to list.

    Unlike _looks_translated's whole-text ratio, this flags a single stray
    word even inside an otherwise fully and correctly translated text -
    the class of defect a ratio check is structurally blind to."""
    target_range = SCRIPT_RANGES.get(target_language_code)
    if not target_range:
        return []
    basic_ascii = chr(0x0000) + "-" + chr(0x007F)
    general_punctuation = chr(0x2000) + "-" + chr(0x206F)
    whitespace = "".join(chr(c) for c in (0x20, 0x09, 0x0A, 0x0D, 0x0C, 0x0B))
    allowed = target_range + basic_ascii + general_punctuation + whitespace
    return re.findall("[^" + allowed + "]+", text)

def translate_to_english(query, return_usage=False):
    model = "openai/gpt-oss-120b"
    reasoning_effort = os.environ.get("TRANSLATION_REASONING", "low")

    cached = get_cached_translation(query, model=model, reasoning_effort=reasoning_effort)
    if cached is not None:
        if return_usage:
            return cached, None
        return cached

    kwargs = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You translate short legal questions into English. "
                    "If the text is already in English, return it unchanged. "
                    "Return ONLY the translated text, nothing else - no explanations, no quotes."
                ),
            },
            {"role": "user", "content": query},
        ],
        "temperature": 0,
        "max_tokens": 500,
    }
    if reasoning_effort and reasoning_effort.lower() not in ("none", "null", "false", "off", "0"):
        kwargs["reasoning_effort"] = reasoning_effort

    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("Translation model returned empty response")
    translated_text = content.strip()
    save_cached_translation(query, translated_text, model=model, reasoning_effort=reasoning_effort)
    if return_usage:
        return translated_text, response.usage
    return translated_text


def translate_explanation(explanation_text, target_language_code):
    """Translate an already-generated explanation into a target language,
    preserving formatting and legal terms. Used for the language toggle -
    does NOT re-run search or re-generate the legal content."""
    target_language = LANGUAGE_NAMES.get(target_language_code)
    if not target_language:
        return explanation_text

    messages = [
        {
            "role": "system",
            "content": (
                f"You translate legal explanations into {target_language}. "
                "Preserve all formatting (markdown tables, bullet points, headers) exactly as given. "
                "Preserve all Act names, Section numbers, and legal terms accurately. "
                "Translate the ENTIRE text, including any bold titles or headings - do not leave "
                "any part of it in the original language. "
                "Return ONLY the translated text, nothing else - no preamble, no notes."
            ),
        },
        {"role": "user", "content": explanation_text},
    ]

    # Non-English scripts (Hindi/Kannada) routinely need more tokens than the
    # English source they're translating, since Indic scripts tokenize less
    # efficiently. 3000 was tuned against English-sized output and was
    # silently truncating hi/kn translations mid-sentence.
    max_tokens = 3000 if target_language_code == "en" else 6000

    max_retries = 3
    best_result = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                temperature=0,
                max_tokens=max_tokens,
            )
        except groq.RateLimitError:
            raise
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise

        choice = response.choices[0]
        result = choice.message.content.strip()
        # finish_reason == "length" means the completion was cut off by the
        # token limit, not that the model finished - a hard truncation signal
        # that the script/length heuristic below can miss (a 70%-translated
        # response that stops mid-word still "looks" mostly translated).
        truncated = choice.finish_reason == "length"
        if truncated or not _looks_translated(result, target_language_code, len(explanation_text)):
            continue

        stray_words = find_stray_script_words(result, target_language_code)
        if not stray_words:
            return result
        # A stray wrong-script word (e.g. one hallucinated Greek word) in an
        # otherwise-correct translation is a much smaller defect than
        # truncation or a wholly-untranslated response. Retry to reduce the
        # odds of hitting it again, but if it persists, ship the best attempt
        # rather than blocking a 99%-correct translation entirely.
        best_result = result

    if best_result is not None:
        return best_result

    raise ValueError(
        f"Translation into {target_language} did not produce valid translated text after {max_retries} attempts."
    )


def generate_explanation(original_query, search_results, language="en", return_model=False):
    if not search_results:
        msg = "No relevant legal sections were found for this query."
        return (msg, None) if return_model else msg

    evidence = ""
    for r in search_results:
        evidence += (
            f"\n---\nAct: {r['act_name']}\n"
            f"Section: {r['section_number']}\n"
            f"Title: {r['section_title']}\n"
            f"Text: {r['legal_text']}\n"
        )

    target_language = LANGUAGE_NAMES.get(language or "en", "English")
    user_prompt = (
        f"User's question: {original_query}\n\n"
        f"Relevant legal sections found:\n{evidence}\n\n"
        f"Explain what these sections mean for the user's situation, in plain language. "
        f"IMPORTANT: Respond entirely in {target_language}."
    )

    max_tokens = 3000 if (language or "en") == "en" else 5000
    max_retries = 3

    use_backup = False
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return (content, "openai/gpt-oss-120b") if return_model else content
        except groq.RateLimitError as e:
            if _is_tokens_per_day_error(e):
                use_backup = True
                break
            raise
        except Exception as e:
            if _is_tokens_per_day_error(e):
                use_backup = True
                break
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise

    if use_backup:
        # Retry once with openai/gpt-oss-20b
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=max_tokens,
            reasoning_effort="low",
        )
        content = response.choices[0].message.content
        return (content, "openai/gpt-oss-20b") if return_model else content

import re


def verify_citations(explanation_text, search_results):
    """Check whether every 'Section X' mentioned in the AI-generated explanation
    was actually among the retrieved search results. This is a defense-in-depth
    check against the LLM hallucinating or misremembering a section number that
    wasn't actually retrieved. Returns (is_valid, list_of_unverified_section_numbers)."""
    retrieved_sections = set(str(r["section_number"]) for r in search_results)
    mentioned = re.findall(r"[Ss]ection\s+(\d+[A-Za-z]?)", explanation_text)
    unverified = [s for s in mentioned if s not in retrieved_sections]
    return (len(unverified) == 0, unverified)
def rewrite_query_for_search(query):
    """Rewrite an everyday-language legal question into likely legal terminology,
    to improve search matching against statutory text. Falls back to the original
    query on any failure, and combines both for safety (search tries the rewritten
    version first, caller can fall back to original if needed)."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You rewrite everyday legal questions into the formal legal "
                            "terminology an Indian statute would actually use, to improve "
                            "search matching. For example: 'seriously injuring someone' -> "
                            "'grievous hurt'. 'reckless driving' -> 'rash driving'. "
                            "'getting property back from someone occupying it' -> 'recovery "
                            "of possession'. 'sending a court notice' -> 'service of summons'. "
                            "Keep the rewritten question short and natural, just replacing "
                            "vague everyday words with the specific legal terms they map to. "
                            "Use current Indian law names (Bharatiya Nyaya Sanhita/BNS, "
                            "Bharatiya Nagarik Suraksha Sanhita/BNSS), never the old repealed "
                            "IPC or CrPC. Return ONLY the rewritten question, nothing else - "
                            "no explanation, no quotes."
                        ),
                    },
                    {"role": "user", "content": query},
                ],
                temperature=0.2,
                max_tokens=800,
            )
            return response.choices[0].message.content.strip()
        except groq.RateLimitError:
            raise
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return query


STATIC_SYSTEM_MESSAGES = {
    "no_results": {
        "en": "No relevant legal sections were found for this query. Try rephrasing with more specific details.",
        "hi": "इस सवाल से जुड़ी कोई कानूनी धारा नहीं मिली। थोड़ा और विस्तार से पूछकर देखें।",
        "kn": "ಈ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ಯಾವುದೇ ಕಾನೂನು ವಿಭಾಗ ಸಿಗಲಿಲ್ಲ. ಇನ್ನಷ್ಟು ವಿವರವಾಗಿ ಮತ್ತೆ ಕೇಳಿ ನೋಡಿ.",
    },
    "low_confidence_prefix": {
        "en": (
            "I am not confident enough about which section applies to your question to give a definite answer. "
            "Here are the closest matching sections, grouped by Act - please check which one fits your situation, "
            "or try rephrasing your question with more specific details:"
        ),
        "hi": (
            "हमें पक्का पता नहीं कि आपके सवाल पर कौन-सी धारा लागू होती है। "
            "नीचे सबसे मिलती-जुलती धाराएं कानून के हिसाब से दी गई हैं — "
            "देखें कौन-सी आपकी स्थिति से मेल खाती है, या थोड़ा और विस्तार से पूछें:"
        ),
        "kn": (
            "ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಯಾವ ವಿಭಾಗ ಅನ್ವಯಿಸುತ್ತದೆ ಎಂದು ನಮಗೆ ಖಚಿತವಿಲ್ಲ. "
            "ಹತ್ತಿರದ ವಿಭಾಗಗಳನ್ನು ಕಾಯ್ದೆಯ ಪ್ರಕಾರ ಕೆಳಗೆ ನೀಡಲಾಗಿದೆ — "
            "ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿಗೆ ಯಾವುದು ಹೊಂದುತ್ತದೆ ನೋಡಿ, ಅಥವಾ ಇನ್ನಷ್ಟು ವಿವರವಾಗಿ ಕೇಳಿ:"
        ),
    },
    "section_label": {
        "en": "Section",
        "hi": "धारा",
        "kn": "ವಿಭಾಗ",
    },
    "rate_limit": {
        "en": "Plain-language explanation is temporarily unavailable due to a service usage limit. Here are the relevant legal sections we found - please review them directly below.",
        "hi": "अभी आसान भाषा में जवाब नहीं बन पा रहा। हमें जो कानूनी धाराएं मिलीं, वे नीचे दी गई हैं।",
        "kn": "ಈಗ ಸರಳ ವಿವರಣೆ ಸಿಗುತ್ತಿಲ್ಲ. ನಾವು ಕಂಡುಕೊಂಡ ಕಾನೂನು ವಿಭಾಗಗಳು ಕೆಳಗೆ ಇವೆ.",
    },
    "error": {
        "en": "We couldn't generate an explanation right now, but here are the relevant legal sections we found below.",
        "hi": "अभी जवाब तैयार नहीं हो सका, लेकिन हमें जो कानूनी धाराएं मिलीं, वे नीचे दी गई हैं।",
        "kn": "ನಾವು ಇದೀಗ ವಿವರಣೆಯನ್ನು ರಚಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ, ಆದರೆ ನಾವು ಕಂಡುಕೊಂಡ ಸಂಬಂಧಿತ ಕಾನೂನು ವಿಭಾಗಗಳನ್ನು ಕೆಳಗೆ ನೀಡಲಾಗಿದೆ.",
    },
}


def get_static_message(key, language="en"):
    msgs = STATIC_SYSTEM_MESSAGES.get(key, {})
    return msgs.get(language) or msgs.get("en", "")

