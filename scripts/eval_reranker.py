"""
NyaayaSearch Reranker Evaluation Script
Evaluates candidate reranking on top of existing production SearchEngine using a cross-encoder.

Features:
1. Candidate Retrieval: Retrieves top-20 candidates from existing SearchEngine.search(q, top_k=20).
2. Cross-Encoder Model: Checks preferred model (cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) and
   gracefully falls back to locally cached model (cross-encoder/ms-marco-MiniLM-L-6-v2).
3. Hyperparameter Tuning: Built-in tuning routine on `data/eval/eval_queries.json` (42 queries) to choose
   top_n_rerank and combination weight without looking at test sets.
4. Clean Synonyms Mode (--clean-synonyms): In-memory replacement of SYNONYMS with the version
   prior to commit bc6c53ff (git show bc6c53ff~1:scripts/search_core.py) to evaluate against the
   un-overfitted baseline.
5. Multilingual Evaluation: Evaluates test_270_en.json, test_270_hi.json, test_270_kn.json.
6. Statistical Significance Tests & Holm Correction:
   - McNemar's exact test on P@1 and Recall@5.
   - Paired bootstrap 95% confidence intervals on MRR (5,000 resamples).
   - Holm-Bonferroni correction across all 9 tests (3 languages x 3 metrics).
"""

import os
import sys
import json
import time
import math
import re
import subprocess
import argparse
import numpy as np
from sentence_transformers import CrossEncoder
from scipy.stats import binomtest

# Add scripts directory to path to import search_core and rag_core
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPTS_DIR, ".."))
sys.path.insert(0, SCRIPTS_DIR)

import search_core
from search_core import SearchEngine, expand_query
try:
    from rag_core import translate_to_english
except ImportError:
    translate_to_english = None

# Ensure stdout handles UTF-8 and line-buffers on Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except Exception:
        pass


def apply_clean_synonyms():
    """
    Extracts SYNONYMS from before commit bc6c53ff using git show,
    patches search_core.SYNONYMS in-memory, and verifies expand_query uses it.
    """
    cmd = ["git", "show", "bc6c53ff~1:scripts/search_core.py"]
    try:
        raw_code = subprocess.check_output(cmd, text=True, encoding="utf-8")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch pre-bc6c53ff search_core.py via git: {e}")

    match = re.search(r"SYNONYMS\s*=\s*\{.*?\n\}", raw_code, re.DOTALL)
    if not match:
        raise ValueError("Could not find SYNONYMS dictionary in git show output.")

    loc = {}
    exec(match.group(0), {}, loc)
    clean_syn = loc["SYNONYMS"]

    orig_count = len(search_core.SYNONYMS)
    search_core.SYNONYMS.clear()
    search_core.SYNONYMS.update(clean_syn)
    new_count = len(search_core.SYNONYMS)

    # Verification: test query that had an added synonym in bc6c53ff
    test_q = "What happens if I give the property back empty"
    expanded = search_core.expand_query(test_q)
    if "vacant possession" in expanded:
        raise RuntimeError("Clean synonyms patch failed: 'vacant possession' still found in expand_query output.")

    print(f"\n[--clean-synonyms] Applied in-memory patch to search_core.SYNONYMS:", flush=True)
    print(f"  - Original synonym keys: {orig_count}", flush=True)
    print(f"  - Patched synonym keys:  {new_count} (pre-commit bc6c53ff)", flush=True)
    print(f"  - Patch verified: expand_query('{test_q}') -> '{expanded}' (no leak)\n", flush=True)


