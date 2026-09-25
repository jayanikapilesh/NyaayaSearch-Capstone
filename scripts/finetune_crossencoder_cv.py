"""
Google Colab Execution Instructions:
===================================
1. Enable GPU:
   In Google Colab, go to Runtime -> Change runtime type -> Hardware accelerator -> GPU (T4 or A100).

2. Upload required files (or clone the repository):
   Ensure the following input files are available:
   - data/eval/classifier_training_data_with_reranker.csv
   - Legal_Knowledge_Base_combined.xlsx
   - data/training_pairs.jsonl
   - data/training_pairs_batch2.jsonl
   - scripts/finetune_crossencoder_cv.py

   If cloning via git:
   !git clone <your_repo_url>
   %cd NyaayaSearch-Capstone

3. Install required packages:
   !pip install -q sentence-transformers pandas openpyxl scikit-learn torch

4. Run the script:
   !python scripts/finetune_crossencoder_cv.py
"""

import os
import sys
import json
import time
import random
import argparse
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score
from sentence_transformers import CrossEncoder, InputExample

# ---------------------------------------------------------------------------
# Path Resolutions (Supports running from repo root or /content in Colab)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Resolve root if executed directly in /content or subfolder
if not os.path.exists(os.path.join(ROOT_DIR, "Legal_Knowledge_Base_combined.xlsx")):
    if os.path.exists("Legal_Knowledge_Base_combined.xlsx"):
        ROOT_DIR = os.path.abspath(".")
    elif os.path.exists("/content/Legal_Knowledge_Base_combined.xlsx"):
        ROOT_DIR = "/content"

DATA_DIR = os.path.join(ROOT_DIR, "data")
EVAL_DIR = os.path.join(DATA_DIR, "eval")

INPUT_CSV_PATH = os.path.join(EVAL_DIR, "classifier_training_data_with_reranker.csv")
KB_PATH = os.path.join(ROOT_DIR, "Legal_Knowledge_Base_combined.xlsx")
OOF_CSV_PATH = os.path.join(EVAL_DIR, "crossencoder_oof_predictions.csv")

BATCH_FILES = [
    os.path.join(DATA_DIR, "training_pairs.jsonl"),
    os.path.join(DATA_DIR, "training_pairs_batch2.jsonl"),
]

# Baseline reference metrics (from Random Forest with 12 features on clean data)
RF_BASELINE_FULL_F1 = 0.7601
RF_BASELINE_UNSEEN_F1 = 0.7074


