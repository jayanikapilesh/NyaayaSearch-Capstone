"""
scripts/clean_training_pairs_old.py

Cleans the old training files:
  - data/training_pairs.jsonl
  - data/training_pairs_batch2.jsonl
  - data/training_pairs_batch3.jsonl
  - data/training_pairs_batch4.jsonl
  - data/training_pairs_batch5.jsonl
  - data/training_pairs_batch6.jsonl

Using the same leakage check as scripts/clean_training_pairs_v2.py:
1. Leakage check against all test/dev questions:
   - data/eval/test_270_en.json (150)
   - data/eval/eval_queries.json (42)
   - data/eval/test_270_hi.json (60) translated via data/eval/translation_cache.json
   - data/eval/test_270_kn.json (60) translated via data/eval/translation_cache.json
   Checks:
   a) Exact match after lowercasing and stripping punctuation.
   b) Cosine similarity using finetuned_legal_model:
      - Drop if cosine similarity >= 0.85 (leak).
      - Report 0.80 <= similarity < 0.85 as borderline.
2. Drop any question whose (act_name, section_number) is in data/excluded_placeholder_sections.csv.
3. Drop exact duplicate queries across/within files.
4. Write kept rows to data/training_pairs_old_clean.jsonl.
5. Report dropped count per file and list every leak pair.
"""

import csv
import json
import os
import re
import string
import sys
from collections import Counter
import numpy as np
from sentence_transformers import SentenceTransformer

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

OLD_TRAINING_FILES = [
    os.path.join(ROOT_DIR, "data", "training_pairs.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch2.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch3.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch4.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch5.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch6.jsonl"),
]

OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "training_pairs_old_clean.jsonl")
EXCLUDED_SECTIONS_FILE = os.path.join(ROOT_DIR, "data", "excluded_placeholder_sections.csv")

TEST_EN_FILE = os.path.join(ROOT_DIR, "data", "eval", "test_270_en.json")
EVAL_QUERIES_FILE = os.path.join(ROOT_DIR, "data", "eval", "eval_queries.json")
TEST_HI_FILE = os.path.join(ROOT_DIR, "data", "eval", "test_270_hi.json")
TEST_KN_FILE = os.path.join(ROOT_DIR, "data", "eval", "test_270_kn.json")
TRANSLATION_CACHE_FILE = os.path.join(ROOT_DIR, "data", "eval", "translation_cache.json")
MODEL_PATH = os.path.join(ROOT_DIR, "finetuned_legal_model")


def normalize_text(text: str) -> str:
    """Lowercases, replaces punctuation with spaces, and collapses whitespace."""
    text = text.lower()
    text = re.sub(r"[" + re.escape(string.punctuation) + r"]", " ", text)
    return " ".join(text.split())


def load_excluded_sections(filepath: str) -> set:
    """Loads (act, section) pairs from excluded_placeholder_sections.csv."""
    excluded = set()
    if not os.path.exists(filepath):
        print(f"Warning: Excluded sections file not found: {filepath}", flush=True)
        return excluded
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            act = str(row.get("act") or "").strip().lower()
            sec = str(row.get("section") or "").strip().lower()
            if act and sec:
                excluded.add((act, sec))
    return excluded


def load_all_test_queries():
    """
    Loads all test/dev queries:
    - 150 English queries from test_270_en.json
    - 42 queries from eval_queries.json
    - 60 Hindi queries translated to English via translation_cache.json
    - 60 Kannada queries translated to English via translation_cache.json
    Returns a list of tuples: (english_query, source_label).
    """
    with open(TEST_EN_FILE, "r", encoding="utf-8") as f:
        test_en = json.load(f)
    en_queries = [(item[0], "test_270_en.json") for item in test_en]

    with open(EVAL_QUERIES_FILE, "r", encoding="utf-8") as f:
        eval_q = json.load(f)
    eval_queries = [(item["query"], "eval_queries.json") for item in eval_q]

    with open(TRANSLATION_CACHE_FILE, "r", encoding="utf-8") as f:
        tc = json.load(f)

    def lookup_translation(raw_q):
        if raw_q in tc:
            return tc[raw_q]
        if f"low:{raw_q}" in tc:
            return tc[f"low:{raw_q}"]
        for k, v in tc.items():
            if k.endswith(raw_q):
                return v
        raise KeyError(f"No translation found in cache for query: {raw_q}")

    with open(TEST_HI_FILE, "r", encoding="utf-8") as f:
        test_hi = json.load(f)
    hi_queries = [(lookup_translation(item[1]), "test_270_hi.json (trans)") for item in test_hi]

    with open(TEST_KN_FILE, "r", encoding="utf-8") as f:
        test_kn = json.load(f)
    kn_queries = [(lookup_translation(item[1]), "test_270_kn.json (trans)") for item in test_kn]

    all_test = en_queries + eval_queries + hi_queries + kn_queries
    return all_test


