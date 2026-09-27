#!/usr/bin/env python3
"""Deploy NyaayaSearch backend to Hugging Face Spaces.

Uploads ONLY runtime files required to build and run the Docker backend:
- Dockerfile, .dockerignore, requirements.txt
- Legal_Knowledge_Base_combined.xlsx
- data/ipc_bns_mapping.csv, data/excluded_placeholder_sections.csv, data/case_law/processed/case_citations.csv
- scripts/*.py
- Generated Space README.md with HF metadata front-matter

Excludes: .env, .venv, frontend/, model folders, caches, training/eval data.
"""

import argparse
import glob
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SPACE_README = """---
title: NyaayaSearch API
emoji: ⚖️
colorFrom: indigo
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

NyaayaSearch API: Hybrid Indian statutory search, cross-encoder reranking, and multilingual legal reasoning.
"""

BLOCKED_PATTERNS = [
    ".env",
    ".venv",
    "frontend/",
    "finetuned_legal_model",
    "data/cache",
    "data/raw",
    "data/eval",
    "data/scenarios",
    "data/training_pairs",
    "data/uncovered_sections",
    "__pycache__",
    ".pyc",
    ".npy",
]


def is_blocked(path_str: str) -> bool:
    normalized = path_str.replace("\\", "/").lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in normalized:
            return True
    return False


def collect_runtime_files(repo_root: Path) -> list[tuple[str, Path]]:
    """Returns a list of (path_in_repo, absolute_path) for all runtime files."""
    files_to_upload: list[tuple[str, Path]] = []

    # 1. Root configuration & dependency files
    root_files = [
        "Dockerfile",
        ".dockerignore",
        "requirements.txt",
        "Legal_Knowledge_Base_combined.xlsx",
    ]
    for rf in root_files:
        p = repo_root / rf
        if not p.is_file():
            raise FileNotFoundError(f"Missing required root file: {rf}")
        files_to_upload.append((rf, p))

    # 2. Data files required at runtime
    data_files = [
        "data/ipc_bns_mapping.csv",
        "data/excluded_placeholder_sections.csv",
        "data/case_law/processed/case_citations.csv",
    ]
    for df in data_files:
        p = repo_root / df
        if not p.is_file():
            raise FileNotFoundError(f"Missing required data file: {df}")
        files_to_upload.append((df.replace("\\", "/"), p))

    # 3. All python scripts in scripts/
    scripts_dir = repo_root / "scripts"
    for py_file in sorted(scripts_dir.glob("*.py")):
        rel = py_file.relative_to(repo_root).as_posix()
        files_to_upload.append((rel, py_file))

    # Final safety check against forbidden files
    for rel_path, abs_path in files_to_upload:
        if is_blocked(rel_path):
            raise ValueError(f"Safety check failed: blocked file detected in upload list: {rel_path}")

    return files_to_upload


def main():
    parser = argparse.ArgumentParser(description="Deploy NyaayaSearch backend to Hugging Face Spaces")
    parser.add_argument("--repo-id", default="duladani/nyaaya-search-api", help="HF Space repository ID")
    parser.add_argument("--dry-run", action="store_true", help="Print file list and README without uploading")
    parser.add_argument("--token", default=None, help="Hugging Face API token (defaults to HF_TOKEN env var)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    files = collect_runtime_files(repo_root)

    total_size = sum(p.stat().st_size for _, p in files)

    print(f"=== Hugging Face Space Deployment: {args.repo_id} ===")
    print(f"Target Space: https://huggingface.co/spaces/{args.repo_id}")
    print(f"Total runtime files to upload: {len(files)} + Space README.md")
    print(f"Total upload size: {total_size / (1024 * 1024):.2f} MB ({total_size:,} bytes)\n")

    print("Files to upload:")
    for rel_path, abs_path in sorted(files, key=lambda x: x[0]):
        size_kb = abs_path.stat().st_size / 1024
        if size_kb >= 1024:
            size_str = f"{size_kb / 1024:.2f} MB"
        else:
            size_str = f"{size_kb:.1f} KB"
        print(f"  - {rel_path:<45} ({size_str:>9})")

    print(f"  - {'README.md (Space front-matter)':<45} ({len(SPACE_README.encode('utf-8'))} bytes)")

    print("\n--- Space README.md Preview ---")
    print(SPACE_README.strip())
    print("--------------------------------\n")

    if args.dry_run:
        print("[DRY-RUN] No files were uploaded. Run without --dry-run to deploy to Hugging Face Spaces.")
        return

    # Real upload via huggingface_hub HfApi
    try:
        from huggingface_hub import HfApi, CommitOperationAdd
    except ImportError:
        print("Error: huggingface_hub is not installed. Install with `pip install huggingface_hub`.", file=sys.stderr)
        sys.exit(1)

    token = args.token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    api = HfApi(token=token)

    print("Checking / creating Hugging Face Space...")
    try:
        api.create_repo(
            repo_id=args.repo_id,
            repo_type="space",
            space_sdk="docker",
            exist_ok=True,
        )
    except Exception as e:
        print(f"Notice during create_repo: {e}")

    print("Creating commit with runtime files...")
    operations = [
        CommitOperationAdd(path_in_repo=rel_path, path_or_fileobj=str(abs_path))
        for rel_path, abs_path in files
    ]
    # Add Space-specific README with front-matter
    operations.append(
        CommitOperationAdd(path_in_repo="README.md", path_or_fileobj=SPACE_README.encode("utf-8"))
    )

    commit_info = api.create_commit(
        repo_id=args.repo_id,
        repo_type="space",
        operations=operations,
        commit_message="Deploy NyaayaSearch backend runtime files",
    )
    print(f"Successfully deployed to Space: https://huggingface.co/spaces/{args.repo_id}")
    print(f"Commit URL: {commit_info.commit_url}")


if __name__ == "__main__":
    main()
