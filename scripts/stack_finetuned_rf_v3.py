"""
Google Colab Execution Instructions:
===================================
1. Enable GPU:
   In Google Colab, go to Runtime -> Change runtime type -> Hardware accelerator -> GPU (T4, V100, or A100).

2. Upload required files (or clone the repository):
   Ensure the following input files are available:
   - data/eval/classifier_training_data_v3.csv
   - Legal_Knowledge_Base_combined.xlsx
   - scripts/stack_finetuned_rf_v3.py

   If cloning via git:
   !git clone <your_repo_url>
   %cd NyaayaSearch-Capstone

3. Install required packages (keep Colab's own PyTorch):
   !pip install scikit-learn==1.9.1 numpy==2.5.3 pandas==3.0.6 sentence-transformers==6.1.0 openpyxl==3.1.5

4. Run the script:
   !python scripts/stack_finetuned_rf_v3.py
"""

import os
import sys
import json
import time
import random
import argparse
import pandas as pd
import numpy as np
import sklearn
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

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

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

INPUT_CSV_PATH = os.path.join(EVAL_DIR, "classifier_training_data_v3.csv")
KB_PATH = os.path.join(ROOT_DIR, "Legal_Knowledge_Base_combined.xlsx")
OUTPUT_CSV_PATH = os.path.join(EVAL_DIR, "stacked_finetuned_rf_v3_predictions.csv")

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


