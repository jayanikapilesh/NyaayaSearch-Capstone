"""
Google Colab Execution Instructions:
===================================
1. Enable GPU:
   In Google Colab, go to Runtime -> Change runtime type -> Hardware accelerator -> GPU (T4, V100, or A100).

2. Upload required files (or clone the repository):
   Ensure the following input files are available:
   - data/eval/classifier_training_data_with_reranker.csv
   - Legal_Knowledge_Base_combined.xlsx
   - data/training_pairs.jsonl
   - data/training_pairs_batch2.jsonl
   - scripts/stack_finetuned_rf.py

   If cloning via git:
   !git clone <your_repo_url>
   %cd NyaayaSearch-Capstone

3. Install required packages:
   !pip install -q transformers pandas openpyxl scikit-learn torch accelerate

4. Run the script:
   !python scripts/stack_finetuned_rf.py
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
from torch.utils.data import Dataset, DataLoader

from sklearn.model_selection import GroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup,
)

# ---------------------------------------------------------------------------
# Path Resolutions (Supports running from repo root or /content in Colab)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

if not os.path.exists(os.path.join(ROOT_DIR, "Legal_Knowledge_Base_combined.xlsx")):
    if os.path.exists("Legal_Knowledge_Base_combined.xlsx"):
        ROOT_DIR = os.path.abspath(".")
    elif os.path.exists("/content/Legal_Knowledge_Base_combined.xlsx"):
        ROOT_DIR = "/content"

DATA_DIR = os.path.join(ROOT_DIR, "data")
EVAL_DIR = os.path.join(DATA_DIR, "eval")

INPUT_CSV_PATH = os.path.join(EVAL_DIR, "classifier_training_data_with_reranker.csv")
KB_PATH = os.path.join(ROOT_DIR, "Legal_Knowledge_Base_combined.xlsx")
OUTPUT_CSV_PATH = os.path.join(EVAL_DIR, "stacked_finetuned_rf_predictions.csv")

BATCH_FILES = [
    os.path.join(DATA_DIR, "training_pairs.jsonl"),
    os.path.join(DATA_DIR, "training_pairs_batch2.jsonl"),
]

# Baseline reference metrics (Random Forest with 12 features on clean data)
RF_12_BASELINE_FULL_F1 = 0.7601
RF_12_BASELINE_UNSEEN_F1 = 0.7074


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


# ---------------------------------------------------------------------------
# PyTorch Dataset and Collate Function
# ---------------------------------------------------------------------------
class QueryDocDataset(Dataset):
    """Dataset for query-document text pairs and optional binary labels."""
    def __init__(self, queries, doc_texts, labels=None):
        self.queries = list(queries)
        self.doc_texts = list(doc_texts)
        self.labels = [float(l) for l in labels] if labels is not None else None

    def __len__(self):
        return len(self.queries)

    def __getitem__(self, idx):
        item = {
            "query": self.queries[idx],
            "doc_text": self.doc_texts[idx],
        }
        if self.labels is not None:
            item["label"] = self.labels[idx]
        return item


def make_collate_fn(tokenizer, max_length=256, has_labels=True):
    """Factory creating tokenizer collate function for DataLoader batches."""
    def collate_fn(batch):
        queries = [item["query"] for item in batch]
        doc_texts = [item["doc_text"] for item in batch]
        encoded = tokenizer(
            queries,
            doc_texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        if has_labels:
            encoded["labels"] = torch.tensor([item["label"] for item in batch], dtype=torch.float)
        return encoded
    return collate_fn


# ---------------------------------------------------------------------------
# Training Routine (Plain PyTorch Loop)
# ---------------------------------------------------------------------------
def train_cross_encoder(
    train_df,
    model_name,
    device,
    seed,
    batch_size=32,
    lr=2e-5,
    epochs=1,
    warmup_ratio=0.10,
    max_length=256,
    desc="Training",
):
    """
    Trains AutoModelForSequenceClassification for 1 epoch with BCEWithLogitsLoss,
    AdamW, linear warmup schedule, and fp16 autocast on GPU.
    """
    set_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1)
    model.to(device)

    train_dataset = QueryDocDataset(
        train_df["query"],
        train_df["doc_text"],
        labels=train_df["is_relevant"].values,
    )
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=make_collate_fn(tokenizer, max_length=max_length, has_labels=True),
    )

    total_steps = len(train_dataloader) * epochs
    warmup_steps = int(total_steps * warmup_ratio)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps,
    )
    loss_fct = nn.BCEWithLogitsLoss()
    scaler = torch.cuda.amp.GradScaler(enabled=(device == "cuda"))

    model.train()
    t0 = time.time()
    for epoch in range(epochs):
        for step, batch in enumerate(train_dataloader, start=1):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            with torch.cuda.amp.autocast(enabled=(device == "cuda")):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits.view(-1)
                loss = loss_fct(logits, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

    elapsed = time.time() - t0
    print(f"      [{desc}] Done 1 epoch ({len(train_df):,} samples) in {elapsed:.1f}s.", flush=True)
    return model, tokenizer


# ---------------------------------------------------------------------------
# Scoring Routine (Eval Mode + Sigmoid Probabilities)
# ---------------------------------------------------------------------------
def score_pairs(model, tokenizer, eval_df, device, batch_size=64, max_length=256):
    """
    Evaluates query-document pairs with AutoModelForSequenceClassification in eval mode.
    Returns sigmoid probabilities in [0, 1].
    """
    model.eval()
    dataset = QueryDocDataset(eval_df["query"], eval_df["doc_text"], labels=None)
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=make_collate_fn(tokenizer, max_length=max_length, has_labels=False),
    )

    all_probs = []
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            with torch.cuda.amp.autocast(enabled=(device == "cuda")):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits.view(-1)
                probs = torch.sigmoid(logits)

            all_probs.extend(probs.cpu().float().numpy().tolist())

    return np.array(all_probs)


# ---------------------------------------------------------------------------
# Main Stacked Model Cross-Validation
# ---------------------------------------------------------------------------
def run_stacked_rf_cv(args):
    """
    Executes the fully stacked Random Forest + Fine-Tuned Cross-Encoder evaluation:
    5 outer GroupKFold folds by query.
    For each outer fold k:
      1. Train cross-encoder on all outer training rows (folds != k) -> score fold k.
      2. Split outer training rows into 4 inner GroupKFold folds by query -> fine-tune on
         3 folds, score held-out 1 fold to populate training finetuned_score with zero leakage.
      3. Compute candidate finetuned_rank within each query.
      4. Train Random Forest (12 existing features + finetuned_score + finetuned_rank),
         predict outer fold k with threshold 0.5.
    """
    set_seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("=" * 85)
    print("  NYAAYASEARCH: STACKED FINE-TUNED CROSS-ENCODER + RANDOM FOREST (COLAB GPU)")
    print("=" * 85)
    print(f"PyTorch Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    if device == "cpu":
        print("WARNING: GPU is not detected. Training on CPU will be significantly slower.")
        print("Please enable GPU under Runtime -> Change runtime type -> Hardware accelerator.")

    # 1. Load clean data
    if not os.path.exists(INPUT_CSV_PATH):
        raise FileNotFoundError(f"Input training data not found at {INPUT_CSV_PATH}")

    print(f"\nLoading training data from {INPUT_CSV_PATH}...", flush=True)
    df_raw = pd.read_csv(INPUT_CSV_PATH)
    junk_mask = df_raw["act_name"] == "act_name"
    df = df_raw[~junk_mask].copy().reset_index(drop=True)
    print(f"Dropped {junk_mask.sum()} junk rows where act_name == 'act_name'.")
    print(f"Clean training dataset size: {len(df):,} rows.")

    # Ensure gap_to_next is present
    if "gap_to_next" not in df.columns:
        df["gap_to_next"] = df.groupby("query", sort=False)["hybrid_score"].diff(-1).fillna(0.0)

    # 2. Load Knowledge Base and build document text
    kb_map = load_knowledge_base(KB_PATH)
    print("Building document text for all candidate rows...", flush=True)
    df["doc_text"] = [build_document_text(row, kb_map) for _, row in df.iterrows()]

    # 3. Partition production vs unseen queries
    prod_826_queries = get_production_queries()
    all_queries = set(df["query"])
    non_826_queries = all_queries - prod_826_queries
    print(f"\nQuery Partitioning:")
    print(f"  - Total unique queries:  {len(all_queries):,} ({len(df):,} candidate rows)")
    print(f"  - Production queries:    {len(prod_826_queries):,} (Batches 1+2)")
    print(f"  - Unseen queries subset: {len(non_826_queries):,} ({len(non_826_queries) * 10:,} rows)")

    # 4. Feature sets
    features_12 = [
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

    features_stacked = features_12 + [
        "finetuned_score",
        "finetuned_rank",
    ]

    # 5. 5-Fold Outer GroupKFold
    outer_gkf = GroupKFold(n_splits=args.num_outer_folds)
    inner_gkf = GroupKFold(n_splits=args.num_inner_folds)

    # Metrics accumulators
    stacked_metrics_full = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
    stacked_metrics_uns = {"f1": [], "precision": [], "recall": [], "pr_auc": []}

    baseline_metrics_full = {"f1": [], "precision": [], "recall": [], "pr_auc": []}
    baseline_metrics_uns = {"f1": [], "precision": [], "recall": [], "pr_auc": []}

    oof_predictions_list = []

    print("\nStarting Stacked Model 5-Fold Cross-Validation...", flush=True)
    print("-" * 85)

    for outer_fold, (train_idx, test_idx) in enumerate(outer_gkf.split(df, groups=df["query"]), start=1):
        outer_t0 = time.time()
        print(f"\n>>> [Outer Fold {outer_fold}/{args.num_outer_folds}] Starting...", flush=True)

        outer_train_df = df.iloc[train_idx].copy().reset_index(drop=True)
        outer_test_df = df.iloc[test_idx].copy().reset_index(drop=True)
        outer_test_unseen_mask = outer_test_df["query"].isin(non_826_queries)

        print(
            f"  [Outer Fold {outer_fold}] Outer Train: {len(outer_train_df):,} rows ({outer_train_df['query'].nunique():,} queries) | "
            f"Outer Test: {len(outer_test_df):,} rows ({outer_test_df['query'].nunique():,} queries)",
            flush=True,
        )

        # -------------------------------------------------------------------
        # Step 1: Test-Fold Feature (Train cross-encoder on ALL outer train rows)
        # -------------------------------------------------------------------
        print(f"  [Outer Fold {outer_fold}] Training Cross-Encoder on ALL outer train rows to score test fold...", flush=True)
        outer_ce_model, outer_ce_tok = train_cross_encoder(
            train_df=outer_train_df,
            model_name=args.model_name,
            device=device,
            seed=args.seed + outer_fold * 100,
            batch_size=args.batch_size,
            lr=args.lr,
            epochs=args.epochs,
            warmup_ratio=args.warmup_ratio,
            max_length=args.max_length,
            desc=f"Outer Fold {outer_fold} Full CE",
        )

        print(f"  [Outer Fold {outer_fold}] Scoring outer test fold...", flush=True)
        outer_test_df["finetuned_score"] = score_pairs(
            model=outer_ce_model,
            tokenizer=outer_ce_tok,
            eval_df=outer_test_df,
            device=device,
            batch_size=args.eval_batch_size,
            max_length=args.max_length,
        )

        # Free GPU memory
        del outer_ce_model, outer_ce_tok
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # -------------------------------------------------------------------
        # Step 2: Training-Row Features (4 Inner GroupKFold folds on outer train)
        # -------------------------------------------------------------------
        print(f"  [Outer Fold {outer_fold}] Running 4-Fold Inner CV on outer train rows to generate training finetuned_score...", flush=True)
        outer_train_df["finetuned_score"] = np.nan

        for inner_fold, (in_tr_idx, in_val_idx) in enumerate(
            inner_gkf.split(outer_train_df, groups=outer_train_df["query"]), start=1
        ):
            inner_train = outer_train_df.iloc[in_tr_idx]
            inner_val = outer_train_df.iloc[in_val_idx]

            in_ce_model, in_ce_tok = train_cross_encoder(
                train_df=inner_train,
                model_name=args.model_name,
                device=device,
                seed=args.seed + outer_fold * 100 + inner_fold,
                batch_size=args.batch_size,
                lr=args.lr,
                epochs=args.epochs,
                warmup_ratio=args.warmup_ratio,
                max_length=args.max_length,
                desc=f"Outer {outer_fold} Inner {inner_fold}/4",
            )

            val_probs = score_pairs(
                model=in_ce_model,
                tokenizer=in_ce_tok,
                eval_df=inner_val,
                device=device,
                batch_size=args.eval_batch_size,
                max_length=args.max_length,
            )
            outer_train_df.loc[in_val_idx, "finetuned_score"] = val_probs

            del in_ce_model, in_ce_tok
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        assert not outer_train_df["finetuned_score"].isna().any(), "Error: NaN values found in outer train finetuned_score!"

        # -------------------------------------------------------------------
        # Step 3: Add finetuned_rank within each query's candidate set
        # -------------------------------------------------------------------
        outer_train_df["finetuned_rank"] = (
            outer_train_df.groupby("query", sort=False)["finetuned_score"]
            .rank(ascending=False, method="min")
            .astype(int)
        )
        outer_test_df["finetuned_rank"] = (
            outer_test_df.groupby("query", sort=False)["finetuned_score"]
            .rank(ascending=False, method="min")
            .astype(int)
        )

        # -------------------------------------------------------------------
        # Step 4: Train Random Forest Models
        # -------------------------------------------------------------------
        # (a) Baseline 12-feature Random Forest (for exact apples-to-apples comparison)
        rf_baseline = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_baseline.fit(outer_train_df[features_12], outer_train_df["is_relevant"])

        probs_base_full = rf_baseline.predict_proba(outer_test_df[features_12])[:, 1]
        preds_base_full = (probs_base_full >= 0.5).astype(int)

        y_full = outer_test_df["is_relevant"].values
        baseline_metrics_full["f1"].append(f1_score(y_full, preds_base_full, zero_division=0))
        baseline_metrics_full["precision"].append(precision_score(y_full, preds_base_full, zero_division=0))
        baseline_metrics_full["recall"].append(recall_score(y_full, preds_base_full, zero_division=0))
        baseline_metrics_full["pr_auc"].append(average_precision_score(y_full, probs_base_full))

        probs_base_uns = probs_base_full[outer_test_unseen_mask]
        preds_base_uns = preds_base_full[outer_test_unseen_mask]
        y_uns = y_full[outer_test_unseen_mask]
        baseline_metrics_uns["f1"].append(f1_score(y_uns, preds_base_uns, zero_division=0))
        baseline_metrics_uns["precision"].append(precision_score(y_uns, preds_base_uns, zero_division=0))
        baseline_metrics_uns["recall"].append(recall_score(y_uns, preds_base_uns, zero_division=0))
        baseline_metrics_uns["pr_auc"].append(average_precision_score(y_uns, probs_base_uns))

        # (b) Stacked Random Forest (12 Features + finetuned_score + finetuned_rank)
        print(f"  [Outer Fold {outer_fold}] Training Stacked Random Forest (14 features)...", flush=True)
        rf_stacked = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_stacked.fit(outer_train_df[features_stacked], outer_train_df["is_relevant"])

        probs_stacked_full = rf_stacked.predict_proba(outer_test_df[features_stacked])[:, 1]
        preds_stacked_full = (probs_stacked_full >= 0.5).astype(int)

        stacked_metrics_full["f1"].append(f1_score(y_full, preds_stacked_full, zero_division=0))
        stacked_metrics_full["precision"].append(precision_score(y_full, preds_stacked_full, zero_division=0))
        stacked_metrics_full["recall"].append(recall_score(y_full, preds_stacked_full, zero_division=0))
        stacked_metrics_full["pr_auc"].append(average_precision_score(y_full, probs_stacked_full))

        probs_stacked_uns = probs_stacked_full[outer_test_unseen_mask]
        preds_stacked_uns = preds_stacked_full[outer_test_unseen_mask]
        stacked_metrics_uns["f1"].append(f1_score(y_uns, preds_stacked_uns, zero_division=0))
        stacked_metrics_uns["precision"].append(precision_score(y_uns, preds_stacked_uns, zero_division=0))
        stacked_metrics_uns["recall"].append(recall_score(y_uns, preds_stacked_uns, zero_division=0))
        stacked_metrics_uns["pr_auc"].append(average_precision_score(y_uns, probs_stacked_uns))

        # Save slice for OOF predictions file
        oof_slice = outer_test_df[["query", "act_name", "section_number", "is_relevant"]].copy()
        oof_slice["fold"] = outer_fold
        oof_slice["finetuned_score"] = outer_test_df["finetuned_score"]
        oof_slice["finetuned_rank"] = outer_test_df["finetuned_rank"]
        oof_slice["stacked_rf_prob"] = probs_stacked_full
        oof_slice["stacked_rf_pred"] = preds_stacked_full
        oof_predictions_list.append(oof_slice)

        outer_elapsed = time.time() - outer_t0
        print(
            f"  [Outer Fold {outer_fold} Result] "
            f"Full F1: 12f={baseline_metrics_full['f1'][-1]:.4f} -> Stacked={stacked_metrics_full['f1'][-1]:.4f} | "
            f"Unseen F1: 12f={baseline_metrics_uns['f1'][-1]:.4f} -> Stacked={stacked_metrics_uns['f1'][-1]:.4f} | "
            f"Elapsed: {outer_elapsed:.1f}s",
            flush=True,
        )

    # 6. Save Out-of-Fold Predictions
    oof_df = pd.concat(oof_predictions_list, ignore_index=True)
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    oof_df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"\nSaved stacked model predictions to {OUTPUT_CSV_PATH} ({len(oof_df):,} rows).", flush=True)

    # 7. Print Final Comparison Table
    print("\n" + "=" * 125)
    print(f"{'STACKED FINE-TUNED CROSS-ENCODER + RANDOM FOREST vs. 12-FEATURE BASELINE':^125}")
    print("=" * 125)
    header = f"{'Evaluation Subset':<32} {'Classifier Architecture':<36} {'F1 (Class 1)':<18} {'Precision':<18} {'Recall':<18} {'PR-AUC':<18}"
    print(header)
    print("-" * 125)

    # Full Test Set Rows
    print(f"{'Full Test Set (5-Fold CV)':<32} {'Random Forest (12 Features Baseline)':<36} {fmt(baseline_metrics_full['f1']):<18} {fmt(baseline_metrics_full['precision']):<18} {fmt(baseline_metrics_full['recall']):<18} {fmt(baseline_metrics_full['pr_auc']):<18}")
    print(f"{'Full Test Set (5-Fold CV)':<32} {'RF + Stacked Fine-Tuned CE (14 Feat)':<36} {fmt(stacked_metrics_full['f1']):<18} {fmt(stacked_metrics_full['precision']):<18} {fmt(stacked_metrics_full['recall']):<18} {fmt(stacked_metrics_full['pr_auc']):<18}")
    print("-" * 125)

    # Unseen Queries Rows
    print(f"{'Unseen Queries (Not in B1+B2)':<32} {'Random Forest (12 Features Baseline)':<36} {fmt(baseline_metrics_uns['f1']):<18} {fmt(baseline_metrics_uns['precision']):<18} {fmt(baseline_metrics_uns['recall']):<18} {fmt(baseline_metrics_uns['pr_auc']):<18}")
    print(f"{'Unseen Queries (Not in B1+B2)':<32} {'RF + Stacked Fine-Tuned CE (14 Feat)':<36} {fmt(stacked_metrics_uns['f1']):<18} {fmt(stacked_metrics_uns['precision']):<18} {fmt(stacked_metrics_uns['recall']):<18} {fmt(stacked_metrics_uns['pr_auc']):<18}")
    print("=" * 125)

    delta_full = np.mean(stacked_metrics_full["f1"]) - np.mean(baseline_metrics_full["f1"])
    delta_uns = np.mean(stacked_metrics_uns["f1"]) - np.mean(baseline_metrics_uns["f1"])
    delta_pr_full = np.mean(stacked_metrics_full["pr_auc"]) - np.mean(baseline_metrics_full["pr_auc"])
    print("\nSummary Impact of Stacked Fine-Tuned Reranker:")
    print(f"  - Full Test Set F1:   {np.mean(baseline_metrics_full['f1']):.4f} -> {np.mean(stacked_metrics_full['f1']):.4f} ({delta_full:+.4f})")
    print(f"  - Unseen Queries F1: {np.mean(baseline_metrics_uns['f1']):.4f} -> {np.mean(stacked_metrics_uns['f1']):.4f} ({delta_uns:+.4f})")
    print(f"  - Full PR-AUC:        {np.mean(baseline_metrics_full['pr_auc']):.4f} -> {np.mean(stacked_metrics_full['pr_auc']):.4f} ({delta_pr_full:+.4f})")


def main():
    parser = argparse.ArgumentParser(description="Stacked Fine-Tuned Cross-Encoder + Random Forest 5-Fold CV on GPU (Google Colab).")
    parser.add_argument("--model_name", type=str, default="cross-encoder/ms-marco-MiniLM-L-6-v2", help="Pretrained cross-encoder model")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs per run (default: 1)")
    parser.add_argument("--batch_size", type=int, default=32, help="Training batch size (default: 32)")
    parser.add_argument("--eval_batch_size", type=int, default=64, help="Inference batch size (default: 64)")
    parser.add_argument("--max_length", type=int, default=256, help="Maximum sequence token length (default: 256)")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate (default: 2e-5)")
    parser.add_argument("--warmup_ratio", type=float, default=0.10, help="Linear warmup ratio (default: 0.10 = 10%)")
    parser.add_argument("--num_outer_folds", type=int, default=5, help="Number of outer GroupKFold splits (default: 5)")
    parser.add_argument("--num_inner_folds", type=int, default=4, help="Number of inner GroupKFold splits (default: 4)")
    parser.add_argument("--seed", type=int, default=42, help="Fixed random seed (default: 42)")
    args = parser.parse_args()

    run_stacked_rf_cv(args)


if __name__ == "__main__":
    main()
