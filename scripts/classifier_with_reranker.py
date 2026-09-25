"""
Evaluation of Relevance Classifier with Cross-Encoder Reranker Features.

Compares:
(a) Current 10 features (Model B baseline from fair_comparison.py)
(b) Current features + cross-encoder score + candidate rank among query's candidates

Uses:
- Model: cross-encoder/ms-marco-MiniLM-L-6-v2
- Data: data/eval/classifier_training_data_clean.csv (Model B data)
- Legal Knowledge Base: Legal_Knowledge_Base_combined.xlsx
- 5-Fold GroupKFold by query (exact same split & settings as fair_comparison.py)
- Evaluated on Full Test Set and Unseen Subset (queries not in batches 1+2)
- Reports F1, Precision, Recall, PR-AUC (mean +/- std) + per-Act F1 for BNS
"""

import os
import sys
import json
import time
import argparse
import pandas as pd
import numpy as np

from sklearn.model_selection import GroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score
from sentence_transformers import CrossEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

CLEAN_DATA_PATH = os.path.join(ROOT_DIR, "data", "eval", "classifier_training_data_clean.csv")
KB_PATH = os.path.join(ROOT_DIR, "Legal_Knowledge_Base_combined.xlsx")
RERANKER_CSV_PATH = os.path.join(ROOT_DIR, "data", "eval", "classifier_training_data_with_reranker.csv")

BATCH_FILES = ["training_pairs.jsonl", "training_pairs_batch2.jsonl"]
BNS_ACT_NAME = "Bharatiya Nyaya Sanhita, 2023"


def load_knowledge_base(kb_path):
    """
    Loads Legal_Knowledge_Base_combined.xlsx and builds a lookup mapping
    by (normalized act_name, normalized section_number).
    """
    print(f"Loading Legal Knowledge Base from {kb_path}...", flush=True)
    kb_df = pd.read_excel(kb_path)
    kb_map = {}
    for _, row in kb_df.iterrows():
        act = str(row.get("act_name") or "").strip().lower()
        sec = str(row.get("section_number") or "").strip().lower()
        kb_map[(act, sec)] = {
            "act_name": str(row.get("act_name") or "").strip(),
            "section_number": str(row.get("section_number") or "").strip(),
            "section_title": str(row.get("section_title") or "").strip(),
            "legal_text": str(row.get("legal_text") or "").strip(),
        }
    print(f"Loaded {len(kb_map)} unique act+section entries from Knowledge Base.", flush=True)
    return kb_map


