"""
scripts/clean_training_pairs_v2.py

Cleans data/training_pairs_v2.jsonl by:
1. Leakage check against all test/dev questions:
   - data/eval/test_270_en.json (150)
   - data/eval/eval_queries.json (42)
   - data/eval/test_270_hi.json (60) translated via data/eval/translation_cache.json
   - data/eval/test_270_kn.json (60) translated via data/eval/translation_cache.json
   Checks:
   a) Exact match after lowercasing and stripping punctuation.
   b) Cosine similarity using the search engine's embedding model (finetuned_legal_model).
      - Flag >= 0.85 as a leak (drop).
      - List 0.80 - 0.85 as borderline (report only, do not drop).
2. Dropping any question whose (act_name, section_number) is in data/excluded_placeholder_sections.csv.
3. Dropping exact duplicates within the file.
4. Writing kept rows to data/training_pairs_v2_clean.jsonl.
5. Reporting total in, dropped per reason, total kept, kept per Act, every leak pair,
   and top 10 borderline pairs.
"""

import csv
import json
import os
import re
import string
import sys
from collections import Counter, OrderedDict
import numpy as np
from sentence_transformers import SentenceTransformer

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INPUT_FILE = os.path.join(ROOT_DIR, "data", "training_pairs_v2.jsonl")
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "training_pairs_v2_clean.jsonl")
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
        print(f"Warning: Excluded sections file not found: {filepath}")
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
    # 1. English test queries (test_270_en.json)
    with open(TEST_EN_FILE, "r", encoding="utf-8") as f:
        test_en = json.load(f)
    en_queries = [(item[0], "test_270_en.json") for item in test_en]

    # 2. Eval queries (eval_queries.json)
    with open(EVAL_QUERIES_FILE, "r", encoding="utf-8") as f:
        eval_q = json.load(f)
    eval_queries = [(item["query"], "eval_queries.json") for item in eval_q]

    # 3. Translation cache
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

    # 4. Hindi queries (test_270_hi.json)
    with open(TEST_HI_FILE, "r", encoding="utf-8") as f:
        test_hi = json.load(f)
    hi_queries = [(lookup_translation(item[1]), "test_270_hi.json (trans)") for item in test_hi]

    # 5. Kannada queries (test_270_kn.json)
    with open(TEST_KN_FILE, "r", encoding="utf-8") as f:
        test_kn = json.load(f)
    kn_queries = [(lookup_translation(item[1]), "test_270_kn.json (trans)") for item in test_kn]

    all_test = en_queries + eval_queries + hi_queries + kn_queries
    return all_test


