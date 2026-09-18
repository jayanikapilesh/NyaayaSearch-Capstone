import fitz  # PyMuPDF
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DOCUMENT_SYSTEM_PROMPT = """You are a legal document assistant. You help people understand a specific document they have uploaded.

STRICT RULES:
- Only use the document text provided to you below. Do not invent or assume any fact, date, clause, or detail not explicitly present in the document.
- If the document does not contain the answer to the question, say so clearly instead of guessing.
- Write in plain, everyday language, not legal jargon.
- Do not give definitive legal advice - explain what the document says, not what the person should legally do.
- Respond in the SAME language as the user's question.
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
        f"Answer based only on the document text above."
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
    return answer_question_about_document(
        document_text,
        "Give a clear, plain-language summary of what this document is and its key points."
    )


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