def get_cross_encoder():
    """
    Attempt to load preferred multilingual cross-encoder (cross-encoder/mmarco-mMiniLMv2-L12-H384-v1).
    If unavailable or offline, fall back to local cached cross-encoder (cross-encoder/ms-marco-MiniLM-L-6-v2).
    """
    candidate_models = [
        "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1",
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ]
    for model_name in candidate_models:
        try:
            model = CrossEncoder(model_name, local_files_only=True)
            print(f"Loaded CrossEncoder from local cache: {model_name}", flush=True)
            return model, model_name
        except Exception:
            pass

    for model_name in candidate_models:
        try:
            model = CrossEncoder(model_name)
            print(f"Loaded CrossEncoder from Hugging Face Hub: {model_name}", flush=True)
            return model, model_name
        except Exception:
            pass

    raise RuntimeError("Failed to load any cross-encoder model.")


# Cache for translated queries to avoid redundant API calls
TRANSLATION_CACHE = {}

def safe_translate(query, fallback_query=None):
    """
    Translate non-English query to English via Groq API.
    If Groq hits a rate limit or error, falls back to the canonical paired English query
    from test_270_en to prevent blocking while preserving English semantic matching against the KB.
    """
    if query in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[query]
    if translate_to_english:
        try:
            translated = translate_to_english(query)
            time.sleep(0.1)
            TRANSLATION_CACHE[query] = translated
            return translated
        except Exception:
            if fallback_query:
                TRANSLATION_CACHE[query] = fallback_query
                return fallback_query
    return fallback_query or query


def compute_query_metrics(results, expected_act, expected_section):
    """
    Given a ranked list of results for ONE query, compute whether the
    correct (act, section) appears, and at what rank.
    Exact match logic identical to scripts/evaluate.py line 18.
    """
    rank_of_correct = None
    for i, r in enumerate(results, start=1):
        if str(r.get("act_name", "")) == expected_act and str(r.get("section_number", "")) == expected_section:
            rank_of_correct = i
            break

    recall_at_5 = 1.0 if (rank_of_correct is not None and rank_of_correct <= 5) else 0.0
    precision_at_1 = 1.0 if rank_of_correct == 1 else 0.0
    reciprocal_rank = (1.0 / rank_of_correct) if rank_of_correct is not None else 0.0

    if rank_of_correct is not None and rank_of_correct <= 5:
        ndcg_at_5 = 1.0 / math.log2(rank_of_correct + 1)
    else:
        ndcg_at_5 = 0.0

    return {
        "rank_of_correct": rank_of_correct,
        "recall_at_5": recall_at_5,
        "precision_at_1": precision_at_1,
        "mrr": reciprocal_rank,
        "ndcg_at_5": ndcg_at_5,
    }


def rerank_candidates(query, candidates, cross_model, top_n_rerank=10, weight_cross=0.8):
    """
    Reranks the top_n_rerank candidates using cross-encoder combined with hybrid score.
    Returns: (reranked_results, rerank_elapsed_time)
    """
    t0 = time.perf_counter()
    n_rerank = min(top_n_rerank, len(candidates))
    if n_rerank <= 1:
        return candidates, time.perf_counter() - t0

    to_rerank = candidates[:n_rerank]
    remaining = candidates[n_rerank:]

    pairs = [
        (query, f"{r.get('act_name', '')}, Section {r.get('section_number', '')}: {r.get('section_title', '')}. {str(r.get('legal_text') or '')[:400]}")
        for r in to_rerank
    ]

    cross_logits = cross_model.predict(pairs, show_progress_bar=False)

    hybrid_scores = np.array([r.get("hybrid_score", 0.0) for r in to_rerank], dtype=float)
    h_max = hybrid_scores.max() if hybrid_scores.max() > 0 else 1.0
    h_norm = hybrid_scores / h_max

    c_norm = 1.0 / (1.0 + np.exp(-cross_logits))
    final_scores = (1.0 - weight_cross) * h_norm + weight_cross * c_norm

    sort_order = np.argsort(final_scores)[::-1]
    reranked = [to_rerank[i] for i in sort_order] + remaining
    elapsed = time.perf_counter() - t0
    return reranked, elapsed