def main():
    print(f"Loading input training pairs from: {INPUT_FILE}")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        input_rows = [json.loads(line) for line in f if line.strip()]
    total_in = len(input_rows)
    print(f"Total input rows: {total_in}")

    # Load excluded placeholder sections
    excluded_sections = load_excluded_sections(EXCLUDED_SECTIONS_FILE)
    print(f"Loaded {len(excluded_sections)} excluded placeholder (act, section) rules.")

    # Load test/dev queries
    test_queries_tagged = load_all_test_queries()
    print(f"Loaded {len(test_queries_tagged)} test/dev query instances.")

    # Build unique test queries list and normalized map for exact matching
    unique_test_queries = []
    test_norm_map = {}
    for q, src in test_queries_tagged:
        if q not in unique_test_queries:
            unique_test_queries.append(q)
        norm_q = normalize_text(q)
        if norm_q not in test_norm_map:
            test_norm_map[norm_q] = (q, src)
    print(f"Unique test/dev query strings: {len(unique_test_queries)}")

    # Load embedding model (same as search_core.py)
    print(f"Loading embedding model from: {MODEL_PATH}")
    model = SentenceTransformer(MODEL_PATH)

    # Encode unique test queries
    print("Encoding test/dev queries...")
    test_embeddings = model.encode(unique_test_queries, normalize_embeddings=True, show_progress_bar=False)

    # Encode input queries
    input_queries = [r["query"] for r in input_rows]
    print(f"Encoding {len(input_queries)} input queries...")
    input_embeddings = model.encode(input_queries, normalize_embeddings=True, show_progress_bar=False)

    # Compute cosine similarity matrix: (num_inputs x num_unique_tests)
    print("Computing cosine similarity against test/dev questions...")
    sim_matrix = np.matmul(input_embeddings, test_embeddings.T)
    max_sims = np.max(sim_matrix, axis=1)
    best_test_indices = np.argmax(sim_matrix, axis=1)

    # Filtering tracking
    dropped_exact_duplicates = []
    dropped_placeholder_sections = []
    dropped_exact_test_matches = []
    dropped_similarity_leaks = []
    borderline_pairs = []

    seen_queries = set()
    kept_rows = []

    for idx, row in enumerate(input_rows):
        raw_query = row.get("query", "").strip()
        norm_query = normalize_text(raw_query)
        act = str(row.get("act_name") or "").strip()
        sec = str(row.get("section_number") or "").strip()
        act_sec_key = (act.lower(), sec.lower())

        sim = float(max_sims[idx])
        matched_test_q = unique_test_queries[best_test_indices[idx]]

        # Record borderline similarity (0.80 <= sim < 0.85) for reporting
        if 0.80 <= sim < 0.85:
            borderline_pairs.append({
                "row_idx": idx,
                "new_query": raw_query,
                "test_query": matched_test_q,
                "similarity": sim,
                "act": act,
                "section": sec,
            })

        # Check 1: In-file exact duplicate
        if raw_query in seen_queries:
            dropped_exact_duplicates.append((idx, row, "Duplicate query in file"))
            continue
        seen_queries.add(raw_query)

        # Check 2: Excluded placeholder section
        if act_sec_key in excluded_sections:
            dropped_placeholder_sections.append((idx, row, f"Excluded section: {act} Sec {sec}"))
            continue

        # Check 3: Exact match with test/dev questions
        if norm_query in test_norm_map:
            test_match_q, src = test_norm_map[norm_query]
            dropped_exact_test_matches.append((idx, row, f"Exact match with {src}: '{test_match_q}'"))
            continue

        # Check 4: Embedding similarity leak (>= 0.85)
        if sim >= 0.85:
            dropped_similarity_leaks.append({
                "row_idx": idx,
                "row": row,
                "new_query": raw_query,
                "test_query": matched_test_q,
                "similarity": sim,
                "act": act,
                "section": sec,
            })
            continue

        kept_rows.append(row)

    total_kept = len(kept_rows)
    total_dropped = (
        len(dropped_exact_duplicates)
        + len(dropped_placeholder_sections)
        + len(dropped_exact_test_matches)
        + len(dropped_similarity_leaks)
    )

    # Write kept rows to OUTPUT_FILE
    print(f"\nWriting {total_kept} kept rows to: {OUTPUT_FILE}")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for row in kept_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Counts per Act for kept rows
    kept_per_act = Counter(r.get("act_name", "Unknown") for r in kept_rows)

    # Print comprehensive report
    print("\n" + "=" * 80)
    print("TRAINING PAIRS V2 CLEANING REPORT")
    print("=" * 80)
    print(f"Total in:                                   {total_in:>6}")
    print(f"Total dropped:                              {total_dropped:>6}")
    print(f"  - In-file exact duplicates:               {len(dropped_exact_duplicates):>6}")
    print(f"  - Excluded placeholder sections:          {len(dropped_placeholder_sections):>6}")
    print(f"  - Exact test/dev matches:                 {len(dropped_exact_test_matches):>6}")
    print(f"  - Embedding similarity leaks (>= 0.85):   {len(dropped_similarity_leaks):>6}")
    print(f"Total kept:                                 {total_kept:>6}")

    print("\n--- Kept Questions per Act ---")
    for act_name, count in sorted(kept_per_act.items()):
        print(f"  {act_name:<55}: {count:>5}")

    print("\n--- Excluded Placeholder Sections Dropped ---")
    if not dropped_placeholder_sections:
        print("  None")
    for idx, row, reason in dropped_placeholder_sections:
        print(f"  Row {idx}: {row.get('act_name')} Sec {row.get('section_number')} | Query: \"{row.get('query')}\"")

    print("\n--- Leak Pairs (Cosine Similarity >= 0.85) ---")
    if not dropped_similarity_leaks:
        print("  None")
    dropped_similarity_leaks.sort(key=lambda x: x["similarity"], reverse=True)
    for leak in dropped_similarity_leaks:
        print(f"  Row {leak['row_idx']} (Sim: {leak['similarity']:.4f}):")
        print(f"    New question:  \"{leak['new_query']}\"")
        print(f"    Test question: \"{leak['test_query']}\"")
        print(f"    Target:        {leak['act']} Section {leak['section']}")

    print("\n--- Top 10 Borderline Pairs (0.80 <= Cosine Similarity < 0.85) [Report Only, Kept] ---")
    borderline_pairs.sort(key=lambda x: x["similarity"], reverse=True)
    if not borderline_pairs:
        print("  None")
    for i, bp in enumerate(borderline_pairs[:10], start=1):
        print(f"  {i}. Sim: {bp['similarity']:.4f} (Row {bp['row_idx']})")
        print(f"     New question:  \"{bp['new_query']}\"")
        print(f"     Test question: \"{bp['test_query']}\"")
        print(f"     Target:        {bp['act']} Section {bp['section']}")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
