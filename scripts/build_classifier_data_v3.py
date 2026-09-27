"""
scripts/build_classifier_data_v3.py

Builds a unified classifier dataset (v3) where OLD and NEW questions are processed identically.

1. Queries:
   - Old training queries: all unique queries in data/eval/classifier_training_data_clean.csv with
     their gold act + section matched from original question files data/training_pairs*.jsonl (batches 1-6).
   - New queries: data/training_pairs_v2_clean.jsonl.
   - Drop any query whose gold section is in data/excluded_placeholder_sections.csv.
   - Tag each query source as "old" or "v2".

2. Search & Feature Extraction:
   - Current SearchEngine with the same settings as eval_reranker.py --strict-clean, rerank=False, top 10.
   - 10 baseline features from classifier_training_data_clean.csv + gap_to_next:
       1. hybrid_score
       2. semantic_score
       3. bm25_score
       4. matched_term_count
       5. rank
       6. reciprocal_rank
       7. query_length
       8. matched_term_ratio
       9. semantic_minus_bm25
      10. gap_to_next
   - 2 cross-encoder features:
      11. cross_encoder_score (ms-marco-MiniLM-L-6-v2)
      12. cross_encoder_rank (rank of cross_encoder_score among the query's candidates)
   - Labels:
       is_relevant = 1 if the candidate is the gold section.

3. Output:
   - Saves to data/eval/classifier_training_data_v3.csv (including query_source).
   - Progress printed every 200 queries.

4. Report:
   - Queries per source (old, v2, total).
   - Rows (old, v2, total).
   - Positives (old, v2, total).
   - % of queries whose gold section appears in top 10 (old vs v2 separately, and total).
   - Time taken.
"""

import csv
import json
import os
import sys
import time
import pandas as pd

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from search_core import SearchEngine
from eval_reranker import apply_strict_clean

CLEAN_CSV_PATH = os.path.join(ROOT_DIR, "data", "eval", "classifier_training_data_clean.csv")
V2_CLEAN_PATH = os.path.join(ROOT_DIR, "data", "training_pairs_v2_clean.jsonl")
EXCLUDED_SECTIONS_FILE = os.path.join(ROOT_DIR, "data", "excluded_placeholder_sections.csv")
OUTPUT_CSV_PATH = os.path.join(ROOT_DIR, "data", "eval", "classifier_training_data_v3.csv")


def load_excluded_sections(filepath):
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


BATCH_FILES = [
    os.path.join(ROOT_DIR, "data", "training_pairs.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch2.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch3.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch4.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch5.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_batch6.jsonl"),
]


