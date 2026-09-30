"""
Google Colab / Kaggle Execution Instructions:
=============================================
1. Enable GPU:
   In Google Colab, go to Runtime -> Change runtime type -> Hardware accelerator -> GPU (T4, V100, or A100).
   In Kaggle, select Settings -> Accelerator -> GPU P100 or T4 x2.

2. Upload required files (or clone the repository):
   Ensure the following input files are available:
   - data/training_pairs_old_clean.jsonl
   - data/training_pairs_v2_clean.jsonl
   - data/excluded_placeholder_sections.csv
   - Legal_Knowledge_Base_v2.xlsx
   - scripts/finetune_embedding_v3.py

   If cloning via git:
   !git clone <your_repo_url>
   %cd NyaayaSearch-Capstone

3. Install required packages (keep Colab's own PyTorch):
   !pip install scikit-learn==1.9.1 numpy==2.5.3 pandas==3.0.6 sentence-transformers==6.1.0 openpyxl==3.1.5

4. Run the script:
   !python scripts/finetune_embedding_v3.py
"""

import argparse
import csv
import json
import os
import random
import sys
import time

import numpy as np
import openpyxl
import torch
from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader

# Reconfigure stdout for UTF-8 on Windows / notebooks
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DEFAULT_DATASET = os.path.join(ROOT_DIR, "Legal_Knowledge_Base_v2.xlsx")
DEFAULT_EXCLUDED_FILE = os.path.join(ROOT_DIR, "data", "excluded_placeholder_sections.csv")
DEFAULT_OUTPUT_DIR = os.path.join(ROOT_DIR, "finetuned_legal_model_v4")

TRAINING_PAIR_FILES = [
    os.path.join(ROOT_DIR, "data", "training_pairs_old_clean.jsonl"),
    os.path.join(ROOT_DIR, "data", "training_pairs_v2_clean.jsonl"), os.path.join(ROOT_DIR, "data", "training_pairs_v3.jsonl"), os.path.join(ROOT_DIR, "data", "training_pairs_v4_judged.jsonl"),
]

BASE_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


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


def load_section_lookup(dataset_path):
    print(f"Loading legal dataset from {dataset_path} to look up section text...", flush=True)
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Knowledge base file not found: {dataset_path}")

    wb = openpyxl.load_workbook(dataset_path, read_only=True)
    ws = wb.active
    headers = list(next(ws.values))
    section_lookup = {}

    for row in ws.iter_rows(values_only=True):
        record = dict(zip(headers, row))
        act_raw = str(record.get("act_name") or "").strip()
        sec_raw = str(record.get("section_number") or "").strip()
        # Original section text construction: act_name. section_title. legal_text
        text = (
            str(record.get("act_name") or "") + ". " +
            str(record.get("section_title") or "") + ". " +
            str(record.get("legal_text") or "")
        )
        section_lookup[(act_raw, sec_raw)] = text
        section_lookup[(act_raw.lower(), sec_raw.lower())] = text

    print(f"Loaded {len(section_lookup)} section lookup keys.", flush=True)
    return section_lookup


def load_training_pairs(training_files, section_lookup, excluded_sections):
    print("Loading training pairs from JSONL files...", flush=True)
    examples = []
    total_read = 0
    total_excluded = 0
    total_missing = 0

    for file_path in training_files:
        if not os.path.exists(file_path):
            print(f"Warning: Training file not found: {file_path}", flush=True)
            continue

        file_read = 0
        file_excluded = 0
        file_missing = 0
        file_kept = 0

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                file_read += 1
                pair = json.loads(line)
                query = str(pair.get("query") or "").strip()
                act_name = str(pair.get("act_name") or "").strip()
                sec_num = str(pair.get("section_number") or "").strip()

                if not query:
                    continue

                # Check if excluded placeholder section
                if (act_name.lower(), sec_num.lower()) in excluded_sections:
                    file_excluded += 1
                    continue

                # Lookup section text
                sec_text = section_lookup.get((act_name, sec_num)) or section_lookup.get((act_name.lower(), sec_num.lower()))
                if sec_text is None:
                    file_missing += 1
                    continue

                # Original method truncates section text to 500 characters
                examples.append(InputExample(texts=[query, sec_text[:500]]))
                file_kept += 1

        total_read += file_read
        total_excluded += file_excluded
        total_missing += file_missing
        rel_name = os.path.relpath(file_path, ROOT_DIR) if os.path.isabs(file_path) else file_path
        print(f"  {rel_name}: read={file_read}, excluded_placeholders={file_excluded}, missing_section={file_missing}, kept={file_kept}", flush=True)

    print("\nSummary of Training Pairs:", flush=True)
    print(f"  Total records read:       {total_read}", flush=True)
    print(f"  Excluded placeholders:    {total_excluded}", flush=True)
    print(f"  Missing section lookup:   {total_missing}", flush=True)
    print(f"  Final training pairs:     {len(examples)}", flush=True)

    return examples


