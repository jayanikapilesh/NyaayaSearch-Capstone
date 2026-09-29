import fitz  # PyMuPDF
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DOCUMENT_SYSTEM_PROMPT = """You are a legal document assistant. You help people understand a specific document they have uploaded.

STRICT RULES:
- Answer ONLY from the document's text.
- Do not add details, amounts, frequencies, or consequences that are not written in it. Never invent or substitute time units or frequencies (for example, if the text says 'for the period of occupation', state that exact phrase—do NOT say 'per month' or 'each month').
- When another clause of the same document changes or qualifies the answer (an exception or condition), mention it and name the clause number.
- Any clause giving a right to hold possession or remain without paying rent (such as when the owner fails to refund a deposit or meet another condition) qualifies a clause requiring vacating or imposing damages for not vacating: you MUST mention both the consequence for not vacating and this qualifying exception/condition, naming each clause number.
- If the document does not contain the answer to the question, say so clearly instead of guessing.
- Write in plain, everyday language, not legal jargon.
- Do not give definitive legal advice - explain what the document says, not what the person should legally do.
- Respond in the SAME language as the user's question.
"""

DOCUMENT_SUMMARY_SYSTEM_PROMPT = """You summarize legal documents in clear, plain language for ordinary people who are not lawyers.

STRICT RULES:
- Summarize ONLY from the document's text.
- Do not add details, amounts, frequencies, or time units that are not written in it. Never invent or substitute time units or frequencies (for example, if the text says 'for the period of occupation' or 'for any period of occupation', state that exact phrase—do NOT say 'per month', 'each month', or 'each period').
- If a clause imposes damages or consequences for not vacating, state the exact consequence and exact duration phrase as written in the text (e.g. 'for any period of occupation'—never add monthly frequencies or substitute 'each' for 'any').
- Do not explain how clauses interact, combine clauses, or speculate on their legal relationship unless the document text itself explicitly states that interaction.
- Mention exceptions, exemptions, and conditions explicitly stated in the text for any clause (such as rights to hold possession without paying rent if a deposit is not refunded, or exemptions for normal wear & tear and acts of God).
- Write in plain, everyday language, not legal jargon.
- Do not give definitive legal advice - explain what the document says, not what the person should legally do.
"""

DATE_EXTRACTION_PROMPT = """You extract important dates and deadlines from legal documents.

STRICT RULES:
- Only extract dates and deadlines that are EXPLICITLY stated in the document text. Never infer, calculate, or assume a date that is not written.
- For each date found, note what it refers to (e.g. "rent due date", "lease end date", "notice period deadline").
- If the document mentions a duration (e.g. "within 30 days") but not an exact date, include it as a duration, not a date.
- If no dates or deadlines are found, return an empty list.
- Return ONLY valid JSON, no other text, no markdown formatting, no code fences. Format:
{"dates": [{"description": "what this date/deadline is for", "value": "the date or duration as written in the document"}]}
"""


def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def answer_question_about_document(document_text, question):
    if not document_text:
        return "Could not extract any text from this document. It may be a scanned image without selectable text."

    max_chars = 12000
    truncated = document_text[:max_chars]
    was_truncated = len(document_text) > max_chars

    user_prompt = (
        f"Document text:\n{truncated}\n\n"
        f"{'[Note: document was truncated due to length]' if was_truncated else ''}\n\n"
        f"User's question: {question}\n\n"
        f"Answer based only on the document text above. "
        f"When another clause of the same document changes or qualifies the answer (an exception or condition), mention it and name the clause number. "
        f"Note: any clause allowing a party to hold possession or remain without paying rent qualifies a clause requiring them to vacate or pay damages—state both clauses and their numbers."
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": DOCUMENT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1500,
    )

    return response.choices[0].message.content


def summarize_document(document_text):
    if not document_text:
        return "Could not extract any text from this document. It may be a scanned image without selectable text."

    max_chars = 12000
    truncated = document_text[:max_chars]
    was_truncated = len(document_text) > max_chars

    user_prompt = (
        f"Document text:\n{truncated}\n\n"
        f"{'[Note: document was truncated due to length]' if was_truncated else ''}\n\n"
        f"Give a clear, plain-language summary of what this document is and its key points (including a table of key clauses).\n\n"
        f"STRICT RULES:\n"
        f"- State ONLY what the text says.\n"
        f"- Do not add details, amounts, frequencies, or time units not written in the text (e.g. never say 'per month' or 'each month' unless written in the text; if the text says 'for any period of occupation' or 'for the period of occupation', preserve that exact wording—do NOT say 'per month', 'each month', or 'each period').\n"
        f"- Do not explain how clauses interact unless the text itself explicitly says so.\n"
        f"- Mention exceptions and conditions explicitly stated in the text."
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": DOCUMENT_SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=5000,
    )

    return response.choices[0].message.content.strip()


def extract_dates_and_deadlines(document_text):
    if not document_text:
        return []

    max_chars = 12000
    truncated = document_text[:max_chars]

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": DATE_EXTRACTION_PROMPT},
            {"role": "user", "content": f"Document text:\n{truncated}"},
        ],
        temperature=0,
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if the model added them despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
        return parsed.get("dates", [])
    except json.JSONDecodeError:
        return []