def load_all_queries():
    excluded_sections = load_excluded_sections(EXCLUDED_SECTIONS_FILE)
    print(f"Loaded {len(excluded_sections)} excluded placeholder rules.", flush=True)

    # 1. Build gold lookup from original question files (batches 1-6)
    print("Loading gold targets from batches 1-6...", flush=True)
    gold_lookup = {}
    for bf in BATCH_FILES:
        if not os.path.exists(bf):
            print(f"Warning: Batch file not found: {bf}", flush=True)
            continue
        with open(bf, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                pair = json.loads(line)
                q_text = str(pair.get("query") or "").strip()
                act_text = str(pair.get("act_name") or "").strip()
                sec_text = str(pair.get("section_number") or "").strip()
                if q_text and q_text not in gold_lookup:
                    gold_lookup[q_text] = (act_text, sec_text)
    print(f"Loaded {len(gold_lookup)} unique queries from batch files 1-6.", flush=True)

    # 2. Match ALL unique queries in classifier_training_data_clean.csv
    print(f"Loading unique queries from {CLEAN_CSV_PATH}...", flush=True)
    df_old = pd.read_csv(CLEAN_CSV_PATH)
    unique_old_queries = list(dict.fromkeys(df_old["query"]))
    total_old_unique = len(unique_old_queries)
    print(f"Found {total_old_unique} unique queries in old clean CSV.", flush=True)

    old_queries = []
    old_dropped_ph = 0
    matched_count = 0
    unmatched_queries = []

    for q in unique_old_queries:
        q_clean = str(q).strip()
        if q_clean in gold_lookup:
            matched_count += 1
            act, sec = gold_lookup[q_clean]
            if (act.lower(), sec.lower()) in excluded_sections:
                old_dropped_ph += 1
                continue
            old_queries.append({
                "query": q_clean,
                "gold_act": act,
                "gold_sec": sec,
                "query_source": "old",
            })
        else:
            unmatched_queries.append(q)

    print(f"Old queries matched: {matched_count}/{total_old_unique}", flush=True)
    if unmatched_queries:
        print(f"Unmatched old queries ({len(unmatched_queries)}): {unmatched_queries[:5]}", flush=True)
    else:
        print("Unmatched old queries: None (0)", flush=True)
    print(f"Old queries dropped (excluded placeholders): {old_dropped_ph}", flush=True)
    print(f"Old queries kept: {len(old_queries)}", flush=True)

    # 3. Load V2 queries from training_pairs_v2_clean.jsonl
    print(f"Loading v2 training queries from {V2_CLEAN_PATH}...", flush=True)
    v2_queries = []
    v2_dropped = 0
    with open(V2_CLEAN_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            pair = json.loads(line)
            q = str(pair.get("query") or "").strip()
            act = str(pair.get("act_name") or "").strip()
            sec = str(pair.get("section_number") or "").strip()
            if (act.lower(), sec.lower()) in excluded_sections:
                v2_dropped += 1
                continue
            v2_queries.append({
                "query": q,
                "gold_act": act,
                "gold_sec": sec,
                "query_source": "v2",
            })
    print(f"V2 queries: {len(v2_queries)} kept, {v2_dropped} dropped (excluded placeholders).", flush=True)

    all_queries = old_queries + v2_queries
    print(f"Total unified queries: {len(all_queries)} ({len(old_queries)} old + {len(v2_queries)} v2).", flush=True)
    return all_queries, len(old_queries), len(v2_queries), total_old_unique, matched_count, unmatched_queries, old_dropped_ph


def main():
    start_total_time = time.time()

    (
        queries,
        n_old,
        n_v2,
        total_old_unique,
        old_matched_count,
        old_unmatched,
        old_dropped_ph,
    ) = load_all_queries()
    total_queries = len(queries)

    print("\nInitializing SearchEngine...", flush=True)
    engine = SearchEngine()

    print("\nApplying strict-clean settings (eval_reranker.py --strict-clean)...", flush=True)
    apply_strict_clean(engine)

    print(f"\nProcessing {total_queries} queries (top_k=10, rerank=False)...", flush=True)
    t_search_start = time.time()

    rows = []
    cross_encoder_pairs = []

    for i, q_item in enumerate(queries, start=1):
        query_text = q_item["query"]
        expected_act = q_item["gold_act"]
        expected_sec = q_item["gold_sec"]
        source = q_item["query_source"]

        results = engine.search(query_text, top_k=10, rerank=False)
        query_word_count = len(query_text.split())
        scores = [r["hybrid_score"] for r in results]

        for rank, r in enumerate(results, start=1):
            is_relevant = int(
                str(r["act_name"]).strip().lower() == expected_act.strip().lower()
                and str(r["section_number"]).strip().lower() == expected_sec.strip().lower()
            )
            matched_count = len(r.get("matched_terms", []))
            idx = rank - 1
            gap_to_next = scores[idx] - scores[idx + 1] if idx + 1 < len(scores) else 0.0

            act_str = str(r.get("act_name") or "").strip()
            sec_str = str(r.get("section_number") or "").strip()
            title_str = str(r.get("section_title") or "").strip()
            text_str = str(r.get("legal_text") or "")[:400]
            doc_text = f"{act_str}, Section {sec_str}: {title_str}. {text_str}"

            rows.append({
                "query": query_text,
                "act_name": r["act_name"],
                "section_number": r["section_number"],
                "hybrid_score": r["hybrid_score"],
                "semantic_score": r["semantic_score"],
                "bm25_score": r["bm25_score"],
                "matched_term_count": matched_count,
                "rank": rank,
                "reciprocal_rank": 1.0 / rank,
                "query_length": query_word_count,
                "matched_term_ratio": matched_count / query_word_count if query_word_count > 0 else 0.0,
                "semantic_minus_bm25": r["semantic_score"] - r["bm25_score"],
                "is_relevant": is_relevant,
                "gap_to_next": gap_to_next,
                "query_source": source,
            })
            cross_encoder_pairs.append((query_text, doc_text))

        if i % 200 == 0 or i == total_queries:
            elapsed = time.time() - t_search_start
            q_per_sec = i / elapsed if elapsed > 0 else 0.0
            print(f"Processed {i}/{total_queries} queries ({elapsed:.1f}s, {q_per_sec:.1f} q/s)...", flush=True)

    search_time = time.time() - t_search_start
    print(f"Search retrieval finished in {search_time:.1f}s. Built {len(rows)} candidate rows.", flush=True)

    # Compute CrossEncoder features
    print(f"\nComputing cross-encoder scores for {len(cross_encoder_pairs)} pairs (ms-marco-MiniLM-L-6-v2)...", flush=True)
    t_ce_start = time.time()
    ce_scores = engine.cross_encoder.predict(cross_encoder_pairs, batch_size=128, show_progress_bar=True)
    ce_time = time.time() - t_ce_start
    print(f"Cross-encoder scoring completed in {ce_time:.1f}s ({len(ce_scores)/ce_time:.1f} pairs/sec).", flush=True)

    df = pd.DataFrame(rows)
    df["cross_encoder_score"] = ce_scores
    df["cross_encoder_rank"] = (
        df.groupby("query", sort=False)["cross_encoder_score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    column_order = [
        "query",
        "act_name",
        "section_number",
        "hybrid_score",
        "semantic_score",
        "bm25_score",
        "matched_term_count",
        "rank",
        "reciprocal_rank",
        "query_length",
        "matched_term_ratio",
        "semantic_minus_bm25",
        "is_relevant",
        "gap_to_next",
        "cross_encoder_score",
        "cross_encoder_rank",
        "query_source",
    ]
    df = df[column_order]

    # Save to OUTPUT_CSV_PATH
    print(f"\nSaving dataset to {OUTPUT_CSV_PATH}...", flush=True)
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print("Save complete.", flush=True)

    total_time = time.time() - start_total_time

    # Compute statistics for report
    old_mask = df["query_source"] == "old"
    v2_mask = df["query_source"] == "v2"

    rows_old = int(old_mask.sum())
    rows_v2 = int(v2_mask.sum())
    total_rows = len(df)

    pos_old = int(df.loc[old_mask, "is_relevant"].sum())
    pos_v2 = int(df.loc[v2_mask, "is_relevant"].sum())
    total_pos = int(df["is_relevant"].sum())

    # Queries with gold section in top 10
    has_gold_per_query = df.groupby(["query_source", "query"], sort=False)["is_relevant"].max()
    gold_top10_old = int(has_gold_per_query.get("old", pd.Series(dtype=int)).sum())
    gold_top10_v2 = int(has_gold_per_query.get("v2", pd.Series(dtype=int)).sum())
    gold_top10_total = gold_top10_old + gold_top10_v2

    pct_old = (gold_top10_old / n_old * 100.0) if n_old > 0 else 0.0
    pct_v2 = (gold_top10_v2 / n_v2 * 100.0) if n_v2 > 0 else 0.0
    pct_total = (gold_top10_total / total_queries * 100.0) if total_queries > 0 else 0.0

    print("\n" + "=" * 80)
    print("CLASSIFIER TRAINING DATA V3 REPORT")
    print("=" * 80)
    print("OLD QUERIES GOLD TARGET MATCHING (batches 1-6):")
    print(f"  - Total unique queries in old clean CSV:    {total_old_unique}")
    print(f"  - Matched with gold target from batches:    {old_matched_count}/{total_old_unique}")
    if old_unmatched:
        print(f"  - Unmatched queries ({len(old_unmatched)}):")
        for uq in old_unmatched:
            print(f"      * {uq}")
    else:
        print("  - Unmatched queries:                        None (0)")
    print(f"  - Dropped (gold in excluded placeholders):  {old_dropped_ph}")
    print(f"  - Kept old queries:                         {n_old}")
    print("-" * 80)
    print(f"{'Source':<12} {'Queries':<10} {'Rows':<12} {'Positives':<12} {'Gold in Top 10':<18} {'Top-10 Recall':<15}")
    print("-" * 80)
    print(f"{'old':<12} {n_old:<10} {rows_old:<12} {pos_old:<12} {gold_top10_old:<18} {pct_old:.2f}%")
    print(f"{'v2':<12} {n_v2:<10} {rows_v2:<12} {pos_v2:<12} {gold_top10_v2:<18} {pct_v2:.2f}%")
    print("-" * 80)
    print(f"{'TOTAL':<12} {total_queries:<10} {total_rows:<12} {total_pos:<12} {gold_top10_total:<18} {pct_total:.2f}%")
    print("=" * 80)
    mins = int(total_time // 60)
    secs = total_time % 60
    print(f"Time taken: {total_time:.2f}s ({mins}m {secs:.1f}s)")
    print(f"Saved to: {OUTPUT_CSV_PATH}\n")


if __name__ == "__main__":
    main()
