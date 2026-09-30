import os
import json
import csv
import re
import hashlib
import threading
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# In-memory cache only (private document content and case simplifications
# are never written to disk on the server).
_memory_cache = {}
_cache_lock = threading.Lock()

CASE_SIMPLIFIER_PROMPT_VERSION = "v5"

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
}

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
IPC_MAPPING_PATH = os.path.join(DATA_DIR, "ipc_bns_mapping.csv")


def _load_ipc_bns_mapping():
    mapping = {}
    if not os.path.exists(IPC_MAPPING_PATH):
        return mapping
    try:
        with open(IPC_MAPPING_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ipc_sec = str(row.get("ipc_section") or "").strip().lower()
                if not ipc_sec or ipc_sec == "n/a":
                    continue
                bns_sec = str(row.get("bns_section") or "").strip()
                bns_base = str(row.get("bns_base_section") or "").strip()
                if bns_sec.lower() in ("deleted", "n/a", ""):
                    continue
                # For IPC 420, statutory / standard equivalent is BNS 318
                if ipc_sec == "420":
                    mapping[ipc_sec] = "318"
                elif bns_sec:
                    mapping[ipc_sec] = bns_sec
                elif bns_base:
                    mapping[ipc_sec] = bns_base
    except Exception:
        pass
    return mapping


IPC_TO_BNS = _load_ipc_bns_mapping()


def extract_ipc_sections(text: str) -> list[str]:
    """Extract ONLY sections explicitly cited as IPC / Indian Penal Code from the text.
    Reuses patterns consistent with search_core.py, ensuring sections of other laws
    (such as CrPC, Evidence Act, etc.) are never misclassified as IPC sections.
    """
    if not text:
        return []
    text_clean = re.sub(r"\s+", " ", text)
    found = []

    def _is_ipc_sec(s: str) -> bool:
        if s in IPC_TO_BNS:
            return True
        m = re.match(r"^(\d+)", s)
        if m:
            val = int(m.group(1))
            return 1 <= val <= 511
        return False

    # Pattern 1: Clauses ending with IPC / Indian Penal Code, e.g.
    # 'Section 420 read with Section 34 of the Indian Penal Code (IPC)'
    clause_pat = re.compile(
        r"\b(?:sections?|sec\.?|s\.?)\s+([0-9a-zA-Z\s,/readwithand&–-]+?)\s*(?:of\s+the\s+)?(?:indian\s+penal\s+code|\bipc\b)",
        re.I,
    )
    for m in clause_pat.finditer(text_clean):
        sub = m.group(1)
        # Avoid capturing sections belonging to other laws mentioned earlier in the sentence
        parts = re.split(
            r"\b(?:code\s+of\s+criminal\s+procedure|cr\.?p\.?c\.?|evidence\s+act|contract\s+act)\b",
            sub,
            flags=re.I,
        )
        last_part = parts[-1]
        nums = re.findall(r"\b(\d+[a-z]*)\b", last_part.lower())
        for n in nums:
            if n not in ["and", "read", "with", "section", "sections", "sec", "s"] and _is_ipc_sec(n) and n not in found:
                found.append(n)

    # Pattern 2: 'IPC [section] 420' or 'IPC 420'
    for m in re.finditer(r"\bipc\s*(?:sections?|sec\.?|s\.?)?\s*(\d+[a-z]*)\b", text_clean, re.I):
        sec = m.group(1).lower()
        if _is_ipc_sec(sec) and sec not in found:
            found.append(sec)

    # Pattern 3: '420 IPC'
    for m in re.finditer(r"\b(\d+[a-z]*)\s*(?:\([a-z0-9\s]+\)\s*)?ipc\b", text_clean, re.I):
        sec = m.group(1).lower()
        if _is_ipc_sec(sec) and sec not in found:
            found.append(sec)

    return found


def extract_law_references(text: str) -> list[dict]:
    """Extract a list of law references from text built in code (not the AI).
    Only IPC sections found in data/ipc_bns_mapping.csv get a 'now' value; never guess one.
    """
    sections = extract_ipc_sections(text)
    refs = []
    for sec in sections:
        item = {"cited": f"IPC {sec.upper()}"}
        if sec in IPC_TO_BNS and IPC_TO_BNS[sec]:
            item["now"] = f"BNS {IPC_TO_BNS[sec]}"
        refs.append(item)
    return refs


CASE_SIMPLIFIER_SYSTEM_PROMPT = """You are a legal case simplifier for Indian law. You take court judgments, orders, or legal case text and explain them in plain, simple language for ordinary people who are not lawyers.

STRICT RULES:
- Only use information explicitly present in the text provided. Do not invent facts, parties, dates, or outcomes not stated in the text.
- If the text is incomplete or unclear, say so honestly rather than guessing.
- Structure your explanation with these sections, using markdown headings:
  - "What happened" - a plain-language summary of the situation/dispute
  - "What the court decided" - the outcome/ruling, in plain language
  - "Why it matters" - what this means in practical terms, if that's clear from the text
- Avoid legal jargon; when a legal term is unavoidable, briefly explain it in plain words.
- Do not give legal advice or predict how this case would apply to the reader's own situation.
- Keep the explanation clear and concise, not a word-for-word restatement of the text.
- Use the offence's legal name as written or implied by the section (IPC 420 = cheating, not "fraud").
- SECTION CONVERSION RULE:
  * Mention BNS equivalents ONLY for sections explicitly given in the provided list.
  * For any section NOT in the explicit IPC->BNS list (e.g. CrPC, Evidence Act), refer to it exactly as written and say nothing about equivalents. Never write "no BNS equivalent" or anything similar.
  * Never convert sections of any other law and never guess an equivalent.
"""


def simplify_case(case_text, language="en"):
    if not case_text or not case_text.strip():
        return {
            "simplified_explanation": "No case text was provided to simplify.",
            "law_references": [],
        }

    lang_code = (language or "en").lower().strip()
    if lang_code not in ("en", "hi", "kn"):
        lang_code = "en"
    target_language = LANGUAGE_NAMES.get(lang_code, "English")

    max_chars = 12000
    truncated = case_text[:max_chars].strip()

    law_references = extract_law_references(truncated)

    cache_key = None
    if os.environ.get("NYAAYA_DISABLE_CACHE") != "1":
        content_hash = hashlib.sha256(truncated.encode("utf-8")).hexdigest()
        cache_key = json.dumps([CASE_SIMPLIFIER_PROMPT_VERSION, lang_code, content_hash], ensure_ascii=False)
        with _cache_lock:
            if cache_key in _memory_cache:
                cached = _memory_cache[cache_key]
                if isinstance(cached, dict):
                    return cached
                return {
                    "simplified_explanation": cached,
                    "law_references": law_references,
                }

    ipc_sections = extract_ipc_sections(truncated)
    mapping_items = []
    for sec in ipc_sections:
        if sec in IPC_TO_BNS:
            mapping_items.append(f"IPC {sec.upper()} -> BNS {IPC_TO_BNS[sec]}")

    if mapping_items:
        mapping_str = "; ".join(mapping_items)
        mapping_context = f"EXPLICIT STATUTORY EQUIVALENTS LIST: {mapping_str}\n\n"
    else:
        mapping_str = "None"
        mapping_context = "EXPLICIT STATUTORY EQUIVALENTS LIST: None\n\n"

    if lang_code == "hi":
        glossary_note = (
            "- TERMINOLOGY GLOSSARY (always followed by the English term in brackets):\n"
            '  * cheating: "छल (cheating)"\n'
            '  * common intention: "सामान्य आशय (common intention)"\n'
            '  * bail: "जमानत (bail)"\n'
            '  * quash: "रद्द करना (quash)"\n'
            "- For other legal terms, keep the English term in brackets when unsure.\n"
        )
    elif lang_code == "kn":
        glossary_note = (
            "- TERMINOLOGY GLOSSARY (always followed by the English term in brackets):\n"
            '  * cheating: "ವಂಚನೆ (cheating)"\n'
            '  * common intention: "ಸಾಮಾನ್ಯ ಉದ್ದೇಶ (common intention)"\n'
            '  * bail: "ಜಾಮೀನು (bail)"\n'
            '  * quash: "ರದ್ದುಪಡಿಸು (quash)"\n'
            "- CRITICAL RULE: Never write Hindi words in Kannada script (e.g. never write 'ಧೋಖಾಧಡಿ' or 'ಧೋಖಾ'). Use proper Kannada legal terms (e.g. 'ವಂಚನೆ (cheating)').\n"
            "- For other legal terms, keep the English term in brackets when unsure.\n"
        )
    else:
        glossary_note = ""

    user_prompt = (
        f"Here is the case text:\n\n{truncated}\n\n"
        f"{mapping_context}"
        f"Explain this case in plain language, following the structure in your instructions.\n"
        f"- Use the offence's legal name as written or implied by the section (IPC 420 = cheating, not 'fraud').\n"
        f"- When mentioning the offences or sections from the case, cite the sections and their BNS equivalents from the list above ({mapping_str}).\n"
        f"- For any section NOT in the explicit list above (e.g. CrPC, Evidence Act), refer to it exactly as written and say NOTHING about equivalents. Never write 'no BNS equivalent' or similar.\n"
        f"IMPORTANT: Write the ENTIRE explanation in {target_language}. All section headings and contents must be in {target_language}.\n"
        f"{glossary_note}"
    )

    max_tokens = 2000 if lang_code == "en" else 2500

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": CASE_SIMPLIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=max_tokens,
        reasoning_effort="low",
    )

    result = response.choices[0].message.content.strip()

    output = {
        "simplified_explanation": result,
        "law_references": law_references,
    }

    if cache_key and os.environ.get("NYAAYA_DISABLE_CACHE") != "1" and result:
        with _cache_lock:
            _memory_cache[cache_key] = output

    return output