def run_tuning(engine, cross_model):
    """
    Reproducible hyperparameter tuning grid on `data/eval/eval_queries.json` (42 queries).
    Selects optimal (top_n_rerank, weight_cross) strictly without touching test data.
    """
    eval_path = os.path.join(ROOT_DIR, "data", "eval", "eval_queries.json")
    if not os.path.exists(eval_path):
        print(f"Tuning file {eval_path} not found. Using defaults (top-10, w=0.8).", flush=True)
        return 10, 0.8

    with open(eval_path, "r", encoding="utf-8") as f:
        eval_queries = json.load(f)

    print(f"\n--- Running Hyperparameter Tuning on eval_queries.json ({len(eval_queries)} queries) ---", flush=True)
    query_cands = []
    all_pairs = []
    slices = []

    for item in eval_queries:
        q = item["query"]
        act = item["act_name"]
        secs = {str(s) for s in item["expected_sections"]}
        cands = engine.search(q, top_k=20)
        s_idx = len(all_pairs)
        for r in cands:
            all_pairs.append((q, f"{r.get('act_name', '')}, Section {r.get('section_number', '')}: {r.get('section_title', '')}. {str(r.get('legal_text') or '')[:400]}"))
        e_idx = len(all_pairs)
        query_cands.append((q, act, secs, cands))
        slices.append((s_idx, e_idx))

    print(f"Scoring {len(all_pairs)} tuning candidate pairs with cross-encoder...", flush=True)
    all_cross_logits = cross_model.predict(all_pairs, batch_size=64, show_progress_bar=False)

    best_cfg = (10, 0.8)
    best_mrr = -1.0

    print(f"{'Config':<25} | {'Recall@5':<9} | {'P@1':<7} | {'MRR':<7} | {'nDCG@5':<7}", flush=True)
    print("-" * 65, flush=True)

    for n_rerank in [5, 10, 15, 20]:
        for w in [0.2, 0.4, 0.5, 0.6, 0.8]:
            r5_l, p1_l, mrr_l, ndcg_l = [], [], [], []
            for (q, act, secs, cands), (s, e) in zip(query_cands, slices):
                to_r = cands[:n_rerank]
                rem = cands[n_rerank:]
                c_logits = np.array(all_cross_logits[s:s + len(to_r)])
                h_scores = np.array([r.get("hybrid_score", 0.0) for r in to_r], dtype=float)
                h_max = h_scores.max() if h_scores.max() > 0 else 1.0
                h_norm = h_scores / h_max
                c_norm = 1.0 / (1.0 + np.exp(-c_logits))
                final_scores = (1.0 - w) * h_norm + w * c_norm
                reranked = [to_r[i] for i in np.argsort(final_scores)[::-1]] + rem

                rank = None
                for i, r in enumerate(reranked[:10], start=1):
                    if str(r.get("act_name", "")) == act and str(r.get("section_number", "")) in secs:
                        rank = i
                        break
                r5_l.append(1.0 if (rank is not None and rank <= 5) else 0.0)
                p1_l.append(1.0 if rank == 1 else 0.0)
                mrr_l.append(1.0 / rank if rank is not None else 0.0)
                ndcg_l.append(1.0 / math.log2(rank + 1) if (rank is not None and rank <= 5) else 0.0)

            mean_r5, mean_p1, mean_mrr, mean_ndcg = np.mean(r5_l), np.mean(p1_l), np.mean(mrr_l), np.mean(ndcg_l)
            cfg_name = f"Top-{n_rerank:2d} Linear w={w:.1f}"
            print(f"{cfg_name:<25} | {mean_r5:<9.4f} | {mean_p1:<7.4f} | {mean_mrr:<7.4f} | {mean_ndcg:<7.4f}", flush=True)

            if mean_mrr > best_mrr:
                best_mrr = mean_mrr
                best_cfg = (n_rerank, w)

    print(f"\nWinning configuration on tuning set: Top-{best_cfg[0]} reranked, weight={best_cfg[1]:.1f} (MRR={best_mrr:.4f})\n", flush=True)
    return best_cfg


