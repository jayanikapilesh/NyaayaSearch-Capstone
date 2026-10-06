"""Score the 270 dev questions through the RUNNING backend's /search.
Usage: python scripts/dev_eval_api.py --label off   (or --label on)
"""
import json, time, argparse, requests

def norm(x):
    s = str(x).strip()
    return s[:-2] if s.endswith(".0") else s

ap = argparse.ArgumentParser()
ap.add_argument("--label", required=True)
ap.add_argument("--url", default="http://127.0.0.1:8000/search")
a = ap.parse_args()

sets = {"en": "data/eval/test_270_en.json", "hi": "data/eval/test_270_hi_as_en.json", "kn": "data/eval/test_270_kn_as_en.json"}
summary, rows = {}, []
for lang, path in sets.items():
    data = json.load(open(path, encoding="utf-8"))
    r5 = p1 = mrr = act5 = 0
    for q, act, sec in data:
        for attempt in range(3):
            try:
                res = requests.post(a.url, json={"query": q, "top_k": 5}, timeout=60)
                if res.status_code == 429:
                    time.sleep(20); continue
                res.raise_for_status()
                results = res.json().get("results", [])
                break
            except Exception:
                time.sleep(5); results = []
        keys = [(str(r.get("act_name")).strip(), norm(r.get("section_number"))) for r in results[:5]]
        rank = next((i + 1 for i, k in enumerate(keys) if k == (act.strip(), norm(sec))), None)
        r5 += rank is not None; p1 += rank == 1; mrr += (1 / rank) if rank else 0
        act5 += any(k[0] == act.strip() for k in keys)
        rows.append({"lang": lang, "q": q, "rank": rank})
        time.sleep(1.1)
    n = len(data)
    summary[lang] = {"n": n, "R@5": round(r5 / n, 3), "P@1": round(p1 / n, 3), "MRR": round(mrr / n, 3), "Act@5": round(act5 / n, 3)}
    print(lang, summary[lang], flush=True)
json.dump({"summary": summary, "rows": rows}, open(f"results/dev_eval_api_{a.label}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved results/dev_eval_api_" + a.label + ".json")
