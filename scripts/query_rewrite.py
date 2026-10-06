"""Rewrite a casual legal question into statute-style search words.
Off unless NYAAYA_QUERY_REWRITE=1. Never names Acts or section numbers.
"""
import os
import threading
from dotenv import load_dotenv
load_dotenv()
from groq import Groq

MODEL = os.getenv("NYAAYA_REWRITE_MODEL", "openai/gpt-oss-120b")
TIMEOUT = float(os.getenv("NYAAYA_REWRITE_TIMEOUT", "5"))
_client = None
_cache = {}
_lock = threading.Lock()

PROMPT = (
    "You turn an ordinary person's description of a legal problem in India into a short search "
    "query for finding the relevant sections of Indian statutes. Describe the legal issue(s) using "
    "the vocabulary statutes use (for example: deficiency in service, refund, breach of contract, "
    "compensation, cheating, criminal breach of trust, non-payment of wages, security deposit, "
    "maintenance, harassment, unfair trade practice), and name the parties in legal terms "
    "(consumer and service provider, tenant and landlord, employer and employee, bank and customer). "
    "Do NOT name any Act or section number. Reply with one line of at most 30 words and nothing else."
)


def rewrite(question):
    with _lock:
        if question in _cache:
            return _cache[question]
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=TIMEOUT, max_retries=0)
    r = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": question}],
        temperature=0, reasoning_effort="low", max_tokens=400)
    text = (r.choices[0].message.content or "").strip()
    out = text.splitlines()[0][:300] if text else ""
    with _lock:
        _cache[question] = out
    return out