def set_seed(seed=42):
    """Sets fixed random seed across all libraries for exact reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_knowledge_base(kb_path):
    """
    Loads Legal_Knowledge_Base_combined.xlsx and builds a lookup mapping
    by (normalized act_name, normalized section_number).
    """
    print(f"Loading Legal Knowledge Base from {kb_path}...", flush=True)
    if not os.path.exists(kb_path):
        raise FileNotFoundError(f"Knowledge Base file not found at {kb_path}")

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
    print(f"Loaded {len(kb_map):,} unique act+section entries from Knowledge Base.", flush=True)
    return kb_map


def build_document_text(row, kb_map):
    """
    Constructs section document text using the exact reranker format from search_core.py:
    f"{act_name}, Section {section_number}: {section_title}. {legal_text[:400]}"
    """
    act_key = str(row.get("act_name") or "").strip().lower()
    sec_key = str(row.get("section_number") or "").strip().lower()
    lookup_key = (act_key, sec_key)

    if lookup_key in kb_map:
        rec = kb_map[lookup_key]
        act_str = rec["act_name"]
        sec_str = rec["section_number"]
        title_str = rec["section_title"]
        text_str = rec["legal_text"][:400]
        return f"{act_str}, Section {sec_str}: {title_str}. {text_str}"
    else:
        return f"{row.get('act_name', '')}, Section {row.get('section_number', '')}: "


def get_production_queries():
    """Identifies the 826 production queries from Batches 1+2 to isolate unseen queries."""
    prod_queries = set()
    for bpath in BATCH_FILES:
        if os.path.exists(bpath):
            with open(bpath, "r", encoding="utf-8") as fp:
                for line in fp:
                    if line.strip():
                        prod_queries.add(json.loads(line)["query"])
        else:
            print(f"Warning: Batch file {bpath} not found.", flush=True)
    return prod_queries


def fmt(arr):
    """Formats array mean and standard deviation."""
    return f"{np.mean(arr):.4f} +/- {np.std(arr):.4f}"


def run_cross_encoder_cv(args):
    """
    Main 5-Fold GroupKFold Cross-Validation for Fine-Tuning CrossEncoder on GPU.
    """
    set_seed(args.seed)

    # 1. Device check
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("=" * 80)
    print("      NYAAYASEARCH: CROSS-ENCODER 5-FOLD CV FINE-TUNING (COLAB GPU)")
    print("=" * 80)
    print(f"PyTorch Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    if device == "cpu":
        print("WARNING: GPU is not detected. Training on CPU will be significantly slower.")
        print("Please enable GPU under Runtime -> Change runtime type -> Hardware accelerator.")

    # 2. Load dataset and drop corrupt header rows
    if not os.path.exists(INPUT_CSV_PATH):
        raise FileNotFoundError(f"Input training data not found at {INPUT_CSV_PATH}")

    print(f"\nLoading training data from {INPUT_CSV_PATH}...", flush=True)
    df_raw = pd.read_csv(INPUT_CSV_PATH)
    initial_len = len(df_raw)

    # Drop rows where act_name == "act_name"
    junk_mask = df_raw["act_name"] == "act_name"
    df = df_raw[~junk_mask].copy().reset_index(drop=True)
    dropped_count = junk_mask.sum()
    print(f"Dropped {dropped_count} junk rows where act_name == 'act_name'.")
    print(f"Clean training dataset size: {len(df):,} rows ({len(df)/initial_len*100:.2f}% retained).")

    # 3. Load Knowledge Base and build document text
    kb_map = load_knowledge_base(KB_PATH)
    print("Building document text for all candidate rows...", flush=True)
    df["doc_text"] = [build_document_text(row, kb_map) for _, row in df.iterrows()]

    # 4. Partition production vs unseen queries
    prod_826_queries = get_production_queries()
    all_queries = set(df["query"])
    non_826_queries = all_queries - prod_826_queries
    print(f"\nQuery Partitioning:")
    print(f"  - Total unique queries:  {len(all_queries):,} ({len(df):,} candidate rows)")
    print(f"  - Production queries:    {len(prod_826_queries):,} (Batches 1+2)")
    print(f"  - Unseen queries subset: {len(non_826_queries):,} ({len(non_826_queries) * 10:,} rows)")

    # 5. 5-Fold GroupKFold by query
    gkf = GroupKFold(n_splits=args.num_folds)
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=args.seed)

    # Metrics accumulators
    full_metrics = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
    unseen_metrics = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
    chosen_thresholds = []

    oof_dfs = []

    print("\nStarting 5-Fold GroupKFold Fine-Tuning & Evaluation...", flush=True)
    print("-" * 80)

    for fold, (train_idx, test_idx) in enumerate(gkf.split(df, groups=df["query"]), start=1):
        fold_start_time = time.time()
        print(f"\n>>> [Fold {fold}/{args.num_folds}] Starting...", flush=True)

        outer_train_df = df.iloc[train_idx].copy()
        outer_test_df = df.iloc[test_idx].copy()
        outer_test_unseen = outer_test_df[outer_test_df["query"].isin(non_826_queries)]

        # --- Step 1: Split outer training fold's queries 80/20 (grouped by query) ---
        inner_train_idx, inner_val_idx = next(gss.split(outer_train_df, groups=outer_train_df["query"]))
        inner_train = outer_train_df.iloc[inner_train_idx]
        inner_val = outer_train_df.iloc[inner_val_idx]

        print(
            f"  [Fold {fold}] Outer Train: {len(outer_train_df):,} rows | "
            f"Inner Train (80%): {len(inner_train):,} rows ({inner_train['query'].nunique():,} queries) | "
            f"Inner Val (20%): {len(inner_val):,} rows ({inner_val['query'].nunique():,} queries)",
            flush=True,
        )

        # Prepare PyTorch InputExamples for 80% inner training
        train_samples = [
            InputExample(texts=[row["query"], row["doc_text"]], label=float(row["is_relevant"]))
            for _, row in inner_train.iterrows()
        ]
        train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=args.batch_size)
        total_steps = len(train_dataloader) * args.epochs
        warmup_steps = int(total_steps * args.warmup_ratio)

        # --- Step 2: Fine-tune cross-encoder on the 80% only ---
        set_seed(args.seed + fold)
        print(f"  [Fold {fold}] Initializing {args.model_name}...", flush=True)
        model = CrossEncoder(
            args.model_name,
            num_labels=1,
            max_length=512,
            device=device,
        )

        print(
            f"  [Fold {fold}] Training 1 epoch (batch_size={args.batch_size}, lr={args.lr}, warmup_steps={warmup_steps})...",
            flush=True,
        )
        t_train_0 = time.time()
        model.fit(
            train_dataloader=train_dataloader,
            epochs=args.epochs,
            loss_fct=nn.BCEWithLogitsLoss(),
            optimizer_params={"lr": args.lr},
            warmup_steps=warmup_steps,
            use_amp=(device == "cuda"),
            show_progress_bar=True,
        )
        train_duration = time.time() - t_train_0
        print(f"  [Fold {fold}] Fine-tuning completed in {train_duration:.1f}s.", flush=True)

        # --- Step 3: Pick the threshold that maximizes F1 on the 20% validation split ---
        print(f"  [Fold {fold}] Predicting on 20% inner validation holdout ({len(inner_val):,} rows)...", flush=True)
        val_pairs = list(zip(inner_val["query"], inner_val["doc_text"]))
        val_logits = model.predict(val_pairs, batch_size=args.eval_batch_size, show_progress_bar=False)
        val_probs = 1.0 / (1.0 + np.exp(-val_logits))
        val_y = inner_val["is_relevant"].values

        # Search threshold grid [0.10, 0.90] with step 0.01
        threshold_grid = np.arange(0.10, 0.91, 0.01)
        best_t = 0.5
        best_val_f1 = -1.0
        for t in threshold_grid:
            f1_t = f1_score(val_y, (val_probs >= t).astype(int), zero_division=0)
            if f1_t > best_val_f1:
                best_val_f1 = f1_t
                best_t = float(t)

        chosen_thresholds.append(best_t)
        print(f"  [Fold {fold}] Optimal inner-val threshold T* = {best_t:.2f} (Inner Val F1 = {best_val_f1:.4f})", flush=True)

        # --- Step 4: Score the outer test fold and apply that threshold ---
        print(f"  [Fold {fold}] Scoring outer test fold ({len(outer_test_df):,} rows)...", flush=True)
        test_pairs = list(zip(outer_test_df["query"], outer_test_df["doc_text"]))
        test_logits = model.predict(test_pairs, batch_size=args.eval_batch_size, show_progress_bar=False)
        test_probs = 1.0 / (1.0 + np.exp(-test_logits))
        test_y = outer_test_df["is_relevant"].values

        # Apply the chosen inner-val threshold T* to outer test fold
        test_preds = (test_probs >= best_t).astype(int)

        # Full outer test fold metrics
        fold_f1_full = f1_score(test_y, test_preds, zero_division=0)
        fold_prec_full = precision_score(test_y, test_preds, zero_division=0)
        fold_rec_full = recall_score(test_y, test_preds, zero_division=0)
        fold_prauc_full = average_precision_score(test_y, test_probs)

        full_metrics["f1"].append(fold_f1_full)
        full_metrics["precision"].append(fold_prec_full)
        full_metrics["recall"].append(fold_rec_full)
        full_metrics["pr_auc"].append(fold_prauc_full)

        # Unseen queries subset metrics
        unseen_idx_mask = outer_test_df["query"].isin(non_826_queries).values
        y_unseen = test_y[unseen_idx_mask]
        preds_unseen = test_preds[unseen_idx_mask]
        probs_unseen = test_probs[unseen_idx_mask]

        fold_f1_uns = f1_score(y_unseen, preds_unseen, zero_division=0)
        fold_prec_uns = precision_score(y_unseen, preds_unseen, zero_division=0)
        fold_rec_uns = recall_score(y_unseen, preds_unseen, zero_division=0)
        fold_prauc_uns = average_precision_score(y_unseen, probs_unseen)

        unseen_metrics["f1"].append(fold_f1_uns)
        unseen_metrics["precision"].append(fold_prec_uns)
        unseen_metrics["recall"].append(fold_rec_uns)
        unseen_metrics["pr_auc"].append(fold_prauc_uns)

        # Record Out-of-Fold predictions with fold IDs
        oof_slice = outer_test_df[["query", "act_name", "section_number", "is_relevant"]].copy()
        oof_slice["fold"] = fold
        oof_slice["oof_raw_logit"] = test_logits
        oof_slice["oof_prob"] = test_probs
        oof_slice["threshold_applied"] = best_t
        oof_slice["pred_relevant"] = test_preds
        oof_dfs.append(oof_slice)

        fold_elapsed = time.time() - fold_start_time
        print(
            f"  [Fold {fold} Result] Full F1: {fold_f1_full:.4f} (P={fold_prec_full:.4f}, R={fold_rec_full:.4f}, PR-AUC={fold_prauc_full:.4f}) | "
            f"Unseen F1: {fold_f1_uns:.4f} | Elapsed: {fold_elapsed:.1f}s",
            flush=True,
        )

    # 6. Save Out-of-Fold predictions to CSV
    oof_all_df = pd.concat(oof_dfs, ignore_index=True)
    os.makedirs(os.path.dirname(OOF_CSV_PATH), exist_ok=True)
    oof_all_df.to_csv(OOF_CSV_PATH, index=False)
    print(f"\nSaved out-of-fold predictions to {OOF_CSV_PATH} ({len(oof_all_df):,} rows).", flush=True)

    # 7. Print Final Comparison Table
    print("\n" + "=" * 120)
    print(f"{'CROSS-ENCODER FINE-TUNING CV vs. RANDOM FOREST BASELINE':^120}")
    print("=" * 120)
    print(f"Optimal decision thresholds chosen per fold: {[round(t, 2) for t in chosen_thresholds]} (mean: {np.mean(chosen_thresholds):.2f})")
    print("-" * 120)
    header = f"{'Evaluation Subset':<32} {'Model':<35} {'F1 (Class 1)':<18} {'Precision':<18} {'Recall':<18} {'PR-AUC':<18}"
    print(header)
    print("-" * 120)

    # Full Test Set Rows
    rf_full_str = f"{RF_BASELINE_FULL_F1:.4f} (baseline)"
    print(f"{'Full Test Set (5-Fold CV)':<32} {'Random Forest (12 Features Best)':<35} {rf_full_str:<18} {'0.7450 +/- 0.0234':<18} {'0.7759 +/- 0.0140':<18} {'0.8100 +/- 0.0267':<18}")
    print(f"{'Full Test Set (5-Fold CV)':<32} {'Fine-Tuned Cross-Encoder (L-6)':<35} {fmt(full_metrics['f1']):<18} {fmt(full_metrics['precision']):<18} {fmt(full_metrics['recall']):<18} {fmt(full_metrics['pr_auc']):<18}")
    print("-" * 120)

    # Unseen Subset Rows
    rf_uns_str = f"{RF_BASELINE_UNSEEN_F1:.4f} (baseline)"
    print(f"{'Unseen Queries (Not in B1+B2)':<32} {'Random Forest (12 Features Best)':<35} {rf_uns_str:<18} {'0.6940 +/- 0.0361':<18} {'0.7214 +/- 0.0228':<18} {'0.7536 +/- 0.0323':<18}")
    print(f"{'Unseen Queries (Not in B1+B2)':<32} {'Fine-Tuned Cross-Encoder (L-6)':<35} {fmt(unseen_metrics['f1']):<18} {fmt(unseen_metrics['precision']):<18} {fmt(unseen_metrics['recall']):<18} {fmt(unseen_metrics['pr_auc']):<18}")
    print("=" * 120)

    delta_full = np.mean(full_metrics["f1"]) - RF_BASELINE_FULL_F1
    delta_unseen = np.mean(unseen_metrics["f1"]) - RF_BASELINE_UNSEEN_F1
    print("\nSummary Comparison:")
    print(f"  - Full Test Set F1:   Fine-Tuned Cross-Encoder {np.mean(full_metrics['f1']):.4f} vs RF Best {RF_BASELINE_FULL_F1:.4f} ({delta_full:+.4f})")
    print(f"  - Unseen Queries F1: Fine-Tuned Cross-Encoder {np.mean(unseen_metrics['f1']):.4f} vs RF Best {RF_BASELINE_UNSEEN_F1:.4f} ({delta_unseen:+.4f})")
    print("\nEvaluation complete. Out-of-fold predictions ready for inspection.")


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Cross-Encoder with 5-Fold GroupKFold on GPU (Google Colab).")
    parser.add_argument("--model_name", type=str, default="cross-encoder/ms-marco-MiniLM-L-6-v2", help="Pretrained cross-encoder model")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs per fold (default: 1)")
    parser.add_argument("--batch_size", type=int, default=32, help="Training batch size (default: 32)")
    parser.add_argument("--eval_batch_size", type=int, default=64, help="Inference evaluation batch size (default: 64)")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate (default: 2e-5)")
    parser.add_argument("--warmup_ratio", type=float, default=0.10, help="Linear warmup ratio (default: 0.10 = 10%)")
    parser.add_argument("--num_folds", type=int, default=5, help="Number of GroupKFold splits (default: 5)")
    parser.add_argument("--seed", type=int, default=42, help="Fixed random seed (default: 42)")
    args = parser.parse_args()

    run_cross_encoder_cv(args)


if __name__ == "__main__":
    main()
