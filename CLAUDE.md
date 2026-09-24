# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

NyaayaSearch is an Indian legal-assistance web app: a FastAPI backend (`scripts/main.py`) doing hybrid (BM25 + fine-tuned sentence-embedding) search over a legal knowledge base, plus a Groq-LLM-powered layer for plain-language explanation, translation (English/Hindi/Kannada), document drafting, case simplification, dictionary lookups, and PDF Q&A. The frontend is a separate Vite/React SPA in `frontend/` (see `frontend/CLAUDE.md` for frontend-specific guidance).

## Commands

Backend (run from `scripts/`, with the venv active):

- `uvicorn main:app --reload --port 8000` — start the API (frontend hardcodes `http://127.0.0.1:8000` as `API_URL`)
- `python evaluate.py --languages en,hi,kn` — run the real retrieval evaluation (Recall@5, P@1, P@3, MRR, nDCG@5) against frozen query sets in `../data/eval/`; add `--ablation` to also run the component ablation. Results are written to `../results/`.

There is **no automated test suite** (no pytest, no `tests/` directory). Correctness of retrieval/ranking changes is checked by running `evaluate.py` and comparing against the numbers in `METRICS_AND_MODEL_COMPARISON.md`, not by unit tests.

Frontend commands are documented in `frontend/CLAUDE.md`.

## Architecture

**Backend layout (`scripts/`)** — each concern is a standalone `*_core.py` module imported directly by `main.py`; there is no package structure or dependency injection:
- `search_core.py` — `SearchEngine`: loads `Legal_Knowledge_Base_combined.xlsx` at startup, builds a BM25 index and a semantic index using a locally fine-tuned model at `../finetuned_legal_model/` (loaded via `sentence-transformers`). `search()` combines `0.15 * bm25 + 0.85 * semantic` scores, then applies a large hand-written table of query-keyword-triggered score boosts/penalties (landlord/tenant, security deposit, IPC→BNS redirection, minor+contract, hacking, driving licence, RTI, specific performance, etc.) before returning top-k. Also holds `IPC_TO_BNS`, the old-IPC-section → new-BNS-section mapping used to redirect queries about the repealed Indian Penal Code.
- `rag_core.py` — Groq client (`GROQ_API_KEY` env var, `python-dotenv`) wrapping `generate_explanation`, `translate_to_english`, `translate_explanation`, `detect_language` (Unicode-script-range based, no API call), and `verify_citations` (checks the LLM's explanation didn't invent a section number not present in the search results).
- `citations_core.py`, `pdf_core.py`, `dictionary_core.py`, `drafter_core.py`, `case_simplifier_core.py`, `bns_decoder_core.py` — one module per `/`-route feature, each independent of the others.
- `main.py` wires these together. `engine = SearchEngine()` is built once at FastAPI startup (`@app.on_event("startup")`) since embedding the whole corpus is expensive; `document_store` (uploaded-PDF text, keyed by `filename_charcount`) is an in-memory dict, not persisted.

**Routes**: `/search`, `/explain` (search + LLM explanation with a confidence-threshold fallback and citation verification), `/translate-explanation`, `/upload-pdf` + `/ask-document`, `/define`, `/draft-document` + `/document-types`, `/simplify-case`, `/bns-lookup`. Every route degrades gracefully on `groq.RateLimitError` (returns a specific "temporarily unavailable" message) rather than failing outright — follow this pattern for any new Groq-backed route.

**Data pipeline is separate from the live app.** `Legal_Knowledge_Base_*.xlsx` files, `data/`, and the many one-off scripts in `scripts/` (`build_classifier_data_*.py`, `add_*.py`, `check_*.py`, etc.) are the offline dataset-construction/experimentation history, not code the running app depends on. The `relevance_classifier*.pkl` models and the reranking-related scripts (`ablation_matrix.py`, `classifier_pr_curve.py`, `train_classifier.py`, `compare_search_vs_reranked.py`, etc.) are evaluation/research artifacts — **the live `SearchEngine.search()` does not use the classifier at all**, only BM25 + embeddings + hand-written boosts. Don't assume a script in `scripts/` is part of the request path just because it lives there.

**Evaluation discipline (important, established by project history):** this project has documented cases (see `METRICS_AND_MODEL_COMPARISON.md`) of retrieval "improvements" that scored well on the exact queries used to diagnose a failure but did not generalize to a fresh, untouched query set. Before claiming a retrieval/ranking change improved anything, validate it on data that was not used to design the change, and report the honest number even if it's a null result. `METRICS_AND_MODEL_COMPARISON.md` is the single source of truth for current metrics; keep it (or run `evaluate.py` yourself) rather than trusting stale numbers elsewhere.

**Multilingual support** works via translate-then-search: non-English queries are translated to English (`translate_to_english`) before hitting `SearchEngine`, and explanations are generated/translated back into the detected language. `BGE_M3_EXPERIMENT_NOTES.md` documents why a native-multilingual embedding model was considered and rejected (CPU-only hardware made embedding the corpus impractical) — re-litigate only if GPU becomes available.

## Rules

- Don't read `.env` files or print API keys (`GROQ_API_KEY` is required for all LLM-backed features). `.claude/settings.json` denies reading `.env`/`.env.*` — don't work around it.
- Don't rename or change any backend endpoint path or request/response shape without updating `frontend/src/App.jsx`, which hardcodes them.
- Frontend and backend have separate CLAUDE.md files — read `frontend/CLAUDE.md` before touching anything under `frontend/`.