def main():
    parser = argparse.ArgumentParser(
        description="Fine-tune sentence embedding model (paraphrase-multilingual-MiniLM-L12-v2) on legal query-section pairs (v3)."
    )
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs (default: 3)")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size (default: 16)")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate for AdamW (default: 2e-5)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR, help="Path to save the fine-tuned model")
    parser.add_argument("--dataset", type=str, default=DEFAULT_DATASET, help="Path to Legal_Knowledge_Base_v2.xlsx")
    parser.add_argument("--excluded-file", type=str, default=DEFAULT_EXCLUDED_FILE, help="Path to excluded placeholder CSV")
    parser.add_argument("--use-amp", action="store_true", default=None, help="Use automatic mixed precision (fp16) on GPU")
    args = parser.parse_args()

    set_seed(args.seed)

    print("=" * 70, flush=True)
    print("Fine-tuning Embedding Model v3", flush=True)
    print("=" * 70, flush=True)
    print(f"Base Model:       {BASE_MODEL_NAME}", flush=True)
    print(f"Epochs:           {args.epochs}", flush=True)
    print(f"Batch Size:       {args.batch_size}", flush=True)
    print(f"Learning Rate:    {args.lr}", flush=True)
    print(f"Random Seed:      {args.seed}", flush=True)
    print(f"Output Directory: {args.output_dir}", flush=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print(f"Compute Device:   {device} ({device_name})", flush=True)

    use_amp = args.use_amp if args.use_amp is not None else torch.cuda.is_available()
    print(f"Mixed Precision:  {use_amp}", flush=True)
    print("=" * 70, flush=True)

    # 1. Load excluded placeholder sections
    excluded_sections = load_excluded_sections(args.excluded_file)
    print(f"Loaded {len(excluded_sections)} excluded placeholder rules.", flush=True)

    # 2. Load section text lookup
    section_lookup = load_section_lookup(args.dataset)

    # 3. Load and filter training pairs
    examples = load_training_pairs(TRAINING_PAIR_FILES, section_lookup, excluded_sections)
    if not examples:
        print("Error: No training examples found! Exiting.", file=sys.stderr)
        sys.exit(1)

    # 4. Initialize DataLoader and Loss
    train_dataloader = DataLoader(examples, shuffle=True, batch_size=args.batch_size)
    warmup_steps = int(len(train_dataloader) * 0.1)

    print(f"\nDataLoader built: {len(train_dataloader)} steps per epoch, {len(train_dataloader) * args.epochs} total steps.", flush=True)
    print(f"Warmup steps: {warmup_steps} (10% of one epoch).", flush=True)

    # 5. Load Base SentenceTransformer Model
    print(f"\nLoading base model '{BASE_MODEL_NAME}' on {device}...", flush=True)
    model = SentenceTransformer(BASE_MODEL_NAME, device=device)

    # MultipleNegativesRankingLoss with default scale=20.0, cos_sim
    train_loss = losses.MultipleNegativesRankingLoss(model)

    # 6. Train model
    print(f"\nStarting fine-tuning for {args.epochs} epochs...", flush=True)
    start_time = time.time()

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=args.epochs,
        warmup_steps=warmup_steps,
        optimizer_params={"lr": args.lr},
        use_amp=use_amp,
        show_progress_bar=True,
    )

    elapsed = time.time() - start_time
    print(f"\nFine-tuning completed in {elapsed:.1f}s ({elapsed / 60:.2f} mins).", flush=True)

    # 7. Save model
    os.makedirs(args.output_dir, exist_ok=True)
    model.save(args.output_dir)
    print(f"Done. Fine-tuned model saved to {args.output_dir}", flush=True)


if __name__ == "__main__":
    main()
