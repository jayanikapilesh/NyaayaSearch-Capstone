import os, json, threading
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from groq import Groq

MODEL = os.getenv("NYAAYA_REWRITE_MODEL", "openai/gpt-oss-120b")
_client = None
_cache = {}
_lock = threading.Lock()
_acts = None

PROMPT = ("You are an expert in Indian law. Given a person's legal problem and a numbered list of Acts, "
          "choose up to 3 Acts most likely to contain the section that answers it, best first. "
          'Reply only with JSON like {"acts": [12, 5]}. Use [] if none apply.')

def acts_list():
    global _acts
    if _acts is None:
        p = os.getenv("NYAAYA_KB_PATH", "Legal_Knowledge_Base_focused.xlsx")
        df = pd.read_excel(p, usecols=["act_name"])
        _acts = sorted(df["act_name"].astype(str).str.strip().unique())
    return _acts

def suggest_acts(question):
    with _lock:
        if question in _cache:
            return _cache[question]
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=float(os.getenv("NYAAYA_REWRITE_TIMEOUT", "6")), max_retries=0)
    acts = acts_list()
    listing = "\n".join(f"{i+1}. {a}" for i, a in enumerate(acts))
    r = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": PROMPT},
                  {"role": "user", "content": f"Problem: {question}\n\nActs:\n{listing}"}],
        temperature=0, reasoning_effort="low", max_tokens=500,
        response_format={"type": "json_object"})
    nums = json.loads(r.choices[0].message.content or "{}").get("acts", [])
    out = [acts[int(n) - 1] for n in nums[:3] if str(n).isdigit() and 1 <= int(n) <= len(acts)]
    with _lock:
        _cache[question] = out
    return out
