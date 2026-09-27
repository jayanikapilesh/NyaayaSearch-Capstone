"""
scripts/compare_old_vs_new_data.py

Fair 5-fold GroupKFold comparison of relevance classifier trained on:
  Model A: Training fold's "old" queries only
  Model B: Training fold's "old" + "v2" queries (full training fold)

Evaluated on the exact same test folds across:
  - All test rows
  - Old-source test rows only
  - V2-source test rows only
Also computes per-Act F1 breakdown (BNS, BNSS, Domestic Violence Act, etc.).

No Groq calls, no disk writes, no pipeline changes.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupKFold

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(ROOT_DIR, "data", "eval", "classifier_training_data_v3.csv")

FEATURES = [
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

ACT_SHORT_NAMES = {
    "Bharatiya Nyaya Sanhita, 2023": "Bharatiya Nyaya Sanhita (BNS)",
    "Bharatiya Nagarik Suraksha Sanhita, 2023": "Bharatiya Nagarik Suraksha Sanhita (BNSS)",
    "Protection of Women from Domestic Violence Act, 2005": "Domestic Violence Act (PWDVA)",
    "Indian Contract Act, 1872": "Indian Contract Act",
    "Consumer Protection Act, 2019": "Consumer Protection Act",
    "Transfer of Property Act, 1882": "Transfer of Property Act",
    "Motor Vehicles Act, 1988": "Motor Vehicles Act",
    "Information Technology Act, 2000": "Information Technology Act",
    "Karnataka Rent Act, 1999": "Karnataka Rent Act",
    "Specific Relief Act, 1963": "Specific Relief Act",
    "Right to Information Act, 2005": "Right to Information Act",
}


def fmt(arr):
    return f"{np.mean(arr):.4f} +/- {np.std(arr):.4f}"


def main():
    print(f"scikit-learn version: {sklearn.__version__}", flush=True)
    if sklearn.__version__ != "1.9.1":
        print(f"Warning: Expected scikit-learn 1.9.1, but found {sklearn.__version__}", flush=True)

    print(f"\nLoading data from {DATA_PATH}...", flush=True)
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df):,} total rows across {df['query'].nunique():,} unique queries.", flush=True)

    source_counts = df.groupby("query_source")["query"].nunique().to_dict()
    print(f"Query breakdown: {source_counts.get('old', 0):,} old queries, {source_counts.get('v2', 0):,} v2 queries.", flush=True)

    # 5-fold GroupKFold by query over ALL queries
    gkf = GroupKFold(n_splits=5)
    groups = df["query"]

    # Metrics storage: model -> subset -> metric -> list of fold scores
    subsets = ["all", "old", "v2"]
    metrics_A = {s: {"f1": [], "precision": [], "recall": [], "pr_auc": []} for s in subsets}
    metrics_B = {s: {"f1": [], "precision": [], "recall": [], "pr_auc": []} for s in subsets}

    # Per-act F1 storage: act -> model -> list of fold scores
    unique_acts = [a for a in sorted(df["act_name"].unique()) if a != "act_name"]
    per_act_f1 = {act: {"A": [], "B": []} for act in unique_acts}

    print(f"\nRunning 5-Fold GroupKFold cross-validation (threshold = 0.50)...", flush=True)
    t_cv_start = time.time()

    for fold, (train_idx, test_idx) in enumerate(gkf.split(df, groups=groups), start=1):
        t_fold_start = time.time()
        train_df = df.iloc[train_idx]
        test_df = df.iloc[test_idx]

        # Model A training data: training fold's "old" queries only
        train_A = train_df[train_df["query_source"] == "old"]

        # Model B training data: training fold's "old" + "v2" queries (full training fold)
        train_B = train_df

        # --- Train Model A ---
        rf_A = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_A.fit(train_A[FEATURES], train_A["is_relevant"])

        # --- Train Model B ---
        rf_B = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_B.fit(train_B[FEATURES], train_B["is_relevant"])

        # --- Predictions on Test Fold ---
        prob_A = rf_A.predict_proba(test_df[FEATURES])[:, 1]
        pred_A = (prob_A >= 0.5).astype(int)

        prob_B = rf_B.predict_proba(test_df[FEATURES])[:, 1]
        pred_B = (prob_B >= 0.5).astype(int)

        y_test = test_df["is_relevant"].values

        # --- Evaluate across subsets: all, old, v2 ---
        mask_old = (test_df["query_source"] == "old").values
        mask_v2 = (test_df["query_source"] == "v2").values

        subset_masks = {
            "all": np.ones(len(test_df), dtype=bool),
            "old": mask_old,
            "v2": mask_v2,
        }

        for s_name, mask in subset_masks.items():
            if mask.sum() == 0 or y_test[mask].sum() == 0:
                continue

            y_sub = y_test[mask]

            # Model A
            f1_a = f1_score(y_sub, pred_A[mask], zero_division=0)
            prec_a = precision_score(y_sub, pred_A[mask], zero_division=0)
            rec_a = recall_score(y_sub, pred_A[mask], zero_division=0)
            prauc_a = average_precision_score(y_sub, prob_A[mask])

            metrics_A[s_name]["f1"].append(f1_a)
            metrics_A[s_name]["precision"].append(prec_a)
            metrics_A[s_name]["recall"].append(rec_a)
            metrics_A[s_name]["pr_auc"].append(prauc_a)

            # Model B
            f1_b = f1_score(y_sub, pred_B[mask], zero_division=0)
            prec_b = precision_score(y_sub, pred_B[mask], zero_division=0)
            rec_b = recall_score(y_sub, pred_B[mask], zero_division=0)
            prauc_b = average_precision_score(y_sub, prob_B[mask])

            metrics_B[s_name]["f1"].append(f1_b)
            metrics_B[s_name]["precision"].append(prec_b)
            metrics_B[s_name]["recall"].append(rec_b)
            metrics_B[s_name]["pr_auc"].append(prauc_b)

        # --- Per-Act F1 on all test rows ---
        for act in unique_acts:
            act_mask = (test_df["act_name"] == act).values
            if act_mask.sum() > 0 and y_test[act_mask].sum() > 0:
                act_f1_a = f1_score(y_test[act_mask], pred_A[act_mask], zero_division=0)
                act_f1_b = f1_score(y_test[act_mask], pred_B[act_mask], zero_division=0)
                per_act_f1[act]["A"].append(act_f1_a)
                per_act_f1[act]["B"].append(act_f1_b)

        fold_time = time.time() - t_fold_start
        print(
            f"  Fold {fold}/5 ({fold_time:.1f}s) - "
            f"All F1: A={metrics_A['all']['f1'][-1]:.4f} -> B={metrics_B['all']['f1'][-1]:.4f} | "
            f"Old F1: A={metrics_A['old']['f1'][-1]:.4f} -> B={metrics_B['old']['f1'][-1]:.4f} | "
            f"V2 F1: A={metrics_A['v2']['f1'][-1]:.4f} -> B={metrics_B['v2']['f1'][-1]:.4f}",
            flush=True,
        )

    cv_total_time = time.time() - t_cv_start
    print(f"\n5-Fold CV completed in {cv_total_time:.1f}s.", flush=True)

    # --- Print Comparison Summary Table ---
    print("\n" + "=" * 120)
    print(f"{'5-FOLD GROUPKFOLD COMPARISON: MODEL A (OLD ONLY) VS MODEL B (OLD + V2)':^120}")
    print("=" * 120)
    col_fmt = "{:<25} {:<30} {:<18} {:<18} {:<18} {:<18}"
    print(col_fmt.format("Test Subset", "Model Training Data", "F1 Score", "Precision", "Recall", "PR-AUC"))
    print("-" * 120)

    subset_labels = [
        ("all", "All Test Rows"),
        ("old", "Old-Source Rows Only"),
        ("v2", "V2-Source Rows Only"),
    ]

    for s_key, s_label in subset_labels:
        mA = metrics_A[s_key]
        mB = metrics_B[s_key]
        print(col_fmt.format(s_label, "Model A: Old Queries Only", fmt(mA["f1"]), fmt(mA["precision"]), fmt(mA["recall"]), fmt(mA["pr_auc"])))
        print(col_fmt.format("", "Model B: Old + V2 Queries", fmt(mB["f1"]), fmt(mB["precision"]), fmt(mB["recall"]), fmt(mB["pr_auc"])))
        f1_delta = np.mean(mB["f1"]) - np.mean(mA["f1"])
        pr_delta = np.mean(mB["pr_auc"]) - np.mean(mA["pr_auc"])
        print(f"  --> Delta (B - A): F1 {f1_delta:+.4f} | PR-AUC {pr_delta:+.4f}")
        print("-" * 120)

    # --- Print Per-Act F1 Breakdown Table ---
    print("\n" + "=" * 110)
    print(f"{'PER-ACT F1 BREAKDOWN (ALL TEST ROWS)':^110}")
    print("=" * 110)
    act_col_fmt = "{:<55} {:<20} {:<20} {:<12}"
    print(act_col_fmt.format("Act Name", "Model A (Old Only)", "Model B (Old + V2)", "Delta (B-A)"))
    print("-" * 110)

    # Priority acts first: BNS, BNSS, Domestic Violence Act
    priority_acts = [
        "Bharatiya Nyaya Sanhita, 2023",
        "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "Protection of Women from Domestic Violence Act, 2005",
    ]
    other_acts = [a for a in unique_acts if a not in priority_acts]

    ordered_acts = priority_acts + other_acts

    for act in ordered_acts:
        list_A = per_act_f1.get(act, {}).get("A", [])
        list_B = per_act_f1.get(act, {}).get("B", [])
        if not list_A:
            continue
        mean_A = np.mean(list_A)
        mean_B = np.mean(list_B)
        delta = mean_B - mean_A
        star = " *" if act in priority_acts else ""
        display_name = ACT_SHORT_NAMES.get(act, act) + star
        print(act_col_fmt.format(display_name, fmt(list_A), fmt(list_B), f"{delta:+.4f}"))

    print("-" * 110)
    print("* Key targeted acts with expanded training pairs in v2.")
    print("=" * 110 + "\n")


if __name__ == "__main__":
    main()
