import os
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import GroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

CLEAN_DATA_PATH = os.path.join(ROOT_DIR, "data", "eval", "classifier_training_data_clean.csv")
PROD_MODEL_PATH = os.path.join(ROOT_DIR, "relevance_classifier_v2.pkl")

# 1. Load clean training data
df = pd.read_csv(CLEAN_DATA_PATH)

# Add gap_to_next if missing
if "gap_to_next" not in df.columns:
    df["gap_to_next"] = df.groupby("query", sort=False)["hybrid_score"].diff(-1).fillna(0.0)

# Identify the 826 production queries (Batches 1+2)
prod_826_queries = set()
for bfile in ["training_pairs.jsonl", "training_pairs_batch2.jsonl"]:
    bpath = os.path.join(ROOT_DIR, "data", bfile)
    with open(bpath, "r", encoding="utf-8") as fp:
        for line in fp:
            if line.strip():
                prod_826_queries.add(json.loads(line)["query"])

all_queries = set(df["query"])
non_826_queries = all_queries - prod_826_queries

# Features for Random Forest
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
]

# Load existing production model (read-only)
prod_model = joblib.load(PROD_MODEL_PATH)

# 2. 5-Fold GroupKFold by query
gkf = GroupKFold(n_splits=5)

# Metrics accumulators across folds
full_metrics_A = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
full_metrics_B = {"f1": [], "precision": [], "recall": [], "pr_auc": []}

sub_metrics_A = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
sub_metrics_B = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
sub_metrics_prod = {"f1": [], "precision": [], "recall": [], "pr_auc": []}

for fold, (train_idx, test_idx) in enumerate(gkf.split(df, groups=df["query"]), start=1):
    train_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

    # Model A: Train only on queries from batches 1+2 in this train fold
    train_df_A = train_df[train_df["query"].isin(prod_826_queries)]
    rf_A = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    rf_A.fit(train_df_A[features], train_df_A["is_relevant"])

    # Model B: Train on all queries (batches 1-6) in this train fold
    train_df_B = train_df
    rf_B = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    rf_B.fit(train_df_B[features], train_df_B["is_relevant"])

    # --- Evaluate on full test set of this fold ---
    for model, mdict in [(rf_A, full_metrics_A), (rf_B, full_metrics_B)]:
        yp = model.predict(test_df[features])
        yprob = model.predict_proba(test_df[features])[:, 1]
        mdict["f1"].append(f1_score(test_df["is_relevant"], yp, zero_division=0))
        mdict["precision"].append(precision_score(test_df["is_relevant"], yp, zero_division=0))
        mdict["recall"].append(recall_score(test_df["is_relevant"], yp, zero_division=0))
        mdict["pr_auc"].append(average_precision_score(test_df["is_relevant"], yprob))

    # --- Evaluate ONLY on test queries NOT in batches 1+2 ---
    test_sub = test_df[test_df["query"].isin(non_826_queries)]
    for model, mdict in [(rf_A, sub_metrics_A), (rf_B, sub_metrics_B), (prod_model, sub_metrics_prod)]:
        yp = model.predict(test_sub[features])
        yprob = model.predict_proba(test_sub[features])[:, 1]
        mdict["f1"].append(f1_score(test_sub["is_relevant"], yp, zero_division=0))
        mdict["precision"].append(precision_score(test_sub["is_relevant"], yp, zero_division=0))
        mdict["recall"].append(recall_score(test_sub["is_relevant"], yp, zero_division=0))
        mdict["pr_auc"].append(average_precision_score(test_sub["is_relevant"], yprob))

# 3. Print Final Comparison Table
def fmt(arr):
    return f"{np.mean(arr):.4f} +/- {np.std(arr):.4f}"

print("=" * 115)
print(f"{'FAIR CLASSIFIER COMPARISON (5-FOLD GROUPKFOLD BY QUERY)':^115}")
print("=" * 115)
print(f"{'Evaluation Subset':<35} {'Model':<30} {'Queries':<10} {'F1 (Class 1)':<18} {'Precision':<18} {'Recall':<18} {'PR-AUC':<18}")
print("-" * 115)

print(f"{'Full Test Set (5-Fold CV)':<35} {'Model A (Batches 1+2)':<30} {'2,084':<10} {fmt(full_metrics_A['f1']):<18} {fmt(full_metrics_A['precision']):<18} {fmt(full_metrics_A['recall']):<18} {fmt(full_metrics_A['pr_auc']):<18}")
print(f"{'Full Test Set (5-Fold CV)':<35} {'Model B (Batches 1-6)':<30} {'2,084':<10} {fmt(full_metrics_B['f1']):<18} {fmt(full_metrics_B['precision']):<18} {fmt(full_metrics_B['recall']):<18} {fmt(full_metrics_B['pr_auc']):<18}")
print("-" * 115)

sub_q_count = len(non_826_queries)
print(f"{'Unseen Queries (Not in Batches 1+2)':<35} {'Model A (Batches 1+2)':<30} {str(sub_q_count):<10} {fmt(sub_metrics_A['f1']):<18} {fmt(sub_metrics_A['precision']):<18} {fmt(sub_metrics_A['recall']):<18} {fmt(sub_metrics_A['pr_auc']):<18}")
print(f"{'Unseen Queries (Not in Batches 1+2)':<35} {'Model B (Batches 1-6)':<30} {str(sub_q_count):<10} {fmt(sub_metrics_B['f1']):<18} {fmt(sub_metrics_B['precision']):<18} {fmt(sub_metrics_B['recall']):<18} {fmt(sub_metrics_B['pr_auc']):<18}")
print(f"{'Unseen Queries (Not in Batches 1+2)':<35} {'Prod v2 (relevance_classifier_v2)':<30} {str(sub_q_count):<10} {fmt(sub_metrics_prod['f1']):<18} {fmt(sub_metrics_prod['precision']):<18} {fmt(sub_metrics_prod['recall']):<18} {fmt(sub_metrics_prod['pr_auc']):<18}")
print("=" * 115)
print(f"\nNote: Test queries NOT in batches 1+2 leave exactly {sub_q_count} unique queries ({sub_q_count * 10} rows).")
print("Prod v2 was trained on batches 1+2, making this 1,258-query subset a strictly unseen evaluation for it.")
