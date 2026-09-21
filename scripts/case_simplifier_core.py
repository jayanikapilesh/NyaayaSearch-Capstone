import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
"""


def simplify_case(case_text):
    if not case_text or not case_text.strip():
        return "No case text was provided to simplify."

    max_chars = 12000
    truncated = case_text[:max_chars]

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": CASE_SIMPLIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the case text:\n\n{truncated}\n\nExplain this case in plain language, following the structure in your instructions."},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    return response.choices[0].message.content
