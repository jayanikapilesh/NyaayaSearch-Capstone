"""LLM quality check of generated training pairs: gpt-oss-120b judges N random (question, section) pairs.

    python scripts/judge_training_pairs_v4.py [--n 150] [--seed 42] [--file data/training_pairs_v4_clean.jsonl]

For each pair the judge answers two questions: (1) does the question really match this section (is this section where a lawyer would
look to answer it, not just the same broad topic)? (2) does it sound like something a real person would type (natural, no legal jargon,
no Act names)? A pair passes when both are yes. Writes data/training_pairs_v4_judge.csv and its own cost ledger.
"""
import argparse
import csv
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
KB = os.path.join(ROOT, "Legal_Knowledge_Base_v2.xlsx")
OUT_CSV = os.path.join(DATA, "training_pairs_v4_judge.csv")
COST_JSON = os.path.join(DATA, "training_pairs_v4_judge_cost.json")
MODEL = "openai/gpt-oss-120b"
PRICE_IN, PRICE_OUT = 0.15, 0.75   # USD per million tokens (same figures as the generator)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SYSTEM = """You are a strict quality reviewer for a legal search engine's training data. You are given ONE section of an Indian law and ONE question that was written for it.

Answer two things about the question:
1. section_matches: Is this section really the place where the answer to this question is found? Say true only if the situation described in the question is what this section actually covers. Say false if the question is only loosely related, about a neighbouring topic, or would be answered by a different section.
2. sounds_real: Does the question sound like something a real person, with no legal training, would type or say when they have this problem? Say false if it sounds robotic or unnatural, uses legal jargon, names a law, or reads like a rephrased legal provision.

Reply with ONLY valid JSON: {"section_matches": true or false, "sounds_real": true or false, "reason": "one short sentence for anything false"}"""


def load_sections():
    ws = openpyxl.load_workbook(KB, read_only=True, data_only=True).active
    it = ws.iter_rows(values_only=True)
    h = [str(x).strip() for x in next(it)]
    ix = {k: i for i, k in enumerate(h)}
    out = {}
    for r in it:
        key = (str(r[ix["act_name"]]).strip(), str(r[ix["section_number"]]).strip())
        out.setdefault(key, (str(r[ix["section_title"]] or ""), str(r[ix["legal_text"]] or "")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--file", default=os.path.join(DATA, "training_pairs_v4_clean.jsonl"))
    args = ap.parse_args()
    from dotenv import load_dotenv
    from groq import Groq
    load_dotenv()
    key = os.environ.get("GROQ_API_KEY_GEN") or os.environ.get("GROQ_API_KEY")
    if not key:
        sys.exit("no GROQ_API_KEY(_GEN) in the environment/.env")
    client = Groq(api_key=key)
    rows = [json.loads(l) for l in open(args.file, encoding="utf-8") if l.strip()]
    random.Random(args.seed).shuffle(rows)
    sample = rows[:args.n]
    sections = load_sections()
    lock = threading.Lock()
    usage = {"prompt": 0, "completion": 0, "calls": 0}
    results = [None] * len(sample)

    def judge(i):
        r = sample[i]
        title, text = sections.get((r["act_name"], str(r["section_number"])), (r.get("section_title", ""), ""))
        user = (f"Law: {r['act_name']}\nSection {r['section_number']}: {title}\nSection text: {text[:1800]}\n\nQuestion: {r['query']}")
        verdict = None
        for attempt in range(6):
            try:
                resp = client.chat.completions.create(model=MODEL, temperature=0, max_tokens=800, reasoning_effort="low",
                                                      messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}])
                with lock:
                    usage["prompt"] += resp.usage.prompt_tokens
                    usage["completion"] += resp.usage.completion_tokens
                    usage["calls"] += 1
                raw = (resp.choices[0].message.content or "").strip()
                m = re.search(r"\{.*\}", raw, re.S)
                verdict = json.loads(m.group(0))
                break
            except Exception as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    time.sleep(5 * (attempt + 1))
                else:
                    time.sleep(1)
        results[i] = {"query": r["query"], "act_name": r["act_name"], "section_number": r["section_number"], "section_title": title,
                      "section_matches": None if verdict is None else bool(verdict.get("section_matches")),
                      "sounds_real": None if verdict is None else bool(verdict.get("sounds_real")),
                      "reason": "" if verdict is None else str(verdict.get("reason", ""))}

    with ThreadPoolExecutor(max_workers=5) as ex:
        list(ex.map(judge, range(len(sample))))

    cost = usage["prompt"] * PRICE_IN / 1e6 + usage["completion"] * PRICE_OUT / 1e6
    json.dump({**usage, "estimated_cost_usd": round(cost, 4), "model": MODEL}, open(COST_JSON, "w"), indent=2)
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    judged = [x for x in results if x["section_matches"] is not None]
    passed = [x for x in judged if x["section_matches"] and x["sounds_real"]]
    fail = [x for x in judged if not (x["section_matches"] and x["sounds_real"])]
    print(f"judged {len(judged)} of {len(results)} pairs | PASS (both yes): {len(passed)} = {100 * len(passed) / max(1, len(judged)):.1f}%")
    print(f"  section does not match: {sum(1 for x in judged if not x['section_matches'])} | does not sound real: {sum(1 for x in judged if not x['sounds_real'])}"
          f" | both: {sum(1 for x in judged if not x['section_matches'] and not x['sounds_real'])}")
    print(f"judge cost ~${cost:.4f} ({usage['calls']} calls)")
    print(f"\n{min(10, len(fail))} of {len(fail)} failures:")
    for x in fail[:10]:
        flags = ("NOT-MATCHING " if not x["section_matches"] else "") + ("NOT-REAL" if not x["sounds_real"] else "")
        print(f"- [{flags.strip()}] {x['query']!r}\n    {x['act_name'][:44]} s{x['section_number']} | {x['section_title'][:60]}\n    judge: {x['reason']}")


if __name__ == "__main__":
    main()
