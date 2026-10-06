"""LLM shortlist rerank for the live /search (same logic as eval_llm_rerank.py).
Search gets the top 20; gpt-oss-120b picks the best 5. Falls back to normal
results on any error/timeout. Disable with env NYAAYA_LLM_RERANK=0.

The live picker also says whether ANY candidate actually covers the question
("covered"). If not, results are tagged llm_covered=False so the app can show
"not confident / topic not covered". Disable with env NYAAYA_ABSTAIN=0.
"""
import json
import os
import re
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
ABSTAIN = os.getenv("NYAAYA_ABSTAIN", "1") == "1"
TIMEOUT = float(os.getenv("NYAAYA_LLM_RERANK_TIMEOUT", "6"))
POOL = 20
_client = None
_cache = {}
_lock = threading.Lock()

LIVE_PROMPT = (
    "You are given a legal question and a numbered list of candidate law sections "
    "(act name, section number, section title only). Pick the 5 candidates most "
    "relevant to answering the question, best first. "
    "Also decide whether at least one candidate actually governs the person's situation "
    "(set covered to true), or whether none of them is legally relevant to it "
    "(set covered to false). Only use false when no candidate genuinely applies. "
    "Return ONLY a JSON object of the form "
    "{\"top5\": [n1, n2, n3, n4, n5], \"covered\": true} using the candidate numbers shown, "
    "nothing else."
)


def _client_get():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=TIMEOUT, max_retries=0)
    return _client


def _ask_llm(query, cands):
    prompt = LIVE_PROMPT if ABSTAIN else SYSTEM_PROMPT
    user = f"Question: {query}\n\nCandidates:\n{build_candidate_list(cands)}"
    msgs = [{"role": "system", "content": prompt}, {"role": "user", "content": user}]
    last = None
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


def _parse_covered(content):
    """True unless the model clearly said covered=false (any doubt -> True)."""
    try:
        val = json.loads(content).get("covered", True)
        if isinstance(val, str):
            return val.strip().lower() != "false"
        return bool(val)
    except Exception:
        return not re.search(r'"covered"\s*:\s*false', content or "", re.IGNORECASE)


def search_with_llm(engine, query, top_k=5, rerank=True):
    cands = engine.search(query, top_k=max(POOL, top_k), rerank=rerank)
    if os.getenv("NYAAYA_QUERY_REWRITE", "0") == "1":
        try:
            from query_rewrite import rewrite
            rq = rewrite(query)
            if rq:
                extra = engine.search(rq, top_k=POOL, rerank=rerank)
                seen = {(str(c.get("act_name")), str(c.get("section_number"))) for c in cands}
                for c in extra:
                    k = (str(c.get("act_name")), str(c.get("section_number")))
                    if k not in seen and len(cands) < 30:
                        cands.append(c); seen.add(k)
                print("[rewrite+union]", rq[:100], "| pool", len(cands))
        except Exception as e:
            print("[rewrite] skipped:", type(e).__name__, str(e)[:100])
    base = cands[:top_k]
    if not (ENABLED and _READY) or len(cands) < 2:
        return base
    key = (query, ABSTAIN, tuple((str(c.get("act_name")), str(c.get("section_number"))) for c in cands))
    try:
        with _lock:
            cached = _cache.get(key)
        if cached is None:
            content = _ask_llm(query, cands)
            picks = parse_top5(content, len(cands))  # 1-indexed
            covered = _parse_covered(content) if ABSTAIN else True
            with _lock:
                _cache[key] = (picks, covered)
        else:
            picks, covered = cached
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
        out = [dict(cands[i], llm_reranked=True, llm_covered=covered) for i in order[:top_k]]
        print("[llm_rerank] used LLM order" + ("" if covered else " | NOT COVERED"))
        return out
    except Exception as e:
        print("[llm_rerank] fallback:", type(e).__name__, str(e)[:120])
        return base