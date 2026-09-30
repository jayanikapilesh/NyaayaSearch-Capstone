"""Clean data/training_pairs_v4.jsonl -> data/training_pairs_v4_clean.jsonl.

Same method as scripts/clean_training_pairs_v2.py, against ALL dev and blind-test questions in data/eval/:
  English sets : test_270_en, eval_queries, final_test_set_batch1-5, holdout3, jayani_validation_set(2), rewrite_validation_set
  Hindi / Kannada sets (test_270_hi/kn, final_test_hindi(2), final_test_kannada(2), kannada_check_set): compared through their cached
  English translations (data/eval/translation_cache.json); a vernacular query with no cached translation cannot be compared by an English
  embedding model and is counted and reported (its English original is normally in one of the English sets above).
Drops: in-file exact duplicates, sections in excluded_placeholder_sections.csv, exact test/dev matches (case/punctuation-insensitive),
and embedding leaks (cosine >= 0.85 with the fine-tuned model used by the search engine). Borderline 0.80-0.85 is reported, not dropped.
"""
import csv
import glob
import json
import os
import re
import string
import sys
from collections import Counter

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
EVAL = os.path.join(DATA, "eval")
INPUT_FILE = os.path.join(DATA, "training_pairs_v4.jsonl")
OUTPUT_FILE = os.path.join(DATA, "training_pairs_v4_clean.jsonl")
LEAKS_CSV = os.path.join(DATA, "training_pairs_v4_leaks.csv")
EXCLUDED_SECTIONS_FILE = os.path.join(DATA, "excluded_placeholder_sections.csv")
MODEL_PATH = os.path.join(ROOT, "finetuned_legal_model")
VERNACULAR = re.compile("[ऀ-ॿಀ-೿]")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def normalize_text(t):
    t = t.lower()
    t = re.sub("[" + re.escape(string.punctuation) + "]", " ", t)
    return " ".join(t.split())


def load_test_queries():
    tc = json.load(open(os.path.join(EVAL, "translation_cache.json"), encoding="utf-8"))

    def translate(q):
        for k in (q, f"low:{q}"):
            if k in tc:
                return tc[k]
        for k, v in tc.items():
            if k.endswith(q):
                return v
        return None

    out, untranslated, per_file = [], 0, Counter()
    for f in sorted(glob.glob(os.path.join(EVAL, "*.json"))):
        name = os.path.basename(f)
        if name == "translation_cache.json" or name == "llm_rerank_cache.json":
            continue
        d = json.load(open(f, encoding="utf-8"))
        for item in d:
            q = item["query"] if isinstance(item, dict) else (item[1] if item[0] in ("Hindi", "Kannada") else item[0])
            if VERNACULAR.search(q):
                en = translate(q)
                if not en:
                    untranslated += 1
                    continue
                q = en
            out.append((q, name))
            per_file[name] += 1
    return out, untranslated, per_file


def main():
    from sentence_transformers import SentenceTransformer
    rows = [json.loads(l) for l in open(INPUT_FILE, encoding="utf-8") if l.strip()]
    excluded = set()
    if os.path.exists(EXCLUDED_SECTIONS_FILE):
        for r in csv.DictReader(open(EXCLUDED_SECTIONS_FILE, encoding="utf-8")):
            a, s = str(r.get("act") or "").strip().lower(), str(r.get("section") or "").strip().lower()
            if a and s:
                excluded.add((a, s))
    tests, untranslated, per_file = load_test_queries()
    uniq, norm_map = [], {}
    for q, src in tests:
        n = normalize_text(q)
        if n not in norm_map:
            norm_map[n] = (q, src)
            uniq.append(q)
    print(f"input rows {len(rows)} | test/dev question instances {len(tests)} from {len(per_file)} files, unique {len(uniq)} "
          f"| vernacular without cached translation (not comparable): {untranslated}")

    model = SentenceTransformer(MODEL_PATH)
    test_emb = model.encode(uniq, normalize_embeddings=True, show_progress_bar=False, batch_size=64)
    max_sims = np.zeros(len(rows), dtype=np.float32)
    best = np.zeros(len(rows), dtype=np.int64)
    B = 512
    for i in range(0, len(rows), B):                                   # chunked: keeps memory small on a laptop
        emb = model.encode([r["query"] for r in rows[i:i + B]], normalize_embeddings=True, show_progress_bar=False, batch_size=64)
        sim = emb @ test_emb.T
        max_sims[i:i + B] = sim.max(axis=1)
        best[i:i + B] = sim.argmax(axis=1)
        if (i // B) % 10 == 0:
            print(f"  encoded {min(i + B, len(rows))}/{len(rows)}", flush=True)

    kept, seen = [], set()
    drops = {"duplicate": [], "placeholder": [], "exact_test": [], "embedding_leak": []}
    borderline = []
    for idx, r in enumerate(rows):
        q = r["query"].strip()
        nq = normalize_text(q)
        act, sec = str(r.get("act_name") or "").strip(), str(r.get("section_number") or "").strip()
        sim, tq = float(max_sims[idx]), uniq[best[idx]]
        if 0.80 <= sim < 0.85:
            borderline.append((sim, q, tq, act, sec))
        if q in seen:
            drops["duplicate"].append((r, ""))
            continue
        seen.add(q)
        if (act.lower(), sec.lower()) in excluded:
            drops["placeholder"].append((r, ""))
            continue
        if nq in norm_map:
            drops["exact_test"].append((r, norm_map[nq][1]))
            continue
        if sim >= 0.85:
            drops["embedding_leak"].append((r, f"{sim:.3f} | {tq}"))
            continue
        kept.append(r)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(LEAKS_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["reason", "new_question", "act_name", "section_number", "matched_test_question_or_source"])
        for k in ("exact_test", "embedding_leak"):
            for r, info in drops[k]:
                w.writerow([k, r["query"], r["act_name"], r["section_number"], info])
    print("\n" + "=" * 70)
    print(f"total in {len(rows)} | kept {len(kept)} | dropped {len(rows) - len(kept)}")
    for k, v in drops.items():
        print(f"  - {k}: {len(v)}")
    print(f"borderline (0.80-0.85, kept): {len(borderline)}")
    for sim, q, tq, a, s in sorted(borderline, reverse=True)[:10]:
        print(f"   {sim:.3f} | {q[:70]!r} ~ {tq[:70]!r}")
    print("\nleaks dropped (first 12):")
    for r, info in (drops["exact_test"] + drops["embedding_leak"])[:12]:
        print(f"   {r['query'][:70]!r} -> {info[:90]}")
    print("\nkept per Act (top 8):", Counter(r["act_name"] for r in kept).most_common(8))


if __name__ == "__main__":
    main()
