"""Dev check for the 'not covered' (abstain) fix, through the RUNNING backend's /search.

Part A: 270 English dev questions (all answerable) -> ranking scores + how often the app
        WRONGLY says 'not covered' (want close to 0%).
Part B: 30 practice questions about laws NOT in the 81-Act KB -> how often the app
        correctly says 'not covered' (want high).
Never uses the 150-question blind test.
Usage: python scripts/dev_eval_abstain.py --label abstain_on
"""
import argparse
import json
import os
import time

import requests

OUT_OF_SCOPE = [
    "How do I file my income tax return if I have two jobs in one year?",
    "My GST registration got cancelled, how do I get it restored?",
    "Someone is using a logo very similar to my brand's trademark. What can I do?",
    "How do I get a patent for a small invention I made?",
    "What is the process to register a private limited company?",
    "My name is missing from the voter list, how can I get it added before the election?",
    "How do I apply for a gun licence for self-protection?",
    "My visa application for the UK was refused. Can I appeal?",
    "My stockbroker sold my shares without permission. Where can I complain?",
    "Is it legal to trade cryptocurrency in India and how is it taxed?",
    "Someone copied my YouTube video and uploaded it as their own. What are my copyright rights?",
    "The electricity board sent me a huge bill for a month when I was away. How do I dispute it?",
    "My train ticket was cancelled by the railways. How do I get the refund?",
    "What permission do I need from the municipality to build a second floor on my house?",
    "A factory near my house makes loud noise all night. Which pollution rules apply?",
    "Do I need permission to cut down a big tree in my own compound?",
    "How do I get an import export code to start an export business?",
    "As an NRI, how is the rent from my flat in India taxed?",
    "How do I register a partnership firm with my friend?",
    "What are the steps to register a charitable trust?",
    "How can I correct the spelling of my name on my PAN card?",
    "Do I need a licence to fly a drone for wedding photography?",
    "Is it legal to keep a parrot as a pet at home?",
    "How do I apply for an OCI card for my child born abroad?",
    "What is the procedure to get married to a foreign national at an Indian embassy abroad?",
    "My mutual fund distributor gave me wrong advice and I lost money. Where can I complain?",
    "How do I register a housing society as a cooperative society?",
    "What are the rules for getting a licence to sell firecrackers during Diwali?",
    "Can I get compensation from the government for crop loss due to floods?",
    "How do I transfer my provident fund from a government job to the national pension system?",
]


def norm(x):
    s = str(x).strip()
    return s[:-2] if s.endswith(".0") else s


def ask(url, q):
    for _ in range(4):
        try:
            res = requests.post(url, json={"query": q, "top_k": 5}, timeout=90)
            if res.status_code == 429:
                time.sleep(20)
                continue
            res.raise_for_status()
            return res.json()
        except Exception:
            time.sleep(5)
    return {"results": [], "low_confidence": False, "error": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:8000/search")
    a = ap.parse_args()

    dev = json.load(open("data/eval/test_270_en.json", encoding="utf-8"))
    rows = []
    r5 = p1 = mrr = act5 = wrong_flag = errors = 0
    for i, (q, act, sec) in enumerate(dev, 1):
        d = ask(a.url, q)
        errors += bool(d.get("error"))
        results = d.get("results", []) or []
        keys = [(str(r.get("act_name")).strip(), norm(r.get("section_number"))) for r in results[:5]]
        rank = next((k + 1 for k, key in enumerate(keys) if key == (act.strip(), norm(sec))), None)
        flagged = bool(d.get("low_confidence"))
        r5 += rank is not None
        p1 += rank == 1
        mrr += (1 / rank) if rank else 0
        act5 += any(key[0] == act.strip() for key in keys)
        wrong_flag += flagged
        rows.append({"part": "A_dev", "q": q, "rank": rank, "flagged": flagged})
        print(f"[A {i}/{len(dev)}] rank={rank} flagged={flagged}", flush=True)
        time.sleep(1.1)
    n = len(dev)
    part_a = {"n": n, "R@5": round(r5 / n, 3), "P@1": round(p1 / n, 3), "MRR": round(mrr / n, 3),
              "Act@5": round(act5 / n, 3), "wrongly_flagged": round(wrong_flag / n, 3), "errors": errors}

    caught = 0
    for i, q in enumerate(OUT_OF_SCOPE, 1):
        d = ask(a.url, q)
        flagged = bool(d.get("low_confidence")) or not d.get("results")
        caught += flagged
        rows.append({"part": "B_out_of_scope", "q": q, "flagged": flagged})
        print(f"[B {i}/{len(OUT_OF_SCOPE)}] flagged={flagged}", flush=True)
        time.sleep(1.1)
    part_b = {"n": len(OUT_OF_SCOPE), "correctly_flagged": round(caught / len(OUT_OF_SCOPE), 3)}

    print("\n=== Part A: 270 English dev questions (all answerable) ===")
    print(part_a)
    prev_path = "results/dev_eval_api_focused_on.json"
    if os.path.exists(prev_path):
        prev = json.load(open(prev_path, encoding="utf-8")).get("summary", {}).get("en")
        print("Before the fix (same setup, English):", prev)
    print("\n=== Part B: 30 questions about laws NOT in the KB ===")
    print(part_b)

    out = f"results/dev_eval_abstain_{a.label}.json"
    json.dump({"part_a": part_a, "part_b": part_b, "rows": rows}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("saved", out)


if __name__ == "__main__":
    main()
