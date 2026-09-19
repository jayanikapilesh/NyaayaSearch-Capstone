import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DICTIONARY_SYSTEM_PROMPT = """You are a legal dictionary assistant for Indian law. You explain legal terms in simple, plain language for ordinary people who are not lawyers.

STRICT RULES:
- Give a clear, short definition (2-4 sentences) in plain everyday language, no legal jargon.
- If relevant, briefly note which Indian law or Act commonly uses this term.
- If the term is not a real legal term, say so honestly rather than making up a definition.
- Do not give legal advice - only explain what the term means.
- Respond in the SAME language as the term/question was asked in.
"""


def define_term(term):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": DICTIONARY_SYSTEM_PROMPT},
            {"role": "user", "content": f"Define this legal term in plain language: {term}"},
        ],
        temperature=0.2,
        max_tokens=400,
    )
    return response.choices[0].message.content
