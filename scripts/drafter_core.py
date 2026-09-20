import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DRAFTER_SYSTEM_PROMPT = """You are a legal document drafting assistant for India. You generate clear, properly formatted legal document drafts based on the details provided by the user.

STRICT RULES:
- Use standard Indian legal document formatting and conventions for the requested document type.
- Fill in ONLY the details the user actually provided. For any information not provided, use a clearly marked placeholder like [FILL IN: description] instead of inventing details.
- Include standard clauses and structure typically expected for this document type in India.
- Do not include today's date unless given - use [DATE] as a placeholder if not provided.
- At the end, add a short note: "This is an AI-generated draft for reference only. Please have it reviewed by a qualified lawyer before signing or using it for any legal purpose."
- Write in clear, formal legal document language appropriate for the document type.
- Return ONLY the document text, no preamble or explanation before or after (except the review note at the end).
"""

DOCUMENT_TYPES = {
    "rent_agreement": "Rent Agreement (Lease Agreement) between a landlord and tenant",
    "affidavit": "General Affidavit for a sworn statement",
    "job_offer": "Employment Offer Letter from an employer to a candidate",
    "legal_notice": "Legal Notice (formal demand/warning letter sent before legal action)",
    "power_of_attorney": "Power of Attorney (General or Specific)",
    "noc": "No Objection Certificate (NOC)",
    "will": "Last Will and Testament",
    "partnership_deed": "Partnership Deed for a business partnership",
}


def draft_document(document_type, details):
    doc_description = DOCUMENT_TYPES.get(document_type)
    if not doc_description:
        raise ValueError(f"Unknown document type: {document_type}")

    details_text = "\n".join(f"- {key}: {value}" for key, value in details.items() if value)

    user_prompt = (
        f"Draft a {doc_description}.\n\n"
        f"Details provided by the user:\n{details_text if details_text else '(no details provided)'}\n\n"
        f"Generate the complete document now, following standard Indian legal formatting for this document type."
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": DRAFTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=3000,
    )

    return response.choices[0].message.content
