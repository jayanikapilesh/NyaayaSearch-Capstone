import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

BNS_DECODER_SYSTEM_PROMPT = """You are a legal explainer for the Bharatiya Nyaya Sanhita (BNS), India's criminal code. You explain a specific BNS section in plain, simple language for ordinary people who are not lawyers.

STRICT RULES:
- Only use the section text provided. Do not invent details not present in it.
- Explain what the section means in plain language: what conduct it covers, and what the punishment or consequence is if stated.
- Keep it concise - a few short paragraphs, not a long essay.
- Do not give legal advice or predict outcomes for any specific situation.
"""


def explain_bns_section(section_title, section_text):
    user_prompt = f"Section title: {section_title}\n\nSection text: {section_text}\n\nExplain this BNS section in plain language."

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": BNS_DECODER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=800,
    )

    return response.choices[0].message.content
