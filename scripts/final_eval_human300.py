import argparse
import csv
import json
import os
import time
import urllib.error
import urllib.request
from collections import defaultdict

import pandas as pd

DEFAULT_LABELS = "data/eval/human_test_300_labelled.xlsx"
DRAFT_LABELS = "data/eval/human_test_300_labelled_claude_draft.xlsx"
CACHE = "data/eval/final_eval_human300_cache.jsonl"
DETAILS = "results/final_eval_human300_details.csv"
SUMMARY = "results/final_eval_human300_summary.txt"


def load_labels(path):
    df = pd.read_excel(path, dtype=str).fillna("")
    rows = []
    for i, r in df.iterrows():
        lang, q, act, sec, also, nc = [str(r.iloc[k]).strip() for k in range(6)]
        acceptable = []
        if act:
            acceptable.append((act, sec))
        if also:
            a, _, s = also.partition("|")
            s = s.strip()
            acceptable.append((a.strip(), s if s and s[0].isdigit() else ""))
        rows.append({
            "id": i, "language": lang, "question": q,
            "not_covered": nc.upper() == "Y" or not act,
            "has_section": bool(act and sec),
            "acceptable": acceptable,
        })
    return rows


def load_cache():
    cache = {}
    if os.path.exists(CACHE):
        with open(CACHE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    cache[d["id"]] = d
    return cache


def ask(base_url, question, timeout=90):
    body = json.dumps({"query": question, "top_k": 5, "rerank": True}).encode("utf-8")
    req = urllib.request.Request(base_url.rstrip("/") + "/search", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data, time.time() - t0


def main():
    p = argparse.ArgumentParser(description="Final test: 300 human questions through the live /search pipeline")
    p.add_argument("--labels", default=None, help="Answer key xlsx (default: reviewed file, else the draft)")
    p.add_argument("--base-url", default="http://127.0.0.1:8000")
    p.add_argument("--pause", type=float, default=1.2, help="Seconds between calls (keeps under 60/min)")
    p.add_argument("--accept-fallback", action="store_true",
                   help="Keep cached answers where the AI picker did not run (default: re-ask them)")
    args = p.parse_args()

    labels_path = args.labels or (DEFAULT_LABELS if os.path.exists(DEFAULT_LABELS) else DRAFT_LABELS)
    status = "FINAL (reviewed answer key)" if labels_path == DEFAULT_LABELS else "PRELIMINARY (unreviewed draft answer key)"
    rows = load_labels(labels_path)
    cache = load_cache()
    print(f"Answer key: {labels_path} -> {status}")
    print(f"{len(rows)} questions, {len(cache)} cached answers found.")

    os.makedirs("results", exist_ok=True)
    for row in rows:
        c = cache.get(row["id"])
        need = c is None or (not c["llm_used"] and c["n_results"] > 0 and not args.accept_fallback)
        if not need:
            continue
        for attempt in range(6):
            try:
                data, secs = ask(args.base_url, row["question"])
                break
            except urllib.error.HTTPError as e:
                wait = 30 if e.code == 429 else 5
                print(f"  [{row['id']}] HTTP {e.code}, waiting {wait}s...")
                time.sleep(wait)
            except Exception as e:
                print(f"  [{row['id']}] error: {e}; retrying in 5s")
                time.sleep(5)
        else:
            print(f"  [{row['id']}] gave up; run the script again later.")
            continue
        results = data.get("results", []) or []
        entry = {
            "id": row["id"],
            "question": row["question"],
            "translated_query": data.get("translated_query", ""),
            "low_confidence": bool(data.get("low_confidence")),
            "n_results": len(results),
            "llm_used": bool(results and results[0].get("llm_reranked")),
            "latency_s": round(secs, 2),
            "top5": [[str(r.get("act_name", "")).strip(), str(r.get("section_number", "")).strip()] for r in results[:5]],
        }
        cache[row["id"]] = entry
        with open(CACHE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"[{row['id'] + 1}/{len(rows)}] {row['language']} | AI picker: {'yes' if entry['llm_used'] else 'NO'} | {secs:.1f}s")
        time.sleep(args.pause)

    # ---------- Scoring ----------
    stats = defaultdict(lambda: defaultdict(float))
    detail_rows = []
    for row in rows:
        c = cache.get(row["id"])
        if not c:
            continue
        top5 = [tuple(x) for x in c["top5"]]
        acts_ok = {a for a, _ in row["acceptable"]}
        pairs_ok = {(a, s) for a, s in row["acceptable"] if s}
        for group in (row["language"], "ALL"):
            s = stats[group]
            s["questions"] += 1
            s["llm_used"] += c["llm_used"]
            s["latency"] += c["latency_s"]
            if row["not_covered"]:
                s["nc"] += 1
                s["nc_flagged"] += c["low_confidence"] or c["n_results"] == 0
                continue
            s["covered"] += 1
            s["act_at1"] += bool(top5) and top5[0][0] in acts_ok
            s["act_at5"] += any(a in acts_ok for a, _ in top5)
            if row["has_section"] and pairs_ok:
                s["sec_n"] += 1
                s["sec_at1"] += bool(top5) and top5[0] in pairs_ok
                s["sec_at5"] += any(t in pairs_ok for t in top5)
                rank = next((i + 1 for i, t in enumerate(top5) if t in pairs_ok), None)
                s["mrr"] += (1 / rank) if rank else 0
        detail_rows.append({
            "id": row["id"], "language": row["language"], "question": row["question"],
            "not_covered": row["not_covered"],
            "acceptable": "; ".join(f"{a} | {s}" for a, s in row["acceptable"]),
            "top1": " | ".join(top5[0]) if top5 else "",
            "act_hit_top5": (not row["not_covered"]) and any(a in acts_ok for a, _ in top5),
            "section_hit_top5": (not row["not_covered"]) and any(t in pairs_ok for t in top5),
            "low_confidence": c["low_confidence"], "ai_picker_used": c["llm_used"],
            "translated_query": c["translated_query"],
        })

    def pct(a, b):
        return f"{100 * a / b:5.1f}%" if b else "  n/a"

    lines = [f"Final test on human questions | answer key: {status}", ""]
    lines.append(f"{'Group':<9}{'Qs':>4}{'Covered':>9}{'Act@1':>8}{'Act@5':>8}{'Sec@1':>8}{'Sec@5':>8}{'MRR':>7}{'NotCov flagged':>16}{'AI picker':>11}{'Avg s':>7}")
    for g in ["English", "Hindi", "Kannada", "ALL"]:
        s = stats.get(g)
        if not s:
            continue
        lines.append(
            f"{g:<9}{int(s['questions']):>4}{int(s['covered']):>9}"
            f"{pct(s['act_at1'], s['covered']):>8}{pct(s['act_at5'], s['covered']):>8}"
            f"{pct(s['sec_at1'], s['sec_n']):>8}{pct(s['sec_at5'], s['sec_n']):>8}"
            f"{(s['mrr'] / s['sec_n'] if s['sec_n'] else 0):>7.3f}"
            f"{pct(s['nc_flagged'], s['nc']):>16}{pct(s['llm_used'], s['questions']):>11}"
            f"{s['latency'] / s['questions']:>7.1f}"
        )
    lines += ["",
              "Act@k / Sec@k: an acceptable Act / Act+section is in the top k results (covered questions only).",
              "NotCov flagged: for questions no law covers, how often the app said 'not confident' or returned nothing.",
              "AI picker: share of questions where the LLM rerank actually ran (others fell back to normal ranking)."]
    text = "\n".join(lines)
    print("\n" + text)
    with open(SUMMARY, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    with open(DETAILS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(detail_rows[0].keys()))
        w.writeheader()
        w.writerows(detail_rows)
    print(f"\nSaved: {SUMMARY} and {DETAILS}")


if __name__ == "__main__":
    main()