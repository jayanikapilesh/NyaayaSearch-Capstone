import time, argparse, requests, pandas as pd
ap = argparse.ArgumentParser()
ap.add_argument("--label", required=True)
a = ap.parse_args()
d = pd.read_csv("data/eval/synthetic200_act_labels.csv")
rows = []
for i, r in d.iterrows():
    res = []
    for attempt in range(3):
        try:
            x = requests.post("http://127.0.0.1:8000/search", json={"query": r["Question"], "top_k": 5}, timeout=60)
            if x.status_code == 429:
                time.sleep(20); continue
            x.raise_for_status(); res = x.json().get("results", []); break
        except Exception:
            time.sleep(5)
    acts = [str(z.get("act_name")).strip() for z in res[:5]]
    rows.append({"ID": r["ID"], "lang": r["Language"], "a1": bool(acts) and acts[0] == r["expected_act"], "a5": r["expected_act"] in acts})
    if (i + 1) % 25 == 0:
        print(f"{i+1}/200", flush=True)
    time.sleep(1.1)
o = pd.DataFrame(rows)
o.to_csv(f"results/synthetic200_{a.label}.csv", index=False)
print("ALL  Act@1 %.1f%%  Act@5 %.1f%%" % (100 * o.a1.mean(), 100 * o.a5.mean()))
for l, g in o.groupby("lang"):
    print("%-8s n=%d  Act@1 %.1f%%  Act@5 %.1f%%" % (l, len(g), 100 * g.a1.mean(), 100 * g.a5.mean()))
