"""
Comparison of Text-Only Classifiers:
(a) Off-the-shelf cross_encoder_score alone
(b) Fine-tuned out-of-fold score alone

Inputs:
- data/eval/classifier_training_data_with_reranker.csv (rows where act_name == "act_name" dropped)
- data/eval/crossencoder_oof_predictions.csv
- data/training_pairs.jsonl + data/training_pairs_batch2.jsonl (to define unseen queries)

Evaluation Setup:
- Same 5 GroupKFold folds as finetune_crossencoder_cv.py
- Same inner 80/20 threshold selection on training fold queries
- Reports F1, Precision, Recall, PR-AUC (mean +/- std) for Full and Unseen queries
- Explicitly checks row-for-row alignment (same query, act, section) and halts if mismatched
"""

import os
import sys
import json
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

DATA_DIR = os.path.join(ROOT_DIR, "data")
EVAL_DIR = os.path.join(DATA_DIR, "eval")

RERANKER_CSV_PATH = os.path.join(EVAL_DIR, "classifier_training_data_with_reranker.csv")
OOF_CSV_PATH = os.path.join(EVAL_DIR, "crossencoder_oof_predictions.csv")

BATCH_FILES = [
    os.path.join(DATA_DIR, "training_pairs.jsonl"),
    os.path.join(DATA_DIR, "training_pairs_batch2.jsonl"),
]


def load_datasets():
    """
    Loads both datasets:
    1. classifier_training_data_with_reranker.csv (dropping act_name == 'act_name')
    2. crossencoder_oof_predictions.csv
    """
    if not os.path.exists(RERANKER_CSV_PATH):
        raise FileNotFoundError(f"Reranker CSV not found at {RERANKER_CSV_PATH}")
    if not os.path.exists(OOF_CSV_PATH):
        raise FileNotFoundError(f"OOF predictions CSV not found at {OOF_CSV_PATH}")

    print(f"Loading reranker data from {RERANKER_CSV_PATH}...", flush=True)
    df_reranker_raw = pd.read_csv(RERANKER_CSV_PATH)
    junk_mask = df_reranker_raw["act_name"] == "act_name"
    df_reranker = df_reranker_raw[~junk_mask].copy().reset_index(drop=True)
    print(f"  Loaded {len(df_reranker):,} clean rows (dropped {junk_mask.sum()} junk rows).", flush=True)

    print(f"Loading out-of-fold predictions from {OOF_CSV_PATH}...", flush=True)
    df_oof = pd.read_csv(OOF_CSV_PATH)
    print(f"  Loaded {len(df_oof):,} rows across {df_oof['fold'].nunique()} folds.", flush=True)

    return df_reranker, df_oof


def check_row_for_row_alignment(df_reranker, df_oof):
    """
    Checks that the two CSVs line up row-for-row (same query, act, section).
    Stops with an error if any row differs.
    """
    print("\nVerifying row-for-row alignment (same query, act, section)...", flush=True)
    if len(df_reranker) != len(df_oof):
        raise ValueError(
            f"Row count mismatch: classifier_training_data_with_reranker.csv has {len(df_reranker):,} rows, "
            f"but crossencoder_oof_predictions.csv has {len(df_oof):,} rows."
        )

    mismatches = []
    for idx in range(len(df_reranker)):
        r1 = df_reranker.iloc[idx]
        r2 = df_oof.iloc[idx]

        q1 = str(r1["query"]).strip()
        q2 = str(r2["query"]).strip()
        act1 = str(r1["act_name"]).strip()
        act2 = str(r2["act_name"]).strip()
        sec1 = str(r1["section_number"]).strip()
        sec2 = str(r2["section_number"]).strip()

        if q1 != q2 or act1 != act2 or sec1 != sec2:
            mismatches.append((idx, (q1, act1, sec1), (q2, act2, sec2)))
            if len(mismatches) >= 5:
                break

    if mismatches:
        err_msg = [
            f"\nCRITICAL ERROR: The two CSVs do not line up row-for-row (same query, act, section)!",
            f"Total rows in both files: {len(df_reranker):,}.",
            f"Sample mismatches (first {len(mismatches)}):",
        ]
        for r_idx, (q1, a1, s1), (q2, a2, s2) in mismatches:
            err_msg.append(f"  - Row #{r_idx}:")
            err_msg.append(f"      Reranker CSV: Query={q1!r}, Act={a1!r}, Sec={s1!r}")
            err_msg.append(f"      OOF CSV:      Query={q2!r}, Act={a2!r}, Sec={s2!r}")
        err_msg.append(
            "\nDiagnostic Explanation:\n"
            "  crossencoder_oof_predictions.csv was written in fold-by-fold order (Folds 1 to 5),\n"
            "  whereas classifier_training_data_with_reranker.csv is stored in the original query order.\n"
            "  The files contain the exact same set of 20,850 rows, but their row sequences differ."
        )
        raise ValueError("\n".join(err_msg))

    print(f"Row-for-row verification passed: all {len(df_reranker):,} rows match perfectly.")