def compute_cross_encoder_features(df, kb_map, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2", batch_size=128):
    """
    Computes cross-encoder score for each (query, section document text) pair.
    Uses exact same document text format as search_core.py:
    f"{act_name}, Section {section_number}: {section_title}. {legal_text[:400]}"
    """
    print(f"\nBuilding query-document pairs for {len(df)} rows...", flush=True)
    matched_count = 0
    unmatched_rows = []
    pairs = []

    for idx, row in df.iterrows():
        act_key = str(row.get("act_name") or "").strip().lower()
        sec_key = str(row.get("section_number") or "").strip().lower()
        lookup_key = (act_key, sec_key)

        if lookup_key in kb_map:
            rec = kb_map[lookup_key]
            act_str = rec["act_name"]
            sec_str = rec["section_number"]
            title_str = rec["section_title"]
            text_str = rec["legal_text"][:400]
            doc_text = f"{act_str}, Section {sec_str}: {title_str}. {text_str}"
            matched_count += 1
        else:
            unmatched_rows.append((idx, row.get("act_name"), row.get("section_number")))
            doc_text = f"{row.get('act_name', '')}, Section {row.get('section_number', '')}: "

        query_str = str(row.get("query") or "")
        pairs.append((query_str, doc_text))

    unmatched_count = len(unmatched_rows)
    print(f"Row matching status:", flush=True)
    print(f"  - Matched:   {matched_count:,} / {len(df):,} rows ({matched_count / len(df) * 100:.2f}%)", flush=True)
    print(f"  - Unmatched: {unmatched_count} / {len(df):,} rows ({unmatched_count / len(df) * 100:.2f}%)", flush=True)
    if unmatched_count > 0:
        print(f"  - Unmatched details (first 5): {unmatched_rows[:5]}", flush=True)

    print(f"\nLoading CrossEncoder model: {model_name}...", flush=True)
    model = CrossEncoder(model_name)

    print(f"Computing cross-encoder scores (batch_size={batch_size})...", flush=True)
    t0 = time.time()
    scores = model.predict(pairs, batch_size=batch_size, show_progress_bar=True)
    elapsed = time.time() - t0
    print(f"Computed {len(scores):,} scores in {elapsed:.2f}s ({len(scores)/elapsed:.1f} pairs/sec).", flush=True)

    df["cross_encoder_score"] = scores

    # Compute rank of candidate among that query's candidates (1 = highest score, 10 = lowest)
    df["cross_encoder_rank"] = (
        df.groupby("query", sort=False)["cross_encoder_score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    return df, unmatched_count


def load_or_generate_dataset(recompute=False):
    """
    Loads dataset with reranker features from CSV if available, or computes and saves it.
    """
    if os.path.exists(RERANKER_CSV_PATH) and not recompute:
        print(f"Loading existing data with reranker features from {RERANKER_CSV_PATH}...", flush=True)
        df = pd.read_csv(RERANKER_CSV_PATH)
        # Ensure gap_to_next is present
        if "gap_to_next" not in df.columns:
            df["gap_to_next"] = df.groupby("query", sort=False)["hybrid_score"].diff(-1).fillna(0.0)
        # Verify columns
        if "cross_encoder_score" in df.columns and "cross_encoder_rank" in df.columns:
            print(f"Loaded {len(df):,} rows with cross_encoder_score and cross_encoder_rank.", flush=True)
            return df

    print(f"Generating reranker features from {CLEAN_DATA_PATH}...", flush=True)
    df = pd.read_csv(CLEAN_DATA_PATH)

    # Ensure gap_to_next is computed exactly as in fair_comparison.py
    if "gap_to_next" not in df.columns:
        df["gap_to_next"] = df.groupby("query", sort=False)["hybrid_score"].diff(-1).fillna(0.0)

    kb_map = load_knowledge_base(KB_PATH)
    df, unmatched_count = compute_cross_encoder_features(df, kb_map)

    # Save to CSV so it never needs recomputing
    os.makedirs(os.path.dirname(RERANKER_CSV_PATH), exist_ok=True)
    df.to_csv(RERANKER_CSV_PATH, index=False)
    print(f"Saved dataset with reranker features to {RERANKER_CSV_PATH} ({os.path.getsize(RERANKER_CSV_PATH):,} bytes).", flush=True)

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


def run_evaluation(df):
    """
    Runs 5-fold GroupKFold CV comparing:
    (a) Current 10 features (Model B baseline from fair_comparison.py)
    (b) Current 10 features + cross_encoder_score + cross_encoder_rank
    """
    prod_826_queries = get_production_queries()
    all_queries = set(df["query"])
    non_826_queries = all_queries - prod_826_queries

    print(f"\nDataset Statistics:")
    print(f"  - Total queries:  {len(all_queries):,} ({len(df):,} candidate rows)")
    print(f"  - Prod queries:   {len(prod_826_queries):,} (Batches 1+2)")
    print(f"  - Unseen queries: {len(non_826_queries):,} ({len(non_826_queries) * 10:,} rows)")

    features_10 = [
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

    features_12 = features_10 + [
        "cross_encoder_score",
        "cross_encoder_rank",
    ]

    gkf = GroupKFold(n_splits=5)

    # Accumulators for metrics across folds
    # Full test set
    full_metrics = {
        "10_features": {"f1": [], "precision": [], "recall": [], "pr_auc": [], "bns_f1": []},
        "12_features": {"f1": [], "precision": [], "recall": [], "pr_auc": [], "bns_f1": []},
    }

    # Unseen queries subset
    unseen_metrics = {
        "10_features": {"f1": [], "precision": [], "recall": [], "pr_auc": [], "bns_f1": []},
        "12_features": {"f1": [], "precision": [], "recall": [], "pr_auc": [], "bns_f1": []},
    }

    # Per-act F1 accumulators across folds
    all_acts = sorted([a for a in df["act_name"].unique() if a != "act_name"])
    per_act_full = {
        act: {"10_features": [], "12_features": []} for act in all_acts
    }
    per_act_unseen = {
        act: {"10_features": [], "12_features": []} for act in all_acts
    }

    print("\nRunning 5-Fold GroupKFold Cross-Validation...", flush=True)

    for fold, (train_idx, test_idx) in enumerate(gkf.split(df, groups=df["query"]), start=1):
        train_df = df.iloc[train_idx]
        test_df = df.iloc[test_idx]
        test_unseen = test_df[test_df["query"].isin(non_826_queries)]

        # --- Train Model A (10 features) ---
        rf_10 = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_10.fit(train_df[features_10], train_df["is_relevant"])

        # --- Train Model B (12 features: + cross_encoder_score + cross_encoder_rank) ---
        rf_12 = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_12.fit(train_df[features_12], train_df["is_relevant"])

        models = [
            ("10_features", rf_10, features_10),
            ("12_features", rf_12, features_12),
        ]

        for m_name, model, feat_list in models:
            # 1. Full test set evaluation
            yp_full = model.predict(test_df[feat_list])
            yprob_full = model.predict_proba(test_df[feat_list])[:, 1]

            f1_f = f1_score(test_df["is_relevant"], yp_full, zero_division=0)
            prec_f = precision_score(test_df["is_relevant"], yp_full, zero_division=0)
            rec_f = recall_score(test_df["is_relevant"], yp_full, zero_division=0)
            prauc_f = average_precision_score(test_df["is_relevant"], yprob_full)

            # BNS subset on full test set
            bns_mask_full = test_df["act_name"] == BNS_ACT_NAME
            if bns_mask_full.sum() > 0:
                bns_f1_f = f1_score(test_df.loc[bns_mask_full, "is_relevant"], yp_full[bns_mask_full], zero_division=0)
            else:
                bns_f1_f = 0.0

            full_metrics[m_name]["f1"].append(f1_f)
            full_metrics[m_name]["precision"].append(prec_f)
            full_metrics[m_name]["recall"].append(rec_f)
            full_metrics[m_name]["pr_auc"].append(prauc_f)
            full_metrics[m_name]["bns_f1"].append(bns_f1_f)

            # Per-act F1 on full test set
            for act in all_acts:
                act_mask = test_df["act_name"] == act
                if act_mask.sum() > 0 and (test_df.loc[act_mask, "is_relevant"] == 1).sum() > 0:
                    act_f1 = f1_score(test_df.loc[act_mask, "is_relevant"], yp_full[act_mask], zero_division=0)
                    per_act_full[act][m_name].append(act_f1)

            # 2. Unseen test set evaluation
            yp_unseen = model.predict(test_unseen[feat_list])
            yprob_unseen = model.predict_proba(test_unseen[feat_list])[:, 1]

            f1_u = f1_score(test_unseen["is_relevant"], yp_unseen, zero_division=0)
            prec_u = precision_score(test_unseen["is_relevant"], yp_unseen, zero_division=0)
            rec_u = recall_score(test_unseen["is_relevant"], yp_unseen, zero_division=0)
            prauc_u = average_precision_score(test_unseen["is_relevant"], yprob_unseen)

            # BNS subset on unseen test set
            bns_mask_unseen = test_unseen["act_name"] == BNS_ACT_NAME
            if bns_mask_unseen.sum() > 0:
                bns_f1_u = f1_score(test_unseen.loc[bns_mask_unseen, "is_relevant"], yp_unseen[bns_mask_unseen], zero_division=0)
            else:
                bns_f1_u = 0.0

            unseen_metrics[m_name]["f1"].append(f1_u)
            unseen_metrics[m_name]["precision"].append(prec_u)
            unseen_metrics[m_name]["recall"].append(rec_u)
            unseen_metrics[m_name]["pr_auc"].append(prauc_u)
            unseen_metrics[m_name]["bns_f1"].append(bns_f1_u)

            # Per-act F1 on unseen test set
            for act in all_acts:
                act_mask = test_unseen["act_name"] == act
                if act_mask.sum() > 0 and (test_unseen.loc[act_mask, "is_relevant"] == 1).sum() > 0:
                    act_f1 = f1_score(test_unseen.loc[act_mask, "is_relevant"], yp_unseen[act_mask], zero_division=0)
                    per_act_unseen[act][m_name].append(act_f1)

        print(f"  Fold {fold}/5 complete (Full F1: 10f={full_metrics['10_features']['f1'][-1]:.4f}, 12f={full_metrics['12_features']['f1'][-1]:.4f} | Unseen F1: 10f={unseen_metrics['10_features']['f1'][-1]:.4f}, 12f={unseen_metrics['12_features']['f1'][-1]:.4f})", flush=True)

    # --- Print Summary Results Table ---
    print("\n" + "=" * 135)
    print(f"{'CLASSIFIER WITH RERANKER FEATURES: 5-FOLD GROUPKFOLD COMPARISON':^135}")
    print("=" * 135)
    header = f"{'Evaluation Subset':<32} {'Feature Set':<32} {'F1 (Class 1)':<18} {'Precision':<18} {'Recall':<18} {'PR-AUC':<18} {'BNS F1':<18}"
    print(header)
    print("-" * 135)

    # Full test set rows
    m10_f = full_metrics["10_features"]
    m12_f = full_metrics["12_features"]
    print(f"{'Full Test Set (5-Fold CV)':<32} {'Current 10 Features (Baseline)':<32} {fmt(m10_f['f1']):<18} {fmt(m10_f['precision']):<18} {fmt(m10_f['recall']):<18} {fmt(m10_f['pr_auc']):<18} {fmt(m10_f['bns_f1']):<18}")
    print(f"{'Full Test Set (5-Fold CV)':<32} {'10 Features + Cross-Encoder':<32} {fmt(m12_f['f1']):<18} {fmt(m12_f['precision']):<18} {fmt(m12_f['recall']):<18} {fmt(m12_f['pr_auc']):<18} {fmt(m12_f['bns_f1']):<18}")
    print("-" * 135)

    # Unseen subset rows
    m10_u = unseen_metrics["10_features"]
    m12_u = unseen_metrics["12_features"]
    print(f"{'Unseen Queries (Not in B1+B2)':<32} {'Current 10 Features (Baseline)':<32} {fmt(m10_u['f1']):<18} {fmt(m10_u['precision']):<18} {fmt(m10_u['recall']):<18} {fmt(m10_u['pr_auc']):<18} {fmt(m10_u['bns_f1']):<18}")
    print(f"{'Unseen Queries (Not in B1+B2)':<32} {'10 Features + Cross-Encoder':<32} {fmt(m12_u['f1']):<18} {fmt(m12_u['precision']):<18} {fmt(m12_u['recall']):<18} {fmt(m12_u['pr_auc']):<18} {fmt(m12_u['bns_f1']):<18}")
    print("=" * 135)

    # Baseline verification check against fair_comparison.py
    f1_10_full_mean = np.mean(m10_f["f1"])
    f1_10_unseen_mean = np.mean(m10_u["f1"])
    print("\nBaseline Reproduction Verification:")
    print(f"  - Full Set F1:   Expected 0.6655 | Actual {f1_10_full_mean:.4f} -> {'MATCH' if abs(f1_10_full_mean - 0.6655) < 0.0005 else 'MISMATCH'}")
    print(f"  - Unseen Set F1: Expected 0.6037 | Actual {f1_10_unseen_mean:.4f} -> {'MATCH' if abs(f1_10_unseen_mean - 0.6037) < 0.0005 else 'MISMATCH'}")

    # Feature Importance of Model with Cross-Encoder (trained on full dataset for inspection)
    print("\nFeature Importances (Model B + Reranker features trained on all data):")
    final_rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    final_rf.fit(df[features_12], df["is_relevant"])
    importances = list(zip(features_12, final_rf.feature_importances_))
    importances.sort(key=lambda x: x[1], reverse=True)
    for rank, (feat, imp) in enumerate(importances, start=1):
        marker = " <-- RERANKER FEATURE" if "cross_encoder" in feat else ""
        print(f"  {rank:2d}. {feat:<25}: {imp:.4f}{marker}")

    # --- Per-Act F1 Breakdown Table ---
    print("\n" + "=" * 115)
    print(f"{'PER-ACT F1 BREAKDOWN (FULL TEST SET & UNSEEN SUBSET)':^115}")
    print("=" * 115)
    act_header = f"{'Act Name':<52} {'Full 10-Feat':<15} {'Full 12-Feat':<15} {'Delta (Full)':<13} {'Unseen 12-Feat':<15}"
    print(act_header)
    print("-" * 115)

    for act in all_acts:
        f10_list = per_act_full[act]["10_features"]
        f12_list = per_act_full[act]["12_features"]
        u12_list = per_act_unseen[act]["12_features"]

        f10_mean = np.mean(f10_list) if len(f10_list) > 0 else 0.0
        f12_mean = np.mean(f12_list) if len(f12_list) > 0 else 0.0
        u12_mean = np.mean(u12_list) if len(u12_list) > 0 else 0.0
        delta = f12_mean - f10_mean

        delta_str = f"{delta:+.4f}"
        bns_tag = " <-- BNS" if act == BNS_ACT_NAME else ""
        print(f"{act:<52} {f10_mean:<15.4f} {f12_mean:<15.4f} {delta_str:<13} {u12_mean:<15.4f}{bns_tag}")

    print("=" * 115)
    print("\nDone. Note: No .pkl models were saved or written to disk.")


def main():
    parser = argparse.ArgumentParser(description="Evaluate relevance classifier with cross-encoder reranker features.")
    parser.add_argument("--recompute", action="store_true", help="Recompute cross-encoder scores even if cached CSV exists.")
    args = parser.parse_args()

    df = load_or_generate_dataset(recompute=args.recompute)
    run_evaluation(df)


if __name__ == "__main__":
    main()
