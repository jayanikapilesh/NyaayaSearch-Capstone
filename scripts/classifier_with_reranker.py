"""
Evaluation of Relevance Classifier with Cross-Encoder Reranker Features
and Threshold Tuning without Leakage.

Features:
1. Loads cached cross-encoder scores from data/eval/classifier_training_data_with_reranker.csv.
2. 5-Fold GroupKFold by query (exact same split as fair_comparison.py).
3. Leakage-free threshold tuning:
   - Inside each outer training fold, holds out 20% of its queries (GroupShuffleSplit by query).
   - Chooses decision threshold that maximizes F1 on that inner holdout.
   - Retrains on the full outer training fold.
   - Applies default 0.5 and tuned threshold to the outer test fold.
4. Compares:
   - Default 0.5 threshold vs Tuned threshold on 12-feature model (Full Test Set and Unseen Subset).
   - Evaluates with all rows (20,860) and with the 10 junk rows dropped (20,850 rows, act_name != 'act_name').
5. No Groq calls, no .pkl files saved.
"""

import os
import sys
import json
import argparse
import pandas as pd
import numpy as np

from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

CLEAN_DATA_PATH = os.path.join(ROOT_DIR, "data", "eval", "classifier_training_data_clean.csv")
KB_PATH = os.path.join(ROOT_DIR, "Legal_Knowledge_Base_combined.xlsx")
RERANKER_CSV_PATH = os.path.join(ROOT_DIR, "data", "eval", "classifier_training_data_with_reranker.csv")

BATCH_FILES = ["training_pairs.jsonl", "training_pairs_batch2.jsonl"]
BNS_ACT_NAME = "Bharatiya Nyaya Sanhita, 2023"


def load_dataset():
    """
    Loads dataset with reranker features from cached CSV.
    """
    if not os.path.exists(RERANKER_CSV_PATH):
        raise FileNotFoundError(
            f"Cached reranker data not found at {RERANKER_CSV_PATH}. "
            "Please ensure the cached CSV is present."
        )

    print(f"Loading cached reranker features from {RERANKER_CSV_PATH}...", flush=True)
    df = pd.read_csv(RERANKER_CSV_PATH)

    # Ensure gap_to_next is present
    if "gap_to_next" not in df.columns:
        df["gap_to_next"] = df.groupby("query", sort=False)["hybrid_score"].diff(-1).fillna(0.0)

    print(f"Loaded {len(df):,} candidate rows across {df['query'].nunique():,} unique queries.", flush=True)
    return df


def get_production_queries():
    """Identifies the 826 production queries from Batches 1+2."""
    prod_queries = set()
    for bfile in BATCH_FILES:
        bpath = os.path.join(ROOT_DIR, "data", bfile)
        if os.path.exists(bpath):
            with open(bpath, "r", encoding="utf-8") as fp:
                for line in fp:
                    if line.strip():
                        prod_queries.add(json.loads(line)["query"])
    return prod_queries


def fmt(arr):
    return f"{np.mean(arr):.4f} +/- {np.std(arr):.4f}"