def get_production_queries():
    """Identifies the 826 production queries from Batches 1+2 to isolate unseen queries."""
    prod_queries = set()
    for bpath in BATCH_FILES:
        if os.path.exists(bpath):
            with open(bpath, "r", encoding="utf-8") as fp:
                for line in fp:
                    if line.strip():
                        prod_queries.add(json.loads(line)["query"])
    return prod_queries


def fmt(arr):
    """Formats array mean and standard deviation."""
    return f"{np.mean(arr):.4f} +/- {np.std(arr):.4f}"


def run_text_only_comparison(df_reranker, df_oof):
    """
    Compares:
    (a) Off-the-shelf cross_encoder_score alone
    (b) Fine-tuned out-of-fold score alone
    Using the same 5 GroupKFold folds and inner 80/20 threshold selection.
    """
    # Align cross_encoder_score to df_oof by (query, act_name, section_number)
    score_map = df_reranker.groupby(["query", "act_name", "section_number"])["cross_encoder_score"].first().to_dict()
    df = df_oof.copy()
    df["cross_encoder_score"] = [
        score_map[(q, a, str(s))] if (q, a, str(s)) in score_map else score_map.get((q, a, s), np.nan)
        for q, a, s in zip(df["query"], df["act_name"], df["section_number"])
    ]
    # Sigmoid of off-the-shelf logit
    df["off_the_shelf_prob"] = 1.0 / (1.0 + np.exp(-df["cross_encoder_score"]))

    prod_826_queries = get_production_queries()
    all_queries = set(df["query"])
    non_826_queries = all_queries - prod_826_queries

    print(f"\nEvaluation Partitioning:")
    print(f"  - Total unique queries:  {len(all_queries):,} ({len(df):,} candidate rows)")
    print(f"  - Production queries:    {len(prod_826_queries):,} (Batches 1+2)")
    print(f"  - Unseen queries subset: {len(non_826_queries):,} ({len(non_826_queries) * 10:,} rows)")

    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    threshold_grid = np.arange(0.10, 0.91, 0.01)

    # Accumulators for metrics
    res_a_full = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
    res_a_uns = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
    res_b_full = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
    res_b_uns = {"f1": [], "precision": [], "recall": [], "pr_auc": []}

    thresholds_a = []
    thresholds_b = []

    print("\nRunning fold evaluation for (a) and (b)...", flush=True)

    for fold in sorted(df["fold"].unique()):
        tr_df = df[df["fold"] != fold]
        te_df = df[df["fold"] == fold]
        te_uns = te_df[te_df["query"].isin(non_826_queries)]

        # --- Model (a): Off-the-shelf score with inner 80/20 threshold selection ---
        in_tr_idx, in_val_idx = next(gss.split(tr_df, groups=tr_df["query"]))
        in_val = tr_df.iloc[in_val_idx]
        val_probs_a = in_val["off_the_shelf_prob"].values
        val_y = in_val["is_relevant"].values

        best_t_a = 0.5
        best_f1_a = -1.0
        for t in threshold_grid:
            f = f1_score(val_y, (val_probs_a >= t).astype(int), zero_division=0)
            if f > best_f1_a:
                best_f1_a = f
                best_t_a = float(t)
        thresholds_a.append(best_t_a)

        # Evaluate (a) on outer test fold
        te_p_a = te_df["off_the_shelf_prob"].values
        te_y = te_df["is_relevant"].values
        pred_a = (te_p_a >= best_t_a).astype(int)

        res_a_full["f1"].append(f1_score(te_y, pred_a, zero_division=0))
        res_a_full["precision"].append(precision_score(te_y, pred_a, zero_division=0))
        res_a_full["recall"].append(recall_score(te_y, pred_a, zero_division=0))
        res_a_full["pr_auc"].append(average_precision_score(te_y, te_p_a))

        # Evaluate (a) on unseen subset
        uns_p_a = te_uns["off_the_shelf_prob"].values
        uns_y = te_uns["is_relevant"].values
        uns_pred_a = (uns_p_a >= best_t_a).astype(int)

        res_a_uns["f1"].append(f1_score(uns_y, uns_pred_a, zero_division=0))
        res_a_uns["precision"].append(precision_score(uns_y, uns_pred_a, zero_division=0))
        res_a_uns["recall"].append(recall_score(uns_y, uns_pred_a, zero_division=0))
        res_a_uns["pr_auc"].append(average_precision_score(uns_y, uns_p_a))

        # --- Model (b): Fine-tuned out-of-fold score ---
        best_t_b = te_df["threshold_applied"].iloc[0]
        thresholds_b.append(best_t_b)

        te_p_b = te_df["oof_prob"].values
        pred_b = te_df["pred_relevant"].values

        res_b_full["f1"].append(f1_score(te_y, pred_b, zero_division=0))
        res_b_full["precision"].append(precision_score(te_y, pred_b, zero_division=0))
        res_b_full["recall"].append(recall_score(te_y, pred_b, zero_division=0))
        res_b_full["pr_auc"].append(average_precision_score(te_y, te_p_b))

        # Evaluate (b) on unseen subset
        uns_p_b = te_uns["oof_prob"].values
        uns_pred_b = te_uns["pred_relevant"].values

        res_b_uns["f1"].append(f1_score(uns_y, uns_pred_b, zero_division=0))
        res_b_uns["precision"].append(precision_score(uns_y, uns_pred_b, zero_division=0))
        res_b_uns["recall"].append(recall_score(uns_y, uns_pred_b, zero_division=0))
        res_b_uns["pr_auc"].append(average_precision_score(uns_y, uns_p_b))

        print(
            f"  Fold {fold}: (a) T*={best_t_a:.2f}, F1={res_a_full['f1'][-1]:.4f} | "
            f"(b) T*={best_t_b:.2f}, F1={res_b_full['f1'][-1]:.4f}",
            flush=True,
        )

    # Print Final Results Table
    print("\n" + "=" * 125)
    print(f"{'TEXT-ONLY CLASSIFIER COMPARISON (5-FOLD CV)':^125}")
    print("=" * 125)
    print(f"Model (a) Off-the-Shelf Thresholds per Fold: {[round(t, 2) for t in thresholds_a]} (mean: {np.mean(thresholds_a):.2f})")
    print(f"Model (b) Fine-Tuned OOF Thresholds per Fold: {[round(t, 2) for t in thresholds_b]} (mean: {np.mean(thresholds_b):.2f})")
    print("-" * 125)
    header = f"{'Evaluation Subset':<32} {'Text-Only Classifier':<36} {'F1 (Class 1)':<18} {'Precision':<18} {'Recall':<18} {'PR-AUC':<18}"
    print(header)
    print("-" * 125)

    # Full Test Set
    print(f"{'Full Test Set (5-Fold CV)':<32} {'(a) Off-the-Shelf Score Alone':<36} {fmt(res_a_full['f1']):<18} {fmt(res_a_full['precision']):<18} {fmt(res_a_full['recall']):<18} {fmt(res_a_full['pr_auc']):<18}")
    print(f"{'Full Test Set (5-Fold CV)':<32} {'(b) Fine-Tuned OOF Score Alone':<36} {fmt(res_b_full['f1']):<18} {fmt(res_b_full['precision']):<18} {fmt(res_b_full['recall']):<18} {fmt(res_b_full['pr_auc']):<18}")
    print("-" * 125)

    # Unseen Queries Subset
    print(f"{'Unseen Queries (Not in B1+B2)':<32} {'(a) Off-the-Shelf Score Alone':<36} {fmt(res_a_uns['f1']):<18} {fmt(res_a_uns['precision']):<18} {fmt(res_a_uns['recall']):<18} {fmt(res_a_uns['pr_auc']):<18}")
    print(f"{'Unseen Queries (Not in B1+B2)':<32} {'(b) Fine-Tuned OOF Score Alone':<36} {fmt(res_b_uns['f1']):<18} {fmt(res_b_uns['precision']):<18} {fmt(res_b_uns['recall']):<18} {fmt(res_b_uns['pr_auc']):<18}")
    print("=" * 125)

    delta_full = np.mean(res_b_full["f1"]) - np.mean(res_a_full["f1"])
    delta_uns = np.mean(res_b_uns["f1"]) - np.mean(res_a_uns["f1"])
    print("\nSummary Impact of Fine-Tuning:")
    print(f"  - Full Test Set F1:   {np.mean(res_a_full['f1']):.4f} -> {np.mean(res_b_full['f1']):.4f} ({delta_full:+.4f})")
    print(f"  - Unseen Queries F1: {np.mean(res_a_uns['f1']):.4f} -> {np.mean(res_b_uns['f1']):.4f} ({delta_uns:+.4f})")
    print(f"  - Full PR-AUC:        {np.mean(res_a_full['pr_auc']):.4f} -> {np.mean(res_b_full['pr_auc']):.4f} ({np.mean(res_b_full['pr_auc']) - np.mean(res_a_full['pr_auc']):+.4f})")


def main():
    parser = argparse.ArgumentParser(description="Compare text-only classifier scores.")
    parser.add_argument(
        "--allow-reorder",
        action="store_true",
        help="Proceed with comparison by matching rows on (query, act, section) if CSV row orders differ.",
    )
    args = parser.parse_args()

    df_reranker, df_oof = load_datasets()

    # Step 1: Check row-for-row alignment
    try:
        check_row_for_row_alignment(df_reranker, df_oof)
    except ValueError as e:
        if not args.allow_reorder:
            print(str(e), file=sys.stderr, flush=True)
            sys.exit(1)
        else:
            print(f"\nWarning: Row-for-row check failed as raw CSVs differ in order, but --allow-reorder was specified.", flush=True)

    # Step 2: Run comparison
    run_text_only_comparison(df_reranker, df_oof)


if __name__ == "__main__":
    main()