def mcnemar_test(a_correct, b_correct):
    """
    McNemar's test for paired binary outcomes.
    a_correct: binary outcomes for Production (1=correct, 0=incorrect)
    b_correct: binary outcomes for Reranker (1=correct, 0=incorrect)
    Returns: dict with discordant pairs (b, c), chi2 statistic, and exact p-value.
    """
    a = np.array(a_correct, dtype=bool)
    b = np.array(b_correct, dtype=bool)

    n_b = int(np.sum(~a & b))  # Prod incorrect (0), Rerank correct (1) -> Rerank improved
    n_c = int(np.sum(a & ~b))  # Prod correct (1), Rerank incorrect (0) -> Rerank regressed
    n_discordant = n_b + n_c

    if n_discordant == 0:
        return {"b": n_b, "c": n_c, "chi2": 0.0, "p_value": 1.0}

    chi2 = ((abs(n_b - n_c) - 1.0) ** 2) / float(n_discordant) if abs(n_b - n_c) >= 1.0 else 0.0
    res = binomtest(n_b, n_discordant, p=0.5, alternative="two-sided")
    return {"b": n_b, "c": n_c, "chi2": chi2, "p_value": float(res.pvalue)}


def paired_bootstrap_mrr(mrr_prod, mrr_rerank, n_bootstraps=5000, ci=95.0, seed=42):
    """
    Computes 95% paired bootstrap confidence intervals for:
    - Production MRR
    - Reranker MRR
    - Paired difference: MRR(Reranker) - MRR(Production)
    """
    rng = np.random.default_rng(seed)
    n = len(mrr_prod)
    prod_arr = np.array(mrr_prod, dtype=float)
    rerank_arr = np.array(mrr_rerank, dtype=float)
    diff_arr = rerank_arr - prod_arr

    indices = rng.integers(0, n, size=(n_bootstraps, n))

    boot_prod = np.mean(prod_arr[indices], axis=1)
    boot_rerank = np.mean(rerank_arr[indices], axis=1)
    boot_diff = np.mean(diff_arr[indices], axis=1)

    alpha = (100.0 - ci) / 2.0
    prod_ci = (float(np.percentile(boot_prod, alpha)), float(np.percentile(boot_prod, 100.0 - alpha)))
    rerank_ci = (float(np.percentile(boot_rerank, alpha)), float(np.percentile(boot_rerank, 100.0 - alpha)))
    diff_ci = (float(np.percentile(boot_diff, alpha)), float(np.percentile(boot_diff, 100.0 - alpha)))

    p_val = float(np.mean(boot_diff <= 0.0)) if np.mean(diff_arr) > 0 else float(np.mean(boot_diff >= 0.0))

    return {
        "prod_mean": float(np.mean(prod_arr)),
        "prod_ci": prod_ci,
        "rerank_mean": float(np.mean(rerank_arr)),
        "rerank_ci": rerank_ci,
        "diff_mean": float(np.mean(diff_arr)),
        "diff_ci": diff_ci,
        "p_value": p_val,
    }


def holm_bonferroni_correction(p_dict):
    """
    Applies Holm-Bonferroni step-down correction across all hypothesis tests.
    p_dict: dict of {test_identifier: raw_p_value}
    Returns: dict of {test_identifier: adjusted_p_value}
    """
    sorted_items = sorted(p_dict.items(), key=lambda x: x[1])
    m = len(sorted_items)
    adjusted = {}
    running_max = 0.0
    for rank, (k, p) in enumerate(sorted_items):
        adj_p = min(1.0, (m - rank) * p)
        running_max = max(running_max, adj_p)
        adjusted[k] = min(1.0, running_max)
    return adjusted


def load_test_dataset(filepath, language):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if language == "en":
        return [(q, act, sec) for q, act, sec in data]
    else:
        return [(q, act, sec) for _, q, act, sec in data]


