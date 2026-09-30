import os
import json
import time
import threading
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "cache"))
DICTIONARY_CACHE_PATH = os.path.join(CACHE_DIR, "dictionary_cache.json")
_cache_lock = threading.Lock()

DICTIONARY_PROMPT_VERSION = "v3"

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
}

# Small verified mapping of terms to current BNSS section and earlier CrPC section.
# Verified against the statutory text in Legal_Knowledge_Base_combined.xlsx.
VERIFIED_SECTIONS = {
    "anticipatory bail": ("BNSS s. 482", "CrPC s. 438"),
    "fir": ("BNSS s. 173", "CrPC s. 154"),
    "first information report": ("BNSS s. 173", "CrPC s. 154"),
    "first information report (fir)": ("BNSS s. 173", "CrPC s. 154"),
    "arrest without warrant": ("BNSS s. 35", "CrPC s. 41"),
    "police custody": ("BNSS s. 187", "CrPC s. 167"),
    "remand": ("BNSS s. 187", "CrPC s. 167"),
    "police custody/remand": ("BNSS s. 187", "CrPC s. 167"),
    "cognizable offence": ("BNSS s. 2(1)(g)", "CrPC s. 2(c)"),
    "cognizable offense": ("BNSS s. 2(1)(g)", "CrPC s. 2(c)"),
}


def get_verified_citation(term: str):
    if not term:
        return None
    norm = term.strip().lower()
    return VERIFIED_SECTIONS.get(norm)


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _load_cache():
    if not os.path.exists(DICTIONARY_CACHE_PATH):
        return {}
    try:
        with open(DICTIONARY_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(data):
    _ensure_cache_dir()
    tmp_path = DICTIONARY_CACHE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, DICTIONARY_CACHE_PATH)


DICTIONARY_SYSTEM_PROMPT = """You are a legal dictionary assistant for Indian law. You explain legal terms in simple, plain language for ordinary people who are not lawyers.

STRICT RULES:
- Give a clear, short definition (2-4 sentences) in plain everyday language, no legal jargon.
- Always refer to the CURRENT Indian criminal laws that came into force on 1 July 2024:
  * Bharatiya Nyaya Sanhita, 2023 (BNS) - replaced the Indian Penal Code (IPC)
  * Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) - replaced the Code of Criminal Procedure (CrPC)
  * Bharatiya Sakshya Adhiniyam, 2023 (BSA) - replaced the Indian Evidence Act
- SECTION CITATION RULE:
  * You may cite section numbers ONLY if an explicit verified citation is provided in the prompt. When provided, cite the new section and mention the old one in brackets (e.g. "(BNSS s. 482, earlier CrPC s. 438)").
  * For ANY other term where no verified citation is provided, you MUST NOT include ANY section numbers. Instead, name the governing law (e.g. "under the Bharatiya Nagarik Suraksha Sanhita (BNSS)") without any section number. Never guess or invent section numbers.
- If the term is not a real legal term, say so honestly rather than making up a definition.
- Do not give legal advice - only explain what the term means.
- For unusual legal terms, keep the English term in brackets when unsure (e.g. "धोखाधड़ी (cheating)").
"""


def define_term(term, language="en"):
    lang_code = (language or "en").lower().strip()
    if lang_code not in ("en", "hi", "kn"):
        lang_code = "en"
    target_language = LANGUAGE_NAMES.get(lang_code, "English")

    norm_term = (term or "").strip().lower()
    cache_key = None
    if os.environ.get("NYAAYA_DISABLE_CACHE") != "1":
        cache_key = json.dumps([DICTIONARY_PROMPT_VERSION, lang_code, norm_term], ensure_ascii=False)
        with _cache_lock:
            cache = _load_cache()
            if cache_key in cache and cache[cache_key] and cache[cache_key].strip():
                return cache[cache_key]

    citation = get_verified_citation(term)
    if citation:
        bnss_sec, crpc_sec = citation
        cit_msg = f"VERIFIED CITATION: Include this exact citation in your definition: ({bnss_sec}, earlier {crpc_sec})."
    else:
        cit_msg = "NO VERIFIED CITATION: Do NOT include ANY section numbers. Name the governing law without any section number."

    user_prompt = (
        f"Define the legal term '{term}' in plain language.\n\n"
        f"{cit_msg}\n\n"
        f"IMPORTANT: Respond entirely in {target_language}.\n"
    )
    if lang_code != "en":
        user_prompt += (
            f"Translate the term to its proper legal term in {target_language} with the English term in brackets (e.g. 'जमानत (bail)' in Hindi, 'ಜಾಮೀನು (bail)' in Kannada).\n"
            "For unusual legal terms, keep the English term in brackets when unsure (e.g. 'धोखाधड़ी (cheating)').\n"
            "Remember: If no verified citation is provided above, do NOT mention ANY section numbers."
        )

    max_tokens = 600 if lang_code == "en" else 2000

    result = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": DICTIONARY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=max_tokens,
                reasoning_effort="low",
            )
            content = response.choices[0].message.content
            if content and content.strip():
                result = content.strip()
                break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1)

    if not result:
        result = "Could not find a definition for this term."

    if cache_key and os.environ.get("NYAAYA_DISABLE_CACHE") != "1" and result and result.strip():
        with _cache_lock:
            cache = _load_cache()
            cache[cache_key] = result
            _save_cache(cache)

    return result
