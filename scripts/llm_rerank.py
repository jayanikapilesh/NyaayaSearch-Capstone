"""LLM shortlist rerank for the live /search (same logic as eval_llm_rerank.py).
Search gets the top 20; gpt-oss-120b picks the best 5. Falls back to normal
results on any error/timeout. Disable with env NYAAYA_LLM_RERANK=0.
"""
import os
import threading
from dotenv import load_dotenv
load_dotenv()

try:
    from groq import Groq
    from eval_llm_rerank import SYSTEM_PROMPT, build_candidate_list, parse_top5, MODEL
    _READY = True
except Exception as e:  # never break the app
    print("[llm_rerank] disabled, import failed:", e)
    _READY = False

ENABLED = os.getenv("NYAAYA_LLM_RERANK", "1") == "1"
TIMEOUT = float(os.getenv("NYAAYA_LLM_RERANK_TIMEOUT", "6"))
POOL = 20
_client = None
_cache = {}
_lock = threading.Lock()


def _client_get():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=TIMEOUT, max_retries=0)
    return _client


def _ask_llm(query, cands):
    user = f"Question: {query}\n\nCandidates:\n{build_candidate_list(cands)}"
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]
    for json_mode in (True, False):
        kw = dict(model=MODEL, messages=msgs, temperature=0, reasoning_effort="low", max_tokens=200)
        if json_mode:
            kw["response_format"] = {"type": "json_object"}
        try:
            r = _client_get().chat.completions.create(**kw)
            return r.choices[0].message.content or ""
        except Exception as e:
            last = e
    raise last


def search_with_llm(engine, query, top_k=5, rerank=True):
    cands = engine.search(query, top_k=max(POOL, top_k), rerank=rerank)
    base = cands[:top_k]
    if not (ENABLED and _READY) or len(cands) < 2:
        return base
    key = (query, tuple((str(c.get("act_name")), str(c.get("section_number"))) for c in cands))
    try:
        with _lock:
            picks = _cache.get(key)
        if picks is None:
            picks = parse_top5(_ask_llm(query, cands), len(cands))  # 1-indexed
            with _lock:
                _cache[key] = picks
        order, seen = [], set()
        for p in picks:
            i = int(p) - 1
            if 0 <= i < len(cands) and i not in seen:
                order.append(i)
                seen.add(i)
        for i in range(len(cands)):
            if len(order) >= top_k:
                break
            if i not in seen:
                order.append(i)
                seen.add(i)
        out = [dict(cands[i], llm_reranked=True) for i in order[:top_k]]
        print("[llm_rerank] used LLM order")
        return out
    except Exception as e:
        print("[llm_rerank] fallback:", type(e).__name__, str(e)[:120])
        return base
