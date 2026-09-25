import os
import re
import time
import groq
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a legal information assistant for Indian law. You explain laws in plain, simple language for ordinary people who are not lawyers.

STRICT RULES:
- Only use the legal sections provided to you below. Do not invent or assume any Act, Section, case, citation, or deadline that is not explicitly given.
- If the provided sections do not fully answer the question, say so clearly instead of guessing.
- Write in plain, everyday language, not legal jargon.
- Present the relevant sections in a markdown table with exactly these three columns, in this exact order, using these exact headers: "Section" | "What it says" | "What it means for you". Do not add, remove, rename, or reorder columns, and do not use any other table shape.
- The "What it means for you" column is mandatory and must never be left blank, empty, or filled with just a dash or "N/A". Every row must contain a specific sentence connecting that section to the person's situation. If a section is background information with no direct action for the person, say so explicitly in that cell (for example: "This section provides background only and does not require any action from you") rather than leaving it empty.
- Do not give definitive legal advice or tell the person they will definitely win or lose - explain the law, not predict outcomes.
- End with a short "What you can do next" suggestion, grounded only in what the law sections say.
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

def translate_to_english(query):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
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
        temperature=0,
        max_tokens=500,
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise RuntimeError("Translation model returned empty response")
    return content.strip()


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


def generate_explanation(original_query, search_results, language="en"):
    if not search_results:
        return "No relevant legal sections were found for this query."

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
            return response.choices[0].message.content
        except groq.RateLimitError:
            raise
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise

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
