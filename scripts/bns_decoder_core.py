import os
import json
import threading
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "cache"))
BNS_CACHE_PATH = os.path.join(CACHE_DIR, "bns_decoder_cache.json")
_cache_lock = threading.Lock()

BNS_DECODER_PROMPT_VERSION = "v3"

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
}


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _load_cache():
    if not os.path.exists(BNS_CACHE_PATH):
        return {}
    try:
        with open(BNS_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(data):
    _ensure_cache_dir()
    tmp_path = BNS_CACHE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, BNS_CACHE_PATH)


BNS_DECODER_SYSTEM_PROMPT = """You are a legal explainer for the Bharatiya Nyaya Sanhita (BNS), India's criminal code. You explain a specific BNS section in plain, simple language for ordinary people who are not lawyers.

STRICT RULES:
- Only use the section text provided. Do not invent details not present in it.
- Explain what the section means in plain language: what conduct it covers, and what the punishment or consequence is if stated.
- Restate each sub-section's condition and punishment faithfully, keeping who the offender is and who is protected exactly as in the text (don't swap roles).
- Mention an offender's duty to protect someone ONLY if the section text itself explicitly says the offender was bound (by law or contract) to protect that interest; in such cases, say explicitly that it is the offender who had that duty (e.g. an agent or trustee cheating their own client). Never add or assume a duty that the text does not explicitly state.
- Cover every punishment tier, including the most common case.
- Don't add meta-sentences like "That's all the section covers" or "It does not give advice".
- Keep it concise - a few short paragraphs, not a long essay.
- Do not give legal advice or predict outcomes for any specific situation.
- IMPORTANT: Respond entirely in the language specified in the user request (English, Hindi, or Kannada). Even though the legal section text provided to you will be in English, provide the explanation in the specified language.
"""


def explain_bns_section(section_title, section_text, language="en"):
    lang_code = (language or "en").lower().strip()
    target_language = LANGUAGE_NAMES.get(lang_code, "English")

    cache_key = None
    if os.environ.get("NYAAYA_DISABLE_CACHE") != "1":
        cache_key = json.dumps([BNS_DECODER_PROMPT_VERSION, lang_code, section_title, section_text], ensure_ascii=False)
        with _cache_lock:
            cache = _load_cache()
            if cache_key in cache:
                return cache[cache_key]

    user_prompt = (
        f"Section title: {section_title}\n\n"
        f"Section text: {section_text}\n\n"
        f"Explain this BNS section in plain language. "
        f"IMPORTANT: Respond entirely in {target_language}."
    )

    max_tokens = 800 if lang_code == "en" else 1800

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": BNS_DECODER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=max_tokens,
    )

    result = response.choices[0].message.content

    if cache_key and os.environ.get("NYAAYA_DISABLE_CACHE") != "1":
        with _cache_lock:
            cache = _load_cache()
            cache[cache_key] = result
            _save_cache(cache)

    return result