def run_threshold_tuning_experiment(df, label="All Rows (20,860)", features=None):
    """
    Runs 5-fold GroupKFold by query with leakage-free threshold tuning.
    Inside each outer training fold:
      1. Holds out 20% of outer train queries (GroupShuffleSplit).
      2. Trains an inner model on inner-train (80%).
      3. Finds threshold T* maximizing F1 on inner-val (20%).
      4. Retrains model on the entire outer train fold.
      5. Evaluates default threshold (0.5) and tuned threshold (T*) on outer test fold.
    """
    if features is None:
        features = [
            "hybrid_score",
            "semantic_score",
            "bm25_score",
            "matched_term_count",
            "rank",
            "reciprocal_rank",
            "query_length",
            "matched_term_ratio",
            "semantic_minus_bm25",
            "gap_to_next",
            "cross_encoder_score",
            "cross_encoder_rank",
        ]

    prod_826_queries = get_production_queries()
    all_queries = set(df["query"])
    non_826_queries = all_queries - prod_826_queries

    gkf = GroupKFold(n_splits=5)
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)

    # Metrics accumulators
    metrics = {
        "full_default": {"f1": [], "precision": [], "recall": [], "pr_auc": []},
        "full_tuned": {"f1": [], "precision": [], "recall": []},
        "unseen_default": {"f1": [], "precision": [], "recall": [], "pr_auc": []},
        "unseen_tuned": {"f1": [], "precision": [], "recall": []},
    }

    chosen_thresholds = []
    inner_val_f1s = []

    threshold_grid = np.arange(0.10, 0.91, 0.01)

    print(f"\nEvaluating: {label} ({len(df):,} rows, {len(all_queries):,} queries)...", flush=True)

    for fold, (train_idx, test_idx) in enumerate(gkf.split(df, groups=df["query"]), start=1):
        outer_train_df = df.iloc[train_idx]
        outer_test_df = df.iloc[test_idx]
        outer_test_unseen = outer_test_df[outer_test_df["query"].isin(non_826_queries)]

        # --- Step 1: Leakage-free inner split on outer training fold ---
        inner_train_idx, inner_val_idx = next(gss.split(outer_train_df, groups=outer_train_df["query"]))
        inner_train = outer_train_df.iloc[inner_train_idx]
        inner_val = outer_train_df.iloc[inner_val_idx]

        # --- Step 2: Inner model training to find optimal threshold ---
        inner_rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        inner_rf.fit(inner_train[features], inner_train["is_relevant"])

        val_probs = inner_rf.predict_proba(inner_val[features])[:, 1]
        val_y = inner_val["is_relevant"].values

        best_threshold = 0.5
        best_val_f1 = -1.0
        for t in threshold_grid:
            pred_val = (val_probs >= t).astype(int)
            f1_val = f1_score(val_y, pred_val, zero_division=0)
            if f1_val > best_val_f1:
                best_val_f1 = f1_val
                best_threshold = float(t)

        chosen_thresholds.append(best_threshold)
        inner_val_f1s.append(best_val_f1)

        # --- Step 3: Retrain model on the FULL outer training fold ---
        outer_rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        outer_rf.fit(outer_train_df[features], outer_train_df["is_relevant"])

        # Predict on outer test fold
        test_probs_full = outer_rf.predict_proba(outer_test_df[features])[:, 1]
        test_probs_unseen = outer_rf.predict_proba(outer_test_unseen[features])[:, 1]

        y_full = outer_test_df["is_relevant"].values
        y_unseen = outer_test_unseen["is_relevant"].values

        # --- Step 4: Evaluate with Default 0.5 Threshold ---
        # Full Test Set
        pred_full_def = (test_probs_full >= 0.5).astype(int)
        metrics["full_default"]["f1"].append(f1_score(y_full, pred_full_def, zero_division=0))
        metrics["full_default"]["precision"].append(precision_score(y_full, pred_full_def, zero_division=0))
        metrics["full_default"]["recall"].append(recall_score(y_full, pred_full_def, zero_division=0))
        metrics["full_default"]["pr_auc"].append(average_precision_score(y_full, test_probs_full))

        # Unseen Subset
        pred_uns_def = (test_probs_unseen >= 0.5).astype(int)
        metrics["unseen_default"]["f1"].append(f1_score(y_unseen, pred_uns_def, zero_division=0))
        metrics["unseen_default"]["precision"].append(precision_score(y_unseen, pred_uns_def, zero_division=0))
        metrics["unseen_default"]["recall"].append(recall_score(y_unseen, pred_uns_def, zero_division=0))
        metrics["unseen_default"]["pr_auc"].append(average_precision_score(y_unseen, test_probs_unseen))

        # --- Step 5: Evaluate with Tuned Threshold (T*) ---
        # Full Test Set
        pred_full_tune = (test_probs_full >= best_threshold).astype(int)
        metrics["full_tuned"]["f1"].append(f1_score(y_full, pred_full_tune, zero_division=0))
        metrics["full_tuned"]["precision"].append(precision_score(y_full, pred_full_tune, zero_division=0))
        metrics["full_tuned"]["recall"].append(recall_score(y_full, pred_full_tune, zero_division=0))

        # Unseen Subset
        pred_uns_tune = (test_probs_unseen >= best_threshold).astype(int)
        metrics["unseen_tuned"]["f1"].append(f1_score(y_unseen, pred_uns_tune, zero_division=0))
        metrics["unseen_tuned"]["precision"].append(precision_score(y_unseen, pred_uns_tune, zero_division=0))
        metrics["unseen_tuned"]["recall"].append(recall_score(y_unseen, pred_uns_tune, zero_division=0))

        print(
            f"  Fold {fold}/5: chosen T* = {best_threshold:.2f} (inner val F1={best_val_f1:.4f}) | "
            f"Full F1: def={metrics['full_default']['f1'][-1]:.4f} -> tuned={metrics['full_tuned']['f1'][-1]:.4f} | "
            f"Unseen F1: def={metrics['unseen_default']['f1'][-1]:.4f} -> tuned={metrics['unseen_tuned']['f1'][-1]:.4f}",
            flush=True,
        )

    return {
        "label": label,
        "metrics": metrics,
        "thresholds": chosen_thresholds,
        "inner_val_f1s": inner_val_f1s,
    }


