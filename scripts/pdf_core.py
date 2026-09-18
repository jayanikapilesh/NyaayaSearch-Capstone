import fitz  # PyMuPDF
from groq import Groq
import os
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

    # Truncate very long documents to stay within reasonable token limits
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