def check_library_versions():
    """Prints library versions and enforces scikit-learn == 1.9.1."""
    print("=" * 85)
    print("  LIBRARY VERSION CHECK")
    print("=" * 85)
    print(f"scikit-learn version: {sklearn.__version__}")
    print(f"numpy version:        {np.__version__}")
    print(f"pandas version:       {pd.__version__}")
    print(f"torch version:        {torch.__version__}")
    print("=" * 85)

    if sklearn.__version__ != "1.9.1":
        sys.exit(
            f"FATAL ERROR: scikit-learn version must be 1.9.1, but found {sklearn.__version__}.\n"
            f"Please run: pip install scikit-learn==1.9.1"
        )


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
    Executes the fully stacked Random Forest + Fine-Tuned Cross-Encoder evaluation on v3 data:
    5 outer GroupKFold folds by query.
    For each outer fold k:
      1. Train cross-encoder on all outer training rows (folds != k) -> score fold k test rows.
      2. Split outer training rows into 4 inner GroupKFold folds by query -> fine-tune on
         3 folds, score held-out 1 fold to populate training finetuned_score with zero leakage.
      3. Compute candidate finetuned_rank within each query.
      4. Train:
         (a) RF with 12 features (10 baseline + cross_encoder_score + cross_encoder_rank)
         (b) RF with 14 features (12 features + finetuned_score + finetuned_rank)
         Predict outer fold k with threshold 0.50.
      5. Evaluate both models on:
         - All test rows
         - Old-source test rows only
         - V2-source test rows only
         - Per-Act F1 (BNS, BNSS, Domestic Violence Act, etc.)
    """
    check_library_versions()
    set_seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("\n" + "=" * 85)
    print("  NYAAYASEARCH: STACKED FINE-TUNED CROSS-ENCODER + RANDOM FOREST V3 (COLAB GPU)")
    print("=" * 85)
    print(f"PyTorch Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    if device == "cpu":
        print("WARNING: GPU is not detected. Training on CPU will be significantly slower.")
        print("Please enable GPU under Runtime -> Change runtime type -> Hardware accelerator.")

    # 1. Load v3 data
    if not os.path.exists(INPUT_CSV_PATH):
        raise FileNotFoundError(f"Input training data not found at {INPUT_CSV_PATH}")

    print(f"\nLoading training data from {INPUT_CSV_PATH}...", flush=True)
    df_raw = pd.read_csv(INPUT_CSV_PATH)
    junk_mask = df_raw["act_name"] == "act_name"
    df = df_raw[~junk_mask].copy().reset_index(drop=True)
    if junk_mask.sum() > 0:
        print(f"Dropped {junk_mask.sum()} junk rows where act_name == 'act_name'.")
    print(f"Training dataset size: {len(df):,} rows across {df['query'].nunique():,} unique queries.")

    # Ensure gap_to_next is present
    if "gap_to_next" not in df.columns:
        df["gap_to_next"] = df.groupby("query", sort=False)["hybrid_score"].diff(-1).fillna(0.0)

    # 2. Load Knowledge Base and build document text
    kb_map = load_knowledge_base(KB_PATH)
    print("Building document text for all candidate rows...", flush=True)
    df["doc_text"] = [build_document_text(row, kb_map) for _, row in df.iterrows()]

    # 3. Query breakdown by source
    source_counts = df.groupby("query_source")["query"].nunique().to_dict()
    print(f"\nQuery Breakdown by Source:")
    print(f"  - Total unique queries: {df['query'].nunique():,} ({len(df):,} candidate rows)")
    print(f"  - Old-source queries:   {source_counts.get('old', 0):,}")
    print(f"  - V2-source queries:    {source_counts.get('v2', 0):,}")

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

    features_14 = features_12 + [
        "finetuned_score",
        "finetuned_rank",
    ]

    # 5. 5-Fold Outer GroupKFold
    outer_gkf = GroupKFold(n_splits=args.num_outer_folds)
    inner_gkf = GroupKFold(n_splits=args.num_inner_folds)

    # Metrics storage: subset -> metric -> list of fold scores
    subsets = ["all", "old", "v2"]
    baseline_metrics = {s: {"f1": [], "precision": [], "recall": [], "pr_auc": []} for s in subsets}
    stacked_metrics = {s: {"f1": [], "precision": [], "recall": [], "pr_auc": []} for s in subsets}

    unique_acts = [a for a in sorted(df["act_name"].unique()) if a != "act_name"]
    per_act_f1 = {act: {"base": [], "stacked": []} for act in unique_acts}

    oof_predictions_list = []

    print("\nStarting Stacked Model 5-Fold Cross-Validation...", flush=True)
    print("-" * 85)

    for outer_fold, (train_idx, test_idx) in enumerate(outer_gkf.split(df, groups=df["query"]), start=1):
        outer_t0 = time.time()
        print(f"\n>>> [Outer Fold {outer_fold}/{args.num_outer_folds}] Starting...", flush=True)

        outer_train_df = df.iloc[train_idx].copy().reset_index(drop=True)
        outer_test_df = df.iloc[test_idx].copy().reset_index(drop=True)

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
        # Step 4: Train and Evaluate Random Forest Models
        # -------------------------------------------------------------------
        # (a) Baseline 12-feature Random Forest
        rf_baseline = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_baseline.fit(outer_train_df[features_12], outer_train_df["is_relevant"])

        probs_base = rf_baseline.predict_proba(outer_test_df[features_12])[:, 1]
        preds_base = (probs_base >= 0.5).astype(int)

        # (b) Stacked 14-feature Random Forest (+ finetuned_score + finetuned_rank)
        print(f"  [Outer Fold {outer_fold}] Training Stacked Random Forest (14 features)...", flush=True)
        rf_stacked = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        rf_stacked.fit(outer_train_df[features_14], outer_train_df["is_relevant"])

        probs_stacked = rf_stacked.predict_proba(outer_test_df[features_14])[:, 1]
        preds_stacked = (probs_stacked >= 0.5).astype(int)

        y_full = outer_test_df["is_relevant"].values

        # Evaluate across subsets: all, old, v2
        mask_old = (outer_test_df["query_source"] == "old").values
        mask_v2 = (outer_test_df["query_source"] == "v2").values

        subset_masks = {
            "all": np.ones(len(outer_test_df), dtype=bool),
            "old": mask_old,
            "v2": mask_v2,
        }

        for s_name, mask in subset_masks.items():
            if mask.sum() == 0 or y_full[mask].sum() == 0:
                continue

            y_sub = y_full[mask]

            # Baseline 12-feat
            baseline_metrics[s_name]["f1"].append(f1_score(y_sub, preds_base[mask], zero_division=0))
            baseline_metrics[s_name]["precision"].append(precision_score(y_sub, preds_base[mask], zero_division=0))
            baseline_metrics[s_name]["recall"].append(recall_score(y_sub, preds_base[mask], zero_division=0))
            baseline_metrics[s_name]["pr_auc"].append(average_precision_score(y_sub, probs_base[mask]))

            # Stacked 14-feat
            stacked_metrics[s_name]["f1"].append(f1_score(y_sub, preds_stacked[mask], zero_division=0))
            stacked_metrics[s_name]["precision"].append(precision_score(y_sub, preds_stacked[mask], zero_division=0))
            stacked_metrics[s_name]["recall"].append(recall_score(y_sub, preds_stacked[mask], zero_division=0))
            stacked_metrics[s_name]["pr_auc"].append(average_precision_score(y_sub, probs_stacked[mask]))

        # Per-Act F1 on all test rows
        for act in unique_acts:
            act_mask = (outer_test_df["act_name"] == act).values
            if act_mask.sum() > 0 and y_full[act_mask].sum() > 0:
                act_f1_base = f1_score(y_full[act_mask], preds_base[act_mask], zero_division=0)
                act_f1_stack = f1_score(y_full[act_mask], preds_stacked[act_mask], zero_division=0)
                per_act_f1[act]["base"].append(act_f1_base)
                per_act_f1[act]["stacked"].append(act_f1_stack)

        # Save slice for out-of-fold predictions file
        oof_slice = outer_test_df[["query", "act_name", "section_number", "is_relevant"]].copy()
        oof_slice["fold"] = outer_fold
        oof_slice["query_source"] = outer_test_df["query_source"]
        oof_slice["finetuned_score"] = outer_test_df["finetuned_score"]
        oof_slice["finetuned_rank"] = outer_test_df["finetuned_rank"]
        oof_slice["rf_12_prob"] = probs_base
        oof_slice["rf_12_pred"] = preds_base
        oof_slice["stacked_rf_prob"] = probs_stacked
        oof_slice["stacked_rf_pred"] = preds_stacked
        oof_predictions_list.append(oof_slice)

        outer_elapsed = time.time() - outer_t0
        print(
            f"  [Outer Fold {outer_fold} Result] "
            f"All F1: 12f={baseline_metrics['all']['f1'][-1]:.4f} -> Stacked={stacked_metrics['all']['f1'][-1]:.4f} | "
            f"Old F1: 12f={baseline_metrics['old']['f1'][-1]:.4f} -> Stacked={stacked_metrics['old']['f1'][-1]:.4f} | "
            f"V2 F1: 12f={baseline_metrics['v2']['f1'][-1]:.4f} -> Stacked={stacked_metrics['v2']['f1'][-1]:.4f} | "
            f"Elapsed: {outer_elapsed:.1f}s",
            flush=True,
        )

    # 6. Save Out-of-Fold Predictions
    oof_df = pd.concat(oof_predictions_list, ignore_index=True)
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    oof_df.to_csv(OUTPUT_CSV_PATH, index=False)
    abs_output_path = os.path.abspath(OUTPUT_CSV_PATH)
    print(f"\nSaved out-of-fold predictions to: {abs_output_path} ({len(oof_df):,} rows).", flush=True)

    # 7. Print Final Comparison Table
    print("\n" + "=" * 135)
    print(f"{'STACKED FINE-TUNED CROSS-ENCODER + RANDOM FOREST (14 FEAT) vs 12-FEATURE BASELINE':^135}")
    print("=" * 135)
    header = f"{'Evaluation Subset':<28} {'Classifier Architecture':<38} {'F1 (Class 1)':<18} {'Precision':<18} {'Recall':<18} {'PR-AUC':<18}"
    print(header)
    print("-" * 135)

    subset_defs = [
        ("all", "All Test Rows"),
        ("old", "Old-Source Rows Only"),
        ("v2", "V2-Source Rows Only"),
    ]

    for s_key, s_label in subset_defs:
        m_base = baseline_metrics[s_key]
        m_stack = stacked_metrics[s_key]
        print(f"{s_label:<28} {'RF (12 Features Baseline)':<38} {fmt(m_base['f1']):<18} {fmt(m_base['precision']):<18} {fmt(m_base['recall']):<18} {fmt(m_base['pr_auc']):<18}")
        print(f"{'':<28} {'RF + Stacked Fine-Tuned CE (14 Feat)':<38} {fmt(m_stack['f1']):<18} {fmt(m_stack['precision']):<18} {fmt(m_stack['recall']):<18} {fmt(m_stack['pr_auc']):<18}")
        delta_f1 = np.mean(m_stack["f1"]) - np.mean(m_base["f1"])
        delta_pr = np.mean(m_stack["pr_auc"]) - np.mean(m_base["pr_auc"])
        print(f"  --> Delta (14 Feat - 12 Feat): F1 {delta_f1:+.4f} | PR-AUC {delta_pr:+.4f}")
        print("-" * 135)

    # 8. Print Per-Act F1 Breakdown Table
    print("\n" + "=" * 110)
    print(f"{'PER-ACT F1 BREAKDOWN (ALL TEST ROWS)':^110}")
    print("=" * 110)
    act_header = f"{'Act Name':<55} {'RF (12 Features)':<20} {'Stacked RF (14 Feat)':<20} {'Delta':<12}"
    print(act_header)
    print("-" * 110)

    priority_acts = [
        "Bharatiya Nyaya Sanhita, 2023",
        "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "Protection of Women from Domestic Violence Act, 2005",
    ]
    other_acts = [a for a in unique_acts if a not in priority_acts]

    for act in priority_acts + other_acts:
        list_base = per_act_f1.get(act, {}).get("base", [])
        list_stack = per_act_f1.get(act, {}).get("stacked", [])
        if not list_base:
            continue
        mean_base = np.mean(list_base)
        mean_stack = np.mean(list_stack)
        delta = mean_stack - mean_base
        star = " *" if act in priority_acts else ""
        display_name = ACT_SHORT_NAMES.get(act, act) + star
        print(f"{display_name:<55} {fmt(list_base):<20} {fmt(list_stack):<20} {delta:+.4f}")

    print("-" * 110)
    print("* Key targeted acts with expanded training pairs in v2.")
    print("=" * 110 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Stacked Fine-Tuned Cross-Encoder + Random Forest v3 (Google Colab GPU).")
    parser.add_argument("--model_name", type=str, default="cross-encoder/ms-marco-MiniLM-L-6-v2", help="Pretrained cross-encoder model")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs per run (default: 1)")
    parser.add_argument("--batch_size", type=int, default=32, help="Training batch size (default: 32)")
    parser.add_argument("--eval_batch_size", type=int, default=64, help="Inference batch size (default: 64)")
    parser.add_argument("--max_length", type=int, default=256, help="Maximum sequence token length (default: 256)")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate (default: 2e-5)")
    parser.add_argument("--warmup_ratio", type=float, default=0.10, help="Linear warmup ratio (default: 0.10 = 10%%)")
    parser.add_argument("--num_outer_folds", type=int, default=5, help="Number of outer GroupKFold splits (default: 5)")
    parser.add_argument("--num_inner_folds", type=int, default=4, help="Number of inner GroupKFold splits (default: 4)")
    parser.add_argument("--seed", type=int, default=42, help="Fixed random seed (default: 42)")
    args = parser.parse_args()

    run_stacked_rf_cv(args)


if __name__ == "__main__":
    main()