def main():
    print("=" * 80)
    print("CLEANING OLD TRAINING PAIRS (BATCHES 1-6)")
    print("=" * 80)

    # 1. Load excluded placeholder sections
    excluded_sections = load_excluded_sections(EXCLUDED_SECTIONS_FILE)
    print(f"Loaded {len(excluded_sections)} excluded placeholder (act, section) rules.", flush=True)

    # 2. Load test/dev queries
    test_queries_tagged = load_all_test_queries()
    print(f"Loaded {len(test_queries_tagged)} test/dev query instances.", flush=True)

    unique_test_queries = []
    test_norm_map = {}
    for q, src in test_queries_tagged:
        if q not in unique_test_queries:
            unique_test_queries.append(q)
        norm_q = normalize_text(q)
        if norm_q not in test_norm_map:
            test_norm_map[norm_q] = (q, src)
    print(f"Unique test/dev query strings: {len(unique_test_queries)}", flush=True)

    # 3. Load embedding model
    print(f"Loading embedding model from: {MODEL_PATH}", flush=True)
    model = SentenceTransformer(MODEL_PATH)

    print("Encoding test/dev queries...", flush=True)
    test_embeddings = model.encode(unique_test_queries, normalize_embeddings=True, show_progress_bar=False)

    # 4. Process each file
    all_kept_rows = []
    seen_queries = set()
    file_stats = []
    all_leak_pairs = []
    all_borderline_pairs = []

    for file_path in OLD_TRAINING_FILES:
        rel_name = os.path.relpath(file_path, ROOT_DIR)
        print(f"\nProcessing {rel_name}...", flush=True)

        if not os.path.exists(file_path):
            print(f"  Warning: File not found: {file_path}", flush=True)
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            file_rows = [json.loads(line) for line in f if line.strip()]

        file_in = len(file_rows)
        queries = [r.get("query", "").strip() for r in file_rows]
        embeddings = model.encode(queries, normalize_embeddings=True, show_progress_bar=False)

        sim_matrix = np.matmul(embeddings, test_embeddings.T)
        max_sims = np.max(sim_matrix, axis=1)
        best_test_indices = np.argmax(sim_matrix, axis=1)

        dropped_ph = 0
        dropped_exact = 0
        dropped_sim = 0
        dropped_dup = 0
        file_kept_rows = []

        for idx, row in enumerate(file_rows):
            raw_query = row.get("query", "").strip()
            norm_query = normalize_text(raw_query)
            act = str(row.get("act_name") or "").strip()
            sec = str(row.get("section_number") or "").strip()
            act_sec_key = (act.lower(), sec.lower())

            sim = float(max_sims[idx])
            matched_test_q = unique_test_queries[best_test_indices[idx]]

            if 0.80 <= sim < 0.85:
                all_borderline_pairs.append({
                    "file": rel_name,
                    "row_idx": idx,
                    "query": raw_query,
                    "test_query": matched_test_q,
                    "similarity": sim,
                    "act": act,
                    "section": sec,
                })

            # Check 1: Excluded placeholder section
            if act_sec_key in excluded_sections:
                dropped_ph += 1
                continue

            # Check 2: Exact match with test/dev question
            if norm_query in test_norm_map:
                test_match_q, src = test_norm_map[norm_query]
                dropped_exact += 1
                all_leak_pairs.append({
                    "file": rel_name,
                    "row_idx": idx,
                    "leak_type": "Exact match",
                    "query": raw_query,
                    "test_query": test_match_q,
                    "test_source": src,
                    "similarity": 1.0,
                    "act": act,
                    "section": sec,
                })
                continue

            # Check 3: Cosine similarity >= 0.85
            if sim >= 0.85:
                dropped_sim += 1
                all_leak_pairs.append({
                    "file": rel_name,
                    "row_idx": idx,
                    "leak_type": f"Similarity ({sim:.4f})",
                    "query": raw_query,
                    "test_query": matched_test_q,
                    "test_source": "embedding >= 0.85",
                    "similarity": sim,
                    "act": act,
                    "section": sec,
                })
                continue

            # Check 4: Exact duplicate query
            if raw_query in seen_queries:
                dropped_dup += 1
                continue
            seen_queries.add(raw_query)

            file_kept_rows.append(row)

        all_kept_rows.extend(file_kept_rows)
        file_kept = len(file_kept_rows)
        file_dropped = dropped_ph + dropped_exact + dropped_sim + dropped_dup
        file_stats.append({
            "file": rel_name,
            "total_in": file_in,
            "dropped_ph": dropped_ph,
            "dropped_exact": dropped_exact,
            "dropped_sim": dropped_sim,
            "dropped_dup": dropped_dup,
            "total_dropped": file_dropped,
            "kept": file_kept,
        })

    # Write kept rows to OUTPUT_FILE
    print(f"\nWriting {len(all_kept_rows)} kept rows to: {OUTPUT_FILE}", flush=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for row in all_kept_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Print summary table
    print("\n" + "=" * 80)
    print("DROPPED COUNT PER FILE")
    print("=" * 80)
    header = f"{'File':<30} | {'Total':>5} | {'Placeholders':>12} | {'Exact Leak':>10} | {'Sim Leak':>8} | {'Dups':>5} | {'Dropped':>7} | {'Kept':>5}"
    print(header)
    print("-" * len(header))
    tot_in = tot_ph = tot_exact = tot_sim = tot_dup = tot_drop = tot_kept = 0
    for s in file_stats:
        tot_in += s["total_in"]
        tot_ph += s["dropped_ph"]
        tot_exact += s["dropped_exact"]
        tot_sim += s["dropped_sim"]
        tot_dup += s["dropped_dup"]
        tot_drop += s["total_dropped"]
        tot_kept += s["kept"]
        print(f"{s['file']:<30} | {s['total_in']:>5} | {s['dropped_ph']:>12} | {s['dropped_exact']:>10} | {s['dropped_sim']:>8} | {s['dropped_dup']:>5} | {s['total_dropped']:>7} | {s['kept']:>5}")
    print("-" * len(header))
    print(f"{'TOTAL':<30} | {tot_in:>5} | {tot_ph:>12} | {tot_exact:>10} | {tot_sim:>8} | {tot_dup:>5} | {tot_drop:>7} | {tot_kept:>5}")

    # List every leak pair
    print("\n" + "=" * 80)
    print(f"ALL LEAK PAIRS (TOTAL: {len(all_leak_pairs)})")
    print("=" * 80)
    if not all_leak_pairs:
        print("  None found!")
    else:
        all_leak_pairs.sort(key=lambda x: x["similarity"], reverse=True)
        for i, leak in enumerate(all_leak_pairs, start=1):
            print(f"{i}. [{leak['file']}] Row {leak['row_idx']} | Type: {leak['leak_type']}")
            print(f"   Train query: \"{leak['query']}\"")
            print(f"   Test query:  \"{leak['test_query']}\" ({leak['test_source']})")
            print(f"   Target:      {leak['act']} Section {leak['section']}")

    # Top 10 Borderline
    print("\n" + "=" * 80)
    print(f"TOP BORDERLINE PAIRS (0.80 <= Cosine Similarity < 0.85) [REPORT ONLY, KEPT]")
    print("=" * 80)
    all_borderline_pairs.sort(key=lambda x: x["similarity"], reverse=True)
    for i, bp in enumerate(all_borderline_pairs[:10], start=1):
        print(f"{i}. [{bp['file']}] Sim: {bp['similarity']:.4f} | Row {bp['row_idx']}")
        print(f"   Train query: \"{bp['query']}\"")
        print(f"   Test query:  \"{bp['test_query']}\"")
        print(f"   Target:      {bp['act']} Section {bp['section']}")

    print("\n" + "=" * 80)
    print("DONE.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