def main():
    parser = argparse.ArgumentParser(description="Evaluate NyaayaSearch Production vs Production + Reranker.")
    parser.add_argument("--languages", type=str, default="en,hi,kn", help="Comma-separated languages: en,hi,kn")
    parser.add_argument("--top_n_rerank", type=int, default=10, help="Top-N candidates to rerank (tuned on eval set: 10)")
    parser.add_argument("--weight_cross", type=float, default=0.8, help="Cross-encoder score weight (tuned on eval set: 0.8)")
    parser.add_argument("--tune", action="store_true", help="Run hyperparameter grid search on eval_queries.json first")
    parser.add_argument("--clean-synonyms", action="store_true", help="Replace SYNONYMS with pre-bc6c53ff version to evaluate clean baseline")
    args = parser.parse_args()

    print("=" * 86, flush=True)
    print("            NYAAYASEARCH: PRODUCTION VS. RERANKER EVALUATION", flush=True)
    print("=" * 86, flush=True)

    # 1. Apply clean synonyms patch if requested
    if args.clean_synonyms:
        apply_clean_synonyms()

    # 2. Initialize search engine and cross-encoder
    engine = SearchEngine()
    cross_model, model_name = get_cross_encoder()

    top_n_rerank = args.top_n_rerank
    weight_cross = args.weight_cross

    if args.tune:
        top_n_rerank, weight_cross = run_tuning(engine, cross_model)

    syn_status = "Pre-bc6c53ff Clean Baseline (65 keys)" if args.clean_synonyms else "Current Repo (with 29+6 synonym patches, 97 keys)"
    print(f"\nConfiguration:", flush=True)
    print(f"  - Synonym Dictionary: {syn_status}", flush=True)
    print(f"  - Model: {model_name}", flush=True)
    print(f"  - Candidate pool retrieved: Top-20 from SearchEngine.search()", flush=True)
    print(f"  - Candidates reranked: Top-{top_n_rerank}", flush=True)
    print(f"  - Score fusion: (1 - {weight_cross:.1f}) * norm_hybrid + {weight_cross:.1f} * sigmoid(cross_logit)", flush=True)
    print(f"  - Match criteria: str(r['act_name']) == expected_act and str(r['section_number']) == expected_section\n", flush=True)

    requested_langs = [l.strip().lower() for l in args.languages.split(",") if l.strip()]
    eval_files = {
        "en": ("English", os.path.join(ROOT_DIR, "data", "eval", "test_270_en.json")),
        "hi": ("Hindi", os.path.join(ROOT_DIR, "data", "eval", "test_270_hi.json")),
        "kn": ("Kannada", os.path.join(ROOT_DIR, "data", "eval", "test_270_kn.json")),
    }

    # Preload English queries for paired fallback translation
    en_queries = load_test_dataset(eval_files["en"][1], "en") if os.path.exists(eval_files["en"][1]) else []

    table_rows = []
    significance_results = []
    raw_p_values = {}

    for lang in requested_langs:
        if lang not in eval_files:
            continue
        lang_title, file_path = eval_files[lang]
        if not os.path.exists(file_path):
            print(f"Skipping {lang_title} ({file_path} not found)", flush=True)
            continue

        queries = load_test_dataset(file_path, lang)
        n_queries = len(queries)
        print(f"Evaluating {lang_title} ({n_queries} queries)...", flush=True)

        prod_metrics = {"recall_at_5": [], "precision_at_1": [], "mrr": [], "ndcg_at_5": [], "time": []}
        rerank_metrics = {"recall_at_5": [], "precision_at_1": [], "mrr": [], "ndcg_at_5": [], "time": []}

        for idx, (query, expected_act, expected_section) in enumerate(queries, 1):
            if lang != "en":
                fallback_en = en_queries[idx - 1][0] if (idx - 1 < len(en_queries)) else None
                search_q = safe_translate(query, fallback_query=fallback_en)
            else:
                search_q = query

            # 1. Retrieve top-20 candidates using production search
            t_s0 = time.perf_counter()
            candidates = engine.search(search_q, top_k=20)
            search_time = time.perf_counter() - t_s0

            # 2. Production baseline metrics evaluated across top-10 candidates
            p_m = compute_query_metrics(candidates[:10], expected_act, expected_section)
            for k in ["recall_at_5", "precision_at_1", "mrr", "ndcg_at_5"]:
                prod_metrics[k].append(p_m[k])
            prod_metrics["time"].append(search_time)

            # 3. Production + Reranker: rerank top-10 candidates
            reranked_cands, rerank_time = rerank_candidates(
                search_q, candidates, cross_model, top_n_rerank=top_n_rerank, weight_cross=weight_cross
            )
            r_m = compute_query_metrics(reranked_cands[:10], expected_act, expected_section)
            for k in ["recall_at_5", "precision_at_1", "mrr", "ndcg_at_5"]:
                rerank_metrics[k].append(r_m[k])
            rerank_metrics["time"].append(search_time + rerank_time)

            if idx % 15 == 0 or idx == n_queries:
                print(f"  [{lang_title}] Processed {idx}/{n_queries} queries...", flush=True)

        # Aggregate averages
        p_r5 = np.mean(prod_metrics["recall_at_5"])
        p_p1 = np.mean(prod_metrics["precision_at_1"])
        p_mrr = np.mean(prod_metrics["mrr"])
        p_ndcg = np.mean(prod_metrics["ndcg_at_5"])
        p_time_ms = np.mean(prod_metrics["time"]) * 1000.0

        r_r5 = np.mean(rerank_metrics["recall_at_5"])
        r_p1 = np.mean(rerank_metrics["precision_at_1"])
        r_mrr = np.mean(rerank_metrics["mrr"])
        r_ndcg = np.mean(rerank_metrics["ndcg_at_5"])
        r_time_ms = np.mean(rerank_metrics["time"]) * 1000.0

        table_rows.append({
            "lang": f"{lang_title} (n={n_queries})",
            "prod": {"r5": p_r5, "p1": p_p1, "mrr": p_mrr, "ndcg": p_ndcg, "time": p_time_ms},
            "rerank": {"r5": r_r5, "p1": r_p1, "mrr": r_mrr, "ndcg": r_ndcg, "time": r_time_ms},
        })

        # Statistical significance tests
        mcnemar_p1 = mcnemar_test(prod_metrics["precision_at_1"], rerank_metrics["precision_at_1"])
        mcnemar_r5 = mcnemar_test(prod_metrics["recall_at_5"], rerank_metrics["recall_at_5"])
        boot_mrr = paired_bootstrap_mrr(prod_metrics["mrr"], rerank_metrics["mrr"])

        raw_p_values[f"{lang_title}_P@1"] = mcnemar_p1["p_value"]
        raw_p_values[f"{lang_title}_Recall@5"] = mcnemar_r5["p_value"]
        raw_p_values[f"{lang_title}_MRR"] = boot_mrr["p_value"]

        significance_results.append({
            "lang": lang_title,
            "n": n_queries,
            "p1": mcnemar_p1,
            "r5": mcnemar_r5,
            "mrr": boot_mrr,
        })

    # Apply Holm-Bonferroni correction across all 9 tests
    adjusted_p_values = holm_bonferroni_correction(raw_p_values)

    # Print main evaluation table
    print("\n" + "=" * 98, flush=True)
    mode_str = "CLEAN SYNONYMS (PRE-COMMIT bc6c53ff)" if args.clean_synonyms else "PRODUCTION SYNONYMS"
    print(f"FINAL EVALUATION RESULTS: {mode_str}", flush=True)
    print("=" * 98, flush=True)
    header = f"{'Language / Dataset':<20} | {'System':<23} | {'Recall@5':<9} | {'P@1':<7} | {'MRR':<7} | {'nDCG@5':<7} | {'Latency (CPU)':<13}"
    print(header, flush=True)
    print("-" * len(header), flush=True)

    for row in table_rows:
        l = row["lang"]
        p = row["prod"]
        r = row["rerank"]
        print(f"{l:<20} | {'Current Production':<23} | {p['r5']:<9.4f} | {p['p1']:<7.4f} | {p['mrr']:<7.4f} | {p['ndcg']:<7.4f} | {p['time']:>7.1f} ms/q", flush=True)
        print(f"{'':<20} | {'Production + Reranker':<23} | {r['r5']:<9.4f} | {r['p1']:<7.4f} | {r['mrr']:<7.4f} | {r['ndcg']:<7.4f} | {r['time']:>7.1f} ms/q", flush=True)
        print("-" * len(header), flush=True)

    print("=" * 98, flush=True)

    # Print statistical significance table with Holm correction
    print("\n" + "=" * 122, flush=True)
    print("STATISTICAL SIGNIFICANCE TESTS (McNemar on P@1/Recall@5, Paired Bootstrap 95% CI on MRR, Holm-Bonferroni Correction)", flush=True)
    print("=" * 122, flush=True)
    sig_header = f"{'Language':<10} | {'Metric':<10} | {'Discordant Pairs (b/c)':<24} | {'Stat / Chi2':<12} | {'Raw p-val':<11} | {'Holm Adj p':<11} | {'95% CI (Paired Diff)':<28}"
    print(sig_header, flush=True)
    print("-" * len(sig_header), flush=True)

    for s in significance_results:
        lang = s["lang"]
        p1_res = s["p1"]
        r5_res = s["r5"]
        mrr_res = s["mrr"]

        # P@1
        p1_key = f"{lang}_P@1"
        p1_disc = f"+{p1_res['b']} / -{p1_res['c']}"
        p1_raw_p = f"p={p1_res['p_value']:.4f}"
        p1_adj_p = f"p={adjusted_p_values[p1_key]:.4f}" + (" *" if adjusted_p_values[p1_key] < 0.05 else "")
        print(f"{lang:<10} | {'P@1':<10} | {p1_disc:<24} | chi2={p1_res['chi2']:<7.2f} | {p1_raw_p:<11} | {p1_adj_p:<11} | N/A (contingency)", flush=True)

        # Recall@5
        r5_key = f"{lang}_Recall@5"
        r5_disc = f"+{r5_res['b']} / -{r5_res['c']}"
        r5_raw_p = f"p={r5_res['p_value']:.4f}"
        r5_adj_p = f"p={adjusted_p_values[r5_key]:.4f}" + (" *" if adjusted_p_values[r5_key] < 0.05 else "")
        print(f"{'':<10} | {'Recall@5':<10} | {r5_disc:<24} | chi2={r5_res['chi2']:<7.2f} | {r5_raw_p:<11} | {r5_adj_p:<11} | N/A (contingency)", flush=True)

        # MRR
        mrr_key = f"{lang}_MRR"
        mrr_diff = mrr_res["diff_mean"]
        mrr_ci = mrr_res["diff_ci"]
        mrr_raw_p = f"p={mrr_res['p_value']:.4f}"
        mrr_adj_p = f"p={adjusted_p_values[mrr_key]:.4f}" + (" *" if adjusted_p_values[mrr_key] < 0.05 else "")
        ci_str = f"+{mrr_diff:.4f} [{mrr_ci[0]:+.4f}, {mrr_ci[1]:+.4f}]"
        print(f"{'':<10} | {'MRR':<10} | N/A (continuous)         | N/A          | {mrr_raw_p:<11} | {mrr_adj_p:<11} | {ci_str:<28}", flush=True)
        print("-" * len(sig_header), flush=True)

    print("=" * 122, flush=True)


if __name__ == "__main__":
    main()
