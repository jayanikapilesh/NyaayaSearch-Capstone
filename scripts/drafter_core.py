import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DRAFTER_SYSTEM_PROMPT = """You are a professional legal document template generator for India. You produce clean, print-ready legal document templates.

CRITICAL FORMATTING RULES - FOLLOW EXACTLY:

1. NEVER use bracketed placeholders like "[FILL IN: Name]" or "[DATE]" or "[Address]" anywhere in the output. This is strictly forbidden.

2. Instead, use real visual blank lines the person can write on:
   - For short fields (name, date, amount): use a line of underscores, e.g. "Name: __________________________________________"
   - For addresses or long text: use multiple short blank lines stacked, e.g.:
     Address:
     _______________________________________________
     _______________________________________________
   - For dates specifically, use segmented blanks: "Date: ____ / ____ / ______"
   - For currency amounts: "Monthly Rent: Rs. ____________________"

3. Sensitive/financial information (bank account numbers, IFSC codes, Aadhaar, PAN, phone numbers, email) must ALWAYS be left as blank lines, even if not explicitly asked about. NEVER invent or guess these values. Use extra-long blanks for these: at least 40 underscores.

4. Only fill in a value if the user explicitly provided that exact value. Never invent realistic-looking names, addresses, amounts, or dates as examples or filler. If in doubt, leave it blank.

5. Structure the document like a real, professional legal template:
   - A clear document title as a single # heading
   - Parties/definitions section, each party's fields clearly grouped and labeled (e.g. "LANDLORD" as a subheading, then their fields)
   - The main legal clauses and terms, organized under clear ## subheadings, numbered where appropriate (1., 2., 3. or (a), (b), (c))
   - Consistent blank-line spacing between sections
   - A dedicated fields section for key details (amounts, dates, terms) organized clearly, not buried in paragraph text
   - A clean, dedicated SIGNATURES section at the end, with separate blocks for each party: Signature, Name, Date - each as its own blank line
   - A WITNESSES section (where applicable to the document type) with the same structure: Signature, Name, Address (as stacked blank lines) for each witness
   - End with this exact disclaimer on its own line: "This is an AI-generated draft template for reference only. Please have it reviewed by a qualified lawyer before signing or using it for any legal purpose."

6. Use markdown: # for the document title, ## for major section headings, blank lines between paragraphs and sections so it renders cleanly as a real document.

7. Preserve full legal substance - all standard clauses expected for this document type in India (term, obligations, default, termination, governing law, etc.) - the formatting change must not remove or shorten the actual legal content.

8. Return ONLY the document template itself. No preamble, no explanation, no meta-commentary before or after (except the disclaimer line at the end, which is part of the document).
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
    "divorce_petition": "Divorce Petition (mutual consent or contested, general template)",
}


def draft_document(document_type, details):
    doc_description = DOCUMENT_TYPES.get(document_type)
    if not doc_description:
        raise ValueError(f"Unknown document type: {document_type}")

    details_text = "\n".join(f"- {key}: {value}" for key, value in details.items() if value)

    user_prompt = (
        f"Generate a professional, print-ready template for: {doc_description}.\n\n"
        f"Details explicitly provided by the user (use ONLY these exact values, nothing else):\n"
        f"{details_text if details_text else '(none provided - leave every field as a blank line)'}\n\n"
        f"Every other field must be a real blank line for the person to fill in by hand, following the formatting rules exactly. "
        f"Do not use bracketed placeholders anywhere. Do not invent any values not listed above."
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": DRAFTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=3500,
    )

    return response.choices[0].message.content