def print_results(res):
    """Prints formatted evaluation table for a single experiment."""
    m = res["metrics"]
    label = res["label"]
    thresholds = res["thresholds"]

    print("\n" + "=" * 115)
    print(f"{'12-FEATURE MODEL WITH LEAKAGE-FREE THRESHOLD TUNING':^115}")
    print(f"{label:^115}")
    print("=" * 115)
    print(f"Decision thresholds chosen per fold: {[round(t, 2) for t in thresholds]} (mean: {np.mean(thresholds):.2f})")
    print("-" * 115)
    header = f"{'Evaluation Subset':<35} {'Threshold Setting':<25} {'F1 (Class 1)':<18} {'Precision':<18} {'Recall':<18}"
    print(header)
    print("-" * 115)

    fd = m["full_default"]
    ft = m["full_tuned"]
    print(f"{'Full Test Set (5-Fold CV)':<35} {'Default (0.50)':<25} {fmt(fd['f1']):<18} {fmt(fd['precision']):<18} {fmt(fd['recall']):<18}")
    print(f"{'Full Test Set (5-Fold CV)':<35} {'Tuned per Fold':<25} {fmt(ft['f1']):<18} {fmt(ft['precision']):<18} {fmt(ft['recall']):<18}")
    print("-" * 115)

    ud = m["unseen_default"]
    ut = m["unseen_tuned"]
    print(f"{'Unseen Queries (Not in B1+B2)':<35} {'Default (0.50)':<25} {fmt(ud['f1']):<18} {fmt(ud['precision']):<18} {fmt(ud['recall']):<18}")
    print(f"{'Unseen Queries (Not in B1+B2)':<35} {'Tuned per Fold':<25} {fmt(ut['f1']):<18} {fmt(ut['precision']):<18} {fmt(ut['recall']):<18}")
    print("=" * 115)


def print_comparison_table(res_all, res_clean):
    """Prints side-by-side comparison of keeping vs dropping the 10 junk rows."""
    print("\n" + "=" * 125)
    print(f"{'IMPACT OF DROPPING 10 JUNK ROWS (act_name == \"act_name\")':^125}")
    print("=" * 125)
    header = f"{'Evaluation Subset':<32} {'Setting':<18} {'All Rows (20,860)':<24} {'Clean Rows (20,850)':<24} {'Difference (Delta)':<18}"
    print(header)
    print("-" * 125)

    m_all = res_all["metrics"]
    m_clean = res_clean["metrics"]

    comparisons = [
        ("Full Test Set", "Default (0.50)", m_all["full_default"]["f1"], m_clean["full_default"]["f1"]),
        ("Full Test Set", "Tuned Threshold", m_all["full_tuned"]["f1"], m_clean["full_tuned"]["f1"]),
        ("Unseen Queries", "Default (0.50)", m_all["unseen_default"]["f1"], m_clean["unseen_default"]["f1"]),
        ("Unseen Queries", "Tuned Threshold", m_all["unseen_tuned"]["f1"], m_clean["unseen_tuned"]["f1"]),
    ]

    for subset, setting, all_f1, clean_f1 in comparisons:
        all_mean = np.mean(all_f1)
        clean_mean = np.mean(clean_f1)
        delta = clean_mean - all_mean
        delta_str = f"{delta:+.4f}"
        print(
            f"{subset:<32} {setting:<18} {fmt(all_f1):<24} {fmt(clean_f1):<24} {delta_str:<18}"
        )

    print("=" * 125)


def main():
    parser = argparse.ArgumentParser(description="Evaluate 12-feature relevance classifier with threshold tuning.")
    args = parser.parse_args()

    # 1. Load cached dataset (no recomputation of cross-encoder scores)
    df_raw = load_dataset()

    # 2. Check for the 10 junk rows
    junk_mask = df_raw["act_name"] == "act_name"
    junk_count = junk_mask.sum()
    print(f"\nJunk Row Audit: Found {junk_count} rows where act_name == 'act_name'.")

    # 3. Experiment A: All Rows (20,860 rows)
    res_all = run_threshold_tuning_experiment(
        df_raw,
        label="ALL ROWS (20,860 rows, including 10 junk rows)"
    )
    print_results(res_all)

    # 4. Experiment B: Drop the 10 junk rows (20,850 rows)
    df_clean = df_raw[~junk_mask].reset_index(drop=True)
    res_clean = run_threshold_tuning_experiment(
        df_clean,
        label="DROPPED 10 JUNK ROWS (20,850 clean rows)"
    )
    print_results(res_clean)

    # 5. Side-by-side comparison report
    print_comparison_table(res_all, res_clean)

    print("\nSummary & Findings on Dropping Junk Rows:")
    delta_full_tuned = np.mean(res_clean["metrics"]["full_tuned"]["f1"]) - np.mean(res_all["metrics"]["full_tuned"]["f1"])
    delta_uns_tuned = np.mean(res_clean["metrics"]["unseen_tuned"]["f1"]) - np.mean(res_all["metrics"]["unseen_tuned"]["f1"])
    print(f"  - Dropping the 10 header rows removes invalid (act_name='act_name', section_number='section_number') entries.")
    print(f"  - Full Test Set Tuned F1: {np.mean(res_all['metrics']['full_tuned']['f1']):.4f} -> {np.mean(res_clean['metrics']['full_tuned']['f1']):.4f} ({delta_full_tuned:+.4f})")
    print(f"  - Unseen Queries Tuned F1: {np.mean(res_all['metrics']['unseen_tuned']['f1']):.4f} -> {np.mean(res_clean['metrics']['unseen_tuned']['f1']):.4f} ({delta_uns_tuned:+.4f})")
    print(f"  - Chosen Thresholds: All Rows={res_all['thresholds']} vs Clean Rows={res_clean['thresholds']}")
    print("\nDone. Note: No .pkl models were saved or written to disk.")


if __name__ == "__main__":
    main()
