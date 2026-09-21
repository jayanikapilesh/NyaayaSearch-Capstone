import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a legal information assistant for Indian law. You explain laws in plain, simple language for ordinary people who are not lawyers.

STRICT RULES:
- Only use the legal sections provided to you below. Do not invent or assume any Act, Section, case, citation, or deadline that is not explicitly given.
- If the provided sections do not fully answer the question, say so clearly instead of guessing.
- Write in plain, everyday language, not legal jargon.
- Keep the explanation focused and practical: what the law says, and what it means for the person's situation.
- Do not give definitive legal advice or tell the person they will definitely win or lose - explain the law, not predict outcomes.
- End with a short "What you can do next" suggestion, grounded only in what the law sections say.
- IMPORTANT: Respond in the SAME language as the user's question. If the question is written in Hindi, respond entirely in Hindi. If the question is written in Kannada, respond entirely in Kannada. If the question is written in English, respond entirely in English. Match the user's language exactly, even though the legal section text provided to you will be in English.
"""

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
}


def detect_language(text):
    """Detect which of English/Hindi/Kannada a piece of text is written in,
    using Unicode script ranges - cheap and reliable, no API call needed."""
    if re.search(r"[\u0C80-\u0CFF]", text):
        return "kn"
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"
    return "en"


def translate_to_english(query):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
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
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def translate_explanation(explanation_text, target_language_code):
    """Translate an already-generated explanation into a target language,
    preserving formatting and legal terms. Used for the language toggle -
    does NOT re-run search or re-generate the legal content."""
    target_language = LANGUAGE_NAMES.get(target_language_code)
    if not target_language:
        return explanation_text

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You translate legal explanations into {target_language}. "
                    "Preserve all formatting (markdown tables, bullet points, headers) exactly as given. "
                    "Preserve all Act names, Section numbers, and legal terms accurately. "
                    "Return ONLY the translated text, nothing else - no preamble, no notes."
                ),
            },
            {"role": "user", "content": explanation_text},
        ],
        temperature=0,
        max_tokens=3000,
    )
    return response.choices[0].message.content.strip()


def generate_explanation(original_query, search_results):
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

    user_prompt = (
        f"User's question: {original_query}\n\n"
        f"Relevant legal sections found:\n{evidence}\n\n"
        f"Explain what these sections mean for the user's situation, in plain language. "
        f"Remember to respond in the same language as the user's question above."
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=2500,
    )

    return response.choices[0].message.content

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
