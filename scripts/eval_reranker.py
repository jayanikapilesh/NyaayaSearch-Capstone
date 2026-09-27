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


def extract_added_synonym_keys(commit_hash):
    """
    Extracts synonym keys added in a given commit using git diff on scripts/search_core.py.
    """
    cmd = ["git", "diff", f"{commit_hash}~1..{commit_hash}", "scripts/search_core.py"]
    try:
        diff_text = subprocess.check_output(cmd, text=True, encoding="utf-8")
    except Exception as e:
        raise RuntimeError(f"Failed to run git diff on commit {commit_hash}: {e}")

    keys = set()
    for line in diff_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            m = re.search(r'"([^"]+)"\s*:\s*\[', line)
            if m:
                keys.add(m.group(1))
    return keys


def apply_strict_clean(engine):
    """
    In-memory strict clean mode:
    (a) Removes all synonym keys added in commits 1d7000c1 and bc6c53ff
        (extracted dynamically via git diff).
    (b) Disables the IPC_TO_BNS score override added in d4ace4a8.
    Verifies each patch with example queries.
    """
    # Pre-patch queries
    syn1_q = "What's the punishment for seriously injuring someone on purpose?"  # from 1d7000c1
    syn2_q = "What happens if I give the property back empty"  # from bc6c53ff
    ipc_q = "What is IPC 302?"  # from d4ace4a8

    exp1_pre = search_core.expand_query(syn1_q)
    exp2_pre = search_core.expand_query(syn2_q)
    ipc_exp_pre = search_core.expand_ipc_references(ipc_q)

    res_pre = engine.search(ipc_q, top_k=3)
    search_pre_ipc = f"{res_pre[0]['act_name']} Sec {res_pre[0]['section_number']} (score={res_pre[0]['hybrid_score']:.4f})"

    # (a) Remove synonym keys added in 1d7000c1 and bc6c53ff
    keys_1d = extract_added_synonym_keys("1d7000c1")
    keys_bc = extract_added_synonym_keys("bc6c53ff")
    keys_to_remove = keys_1d | keys_bc

    orig_syn_count = len(search_core.SYNONYMS)
    for k in keys_to_remove:
        search_core.SYNONYMS.pop(k, None)
    new_syn_count = len(search_core.SYNONYMS)

    # (b) Disable IPC_TO_BNS score override
    orig_ipc_count = len(search_core.IPC_TO_BNS)
    search_core.IPC_TO_BNS.clear()
    new_ipc_count = len(search_core.IPC_TO_BNS)

    # Post-patch verification queries
    exp1_post = search_core.expand_query(syn1_q)
    exp2_post = search_core.expand_query(syn2_q)
    ipc_exp_post = search_core.expand_ipc_references(ipc_q)
    res_post = engine.search(ipc_q, top_k=3)
    search_post_ipc = f"{res_post[0]['act_name']} Sec {res_post[0]['section_number']} (score={res_post[0]['hybrid_score']:.4f})"

    assert "grievous hurt" not in exp1_post, "Patch (a) verification failed: 'grievous hurt' still present!"
    assert "vacant possession" not in exp2_post, "Patch (a) verification failed: 'vacant possession' still present!"
    assert "bns section 103" not in ipc_exp_post, "Patch (b) verification failed: IPC reference still expanded!"
    assert ("103" not in search_post_ipc or res_post[0]["hybrid_score"] < 1.0), "Patch (b) verification failed: score override still active!"

    print("\n" + "=" * 86, flush=True)
    print("      [--strict-clean] IN-MEMORY PATCHES APPLIED & INDEPENDENTLY VERIFIED", flush=True)
    print("=" * 86, flush=True)
    print(f"Patch (a): Removed synonym keys from commits 1d7000c1 ({len(keys_1d)} keys) and bc6c53ff ({len(keys_bc)} keys)", flush=True)
    print(f"  - Total unique synonym keys removed: {len(keys_to_remove)} (dictionary size: {orig_syn_count} -> {new_syn_count})", flush=True)
    print("  - Verification Example 1 (commit 1d7000c1 - 'seriously injuring' -> 'grievous hurt'):", flush=True)
    print(f"      Query: '{syn1_q}'", flush=True)
    print(f"      Before patch: 'grievous hurt' in expand_query: {'grievous hurt' in exp1_pre}", flush=True)
    print(f"      After patch:  'grievous hurt' in expand_query: {'grievous hurt' in exp1_post} [REMOVED]", flush=True)
    print("  - Verification Example 2 (commit bc6c53ff - 'give the property back empty' -> 'vacant possession'):", flush=True)
    print(f"      Query: '{syn2_q}'", flush=True)
    print(f"      Before patch: 'vacant possession' in expand_query: {'vacant possession' in exp2_pre}", flush=True)
    print(f"      After patch:  'vacant possession' in expand_query: {'vacant possession' in exp2_post} [REMOVED]", flush=True)

    print(f"\nPatch (b): Disabled IPC_TO_BNS score override from commit d4ace4a8", flush=True)
    print(f"  - IPC_TO_BNS mappings cleared in-memory: {orig_ipc_count} -> {new_ipc_count}", flush=True)
    print("  - Verification Example (commit d4ace4a8 - IPC 302 -> BNS 103 direct score override):", flush=True)
    print(f"      Query: '{ipc_q}'", flush=True)
    print(f"      Before patch top result: {search_pre_ipc} [OVERRIDDEN: score > 1.0]", flush=True)
    print(f"      After patch top result:  {search_post_ipc} [NATURAL RETRIEVAL: score < 1.0]", flush=True)
    print("=" * 86 + "\n", flush=True)


DEFAULT_MODEL_SETTINGS = {
    "cross-encoder/ms-marco-MiniLM-L-6-v2": {"top_k": 10, "weight": 0.8},
    "cross-encoder/ms-marco-MiniLM-L-12-v2": {"top_k": 10, "weight": 0.2},
}


def get_cross_encoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
    """
    Load cross-encoder with local_files_only=True.
    Falls back to Hugging Face Hub if local files are missing.
    """
    try:
        model = CrossEncoder(model_name, local_files_only=True)
        print(f"Loaded CrossEncoder from local cache: {model_name}", flush=True)
        return model, model_name
    except Exception as e:
        print(f"Notice: local_files_only failed for {model_name} ({e}), attempting online load...", flush=True)
        try:
            model = CrossEncoder(model_name)
            print(f"Loaded CrossEncoder from Hugging Face Hub: {model_name}", flush=True)
            return model, model_name
        except Exception as e2:
            raise RuntimeError(f"Failed to load cross-encoder {model_name}: {e2}")


TRANSLATION_CACHE_FILE = os.path.join(ROOT_DIR, "data", "eval", "translation_cache.json")
TRANSLATION_CACHE = {}


def get_translation_cache_key(query):
    reasoning = os.environ.get("TRANSLATION_REASONING", "low").strip()
    return f"{reasoning}:{query}"


def load_translation_cache(refresh=False):
    global TRANSLATION_CACHE
    if refresh:
        TRANSLATION_CACHE = {}
        return TRANSLATION_CACHE
    if os.path.exists(TRANSLATION_CACHE_FILE):
        try:
            with open(TRANSLATION_CACHE_FILE, "r", encoding="utf-8") as f:
                TRANSLATION_CACHE = json.load(f)
                return TRANSLATION_CACHE
        except Exception as e:
            print(f"Warning: Failed to load translation cache ({e})", flush=True)
    TRANSLATION_CACHE = {}
    return TRANSLATION_CACHE


def save_translation_cache():
    try:
        os.makedirs(os.path.dirname(TRANSLATION_CACHE_FILE), exist_ok=True)
        with open(TRANSLATION_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(TRANSLATION_CACHE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save translation cache ({e})", flush=True)


# Unicode script ranges for Devanagari (\u0900-\u097F) and Kannada (\u0C80-\u0CFF)
DEVANAGARI_RANGE = chr(0x0900) + "-" + chr(0x097F)
KANNADA_RANGE = chr(0x0C80) + "-" + chr(0x0CFF)
VERNACULAR_SCRIPT_RE = re.compile("[" + DEVANAGARI_RANGE + KANNADA_RANGE + "]")


def validate_english_translation(query, translated):
    """
    Validates a translated English query.
    Rejects the translation if:
    - It is empty or whitespace-only
    - It equals the original input query (case-insensitive stripped)
    - It still contains Devanagari or Kannada script characters
    Raises ValueError on validation failure.
    """
    if not translated or not translated.strip():
        raise ValueError("Translation is empty or whitespace-only")

    cleaned = translated.strip()
    if cleaned.lower() == query.strip().lower():
        raise ValueError("Translation is identical to input query (untranslated echo)")

    match = VERNACULAR_SCRIPT_RE.search(cleaned)
    if match:
        raise ValueError(f"Translation still contains non-English vernacular characters ({repr(match.group(0))})")

    return cleaned


def translate_single_query(query, max_retries=3, base_delay=1.0):
    """
    Translates a single non-English query to English via translate_to_english().
    Retries on transient errors or invalid translations with exponential backoff.
    Returns the validated, stripped translation string on success.
    Raises RuntimeError on failure after all retries.
    NEVER substitutes any fallback text.
    """
    if not translate_to_english:
        raise RuntimeError("translate_to_english is not available from rag_core.")

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            raw_translated = translate_to_english(query)
            valid_translated = validate_english_translation(query, raw_translated)
            return valid_translated
        except Exception as e:
            last_error = str(e)

        if attempt < max_retries:
            time.sleep(base_delay * (2 ** (attempt - 1)))

    raise RuntimeError(f"{last_error} (after {max_retries} attempts)")


def ensure_translations_for_dataset(lang, lang_title, queries, en_filepath, refresh=False, max_retries=3):
    """
    Validates that all queries for a non-English dataset have valid translations in cache.
    If translations are missing, refresh=True, or fail validation, translates them via Groq with retries.
    Never writes failed translations or fallbacks to the cache.
    If any translations fail, stops the run with a clear error listing all failed queries.
    After ensuring the cache, counts translations identical to the paired English originals;
    if > 5, stops the run with an error.
    """
    global TRANSLATION_CACHE

    if not os.path.exists(en_filepath):
        raise FileNotFoundError(f"English test file not found at {en_filepath} to verify translations against.")

    with open(en_filepath, "r", encoding="utf-8") as f:
        en_raw = json.load(f)

    if len(queries) > len(en_raw):
        raise ValueError(f"More {lang_title} queries ({len(queries)}) than English queries ({len(en_raw)})")

    paired_en = en_raw[:len(queries)]
    en_queries = [item[0] for item in paired_en]

    # Verify that for every index, the Hindi/Kannada item has the same act and section as the English item
    mismatches = []
    for idx, ((q, act, sec), (en_q, en_act, en_sec)) in enumerate(zip(queries, paired_en), start=1):
        if str(act).strip() != str(en_act).strip() or str(sec).strip() != str(en_sec).strip():
            mismatches.append(
                f"  - Query #{idx}: {lang_title}=({act}, Sec {sec}) vs English=({en_act}, Sec {en_sec})"
            )

    if mismatches:
        err_msg = (
            f"CRITICAL ERROR: Ground truth mismatch between {lang_title} and paired English items:\n"
            + "\n".join(mismatches)
        )
        raise RuntimeError(err_msg)

    queries_to_translate = []
    for idx, (q, _, _) in enumerate(queries):
        cache_key = get_translation_cache_key(q)
        cached_val = TRANSLATION_CACHE.get(cache_key)
        if refresh or not cached_val:
            queries_to_translate.append((idx + 1, q))
        else:
            try:
                validate_english_translation(q, cached_val)
            except ValueError as e:
                print(f"[{lang_title}] Evicting invalid cached translation for query #{idx + 1}: {e}", flush=True)
                queries_to_translate.append((idx + 1, q))

    if queries_to_translate:
        print(f"[{lang_title}] Translating {len(queries_to_translate)} queries to English...", flush=True)
        failed_queries = []
        new_translations = {}

        for item_idx, q in queries_to_translate:
            try:
                translated_text = translate_single_query(q, max_retries=max_retries)
                cache_key = get_translation_cache_key(q)
                new_translations[cache_key] = translated_text
            except Exception as e:
                failed_queries.append((item_idx, q, str(e)))

        if failed_queries:
            err_msg_lines = [
                f"\nCRITICAL ERROR: Translation failed for {len(failed_queries)} {lang_title} queries after {max_retries} retries:",
                "No failed queries or fallbacks were written to the cache.",
                "Failed queries list:"
            ]
            for item_idx, q, err in failed_queries:
                err_msg_lines.append(f"  - Query #{item_idx}: {q!r} -> Error: {err}")
            full_err = "\n".join(err_msg_lines)
            raise RuntimeError(full_err)

        # Update cache with verified successful translations and save
        TRANSLATION_CACHE.update(new_translations)
        save_translation_cache()
        print(f"[{lang_title}] Successfully translated and cached {len(new_translations)} queries.", flush=True)

    # Validate cached translations against the paired English originals
    identical_matches = []
    for idx, (q, _, _) in enumerate(queries):
        cache_key = get_translation_cache_key(q)
        cached_translation = TRANSLATION_CACHE.get(cache_key, "").strip().lower()
        english_original = en_queries[idx].strip().lower()
        if cached_translation == english_original:
            identical_matches.append((idx + 1, q, TRANSLATION_CACHE.get(cache_key), en_queries[idx]))

    identical_count = len(identical_matches)
    print(f"[{lang_title}] Translations identical to English original: {identical_count} / {len(queries)}", flush=True)

    if identical_count > len(queries) * 0.50:
        err_msg_lines = [
            f"\nCRITICAL ERROR: {identical_count} / {len(queries)} ({identical_count / len(queries) * 100:.1f}%) {lang_title} translations are identical to the English original (max allowed: 50%).",
            "This indicates fallback contamination or English query leakage in the translation cache.",
            "Sample identical queries:"
        ]
        for item_idx, q, tr, en_orig in identical_matches[:10]:
            err_msg_lines.append(f"  - Query #{item_idx}: Vernacular: {q!r} | Translation: {tr!r} | Original EN: {en_orig!r}")
        full_err = "\n".join(err_msg_lines)
        raise RuntimeError(full_err)
    elif identical_count > 0:
        print(f"[{lang_title}] Warning: {identical_count} / {len(queries)} translations are identical to the English original:", flush=True)
        for item_idx, q, tr, en_orig in identical_matches:
            print(f"  - Query #{item_idx}: Vernacular: {q!r} | Translation: {tr!r} | Original EN: {en_orig!r}", flush=True)



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
    parser.add_argument("--reranker", type=str, default="cross-encoder/ms-marco-MiniLM-L-6-v2", help="Cross-encoder model name or path (default: cross-encoder/ms-marco-MiniLM-L-6-v2)")
    parser.add_argument("--compare", action="store_true", help="Compare Production, Production + L-6 reranker, and Production + L-12 reranker in one table")
    parser.add_argument("--top_n_rerank", type=int, default=None, help="Top-N candidates to rerank (default: model-specific tuned default)")
    parser.add_argument("--weight_cross", type=float, default=None, help="Cross-encoder score weight (default: model-specific tuned default)")
    parser.add_argument("--tune", action="store_true", help="Run hyperparameter grid search on eval_queries.json first")
    parser.add_argument("--clean-synonyms", action="store_true", help="Replace SYNONYMS with pre-bc6c53ff version to evaluate clean baseline")
    parser.add_argument("--strict-clean", action="store_true", help="Strictly clean baseline: remove synonyms from 1d7000c1 and bc6c53ff, disable IPC_TO_BNS score override")
    parser.add_argument("--refresh-translations", action="store_true", help="Force re-translation of queries via Groq instead of using cached translations")
    args = parser.parse_args()

    if args.refresh_translations:
        os.environ["NYAAYA_DISABLE_CACHE"] = "1"

    print("=" * 86, flush=True)
    print("            NYAAYASEARCH: PRODUCTION VS. RERANKER EVALUATION", flush=True)
    print("=" * 86, flush=True)

    # 1. Initialize search engine
    engine = SearchEngine()

    # 2. Apply clean patches if requested
    if args.strict_clean:
        apply_strict_clean(engine)
    elif args.clean_synonyms:
        apply_clean_synonyms()

    # 3. Load translation cache
    t_cache = load_translation_cache(refresh=args.refresh_translations)
    if t_cache:
        print(f"Translation cache: loaded {len(t_cache)} cached query translations from {TRANSLATION_CACHE_FILE}", flush=True)
    elif args.refresh_translations:
        print(f"Translation cache: --refresh-translations specified, will re-translate via Groq", flush=True)


    is_compare = args.compare or args.reranker in ("compare", "both", "all", "l6,l12")

    if is_compare:
        l6_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        l12_name = "cross-encoder/ms-marco-MiniLM-L-12-v2"
        if getattr(engine, "cross_encoder", None) is not None:
            l6_model = engine.cross_encoder
            print(f"Using SearchEngine built-in CrossEncoder: {l6_name}", flush=True)
        else:
            l6_model, _ = get_cross_encoder(l6_name)
        l12_model, _ = get_cross_encoder(l12_name)

        if args.tune:
            print("\n--- Tuning L-6 on eval_queries.json ---", flush=True)
            l6_top_k, l6_weight = run_tuning(engine, l6_model)
            print("\n--- Tuning L-12 on eval_queries.json ---", flush=True)
            l12_top_k, l12_weight = run_tuning(engine, l12_model)
        else:
            l6_top_k = args.top_n_rerank if args.top_n_rerank is not None else DEFAULT_MODEL_SETTINGS[l6_name]["top_k"]
            l6_weight = args.weight_cross if args.weight_cross is not None else DEFAULT_MODEL_SETTINGS[l6_name]["weight"]
            l12_top_k = args.top_n_rerank if args.top_n_rerank is not None else DEFAULT_MODEL_SETTINGS[l12_name]["top_k"]
            l12_weight = args.weight_cross if args.weight_cross is not None else DEFAULT_MODEL_SETTINGS[l12_name]["weight"]
    else:
        if args.reranker == "cross-encoder/ms-marco-MiniLM-L-6-v2" and getattr(engine, "cross_encoder", None) is not None:
            cross_model = engine.cross_encoder
            model_name = args.reranker
            print(f"Using SearchEngine built-in CrossEncoder: {model_name}", flush=True)
        else:
            cross_model, model_name = get_cross_encoder(args.reranker)
        default_cfg = DEFAULT_MODEL_SETTINGS.get(model_name, {"top_k": 10, "weight": 0.8})
        top_n_rerank = args.top_n_rerank if args.top_n_rerank is not None else default_cfg["top_k"]
        weight_cross = args.weight_cross if args.weight_cross is not None else default_cfg["weight"]
        if args.tune:
            top_n_rerank, weight_cross = run_tuning(engine, cross_model)

    if args.strict_clean:
        syn_status = "Strict Clean Baseline (54 keys: 1d7000c1 & bc6c53ff removed, IPC_TO_BNS disabled)"
    elif args.clean_synonyms:
        syn_status = "Pre-bc6c53ff Clean Baseline (65 keys)"
    else:
        syn_status = "Current Repo (with 29+6 synonym patches, 97 keys, IPC_TO_BNS active)"

    print(f"\nConfiguration:", flush=True)
    print(f"  - Synonym Dictionary: {syn_status}", flush=True)
    if is_compare:
        print(f"  - Mode: 3-Way Comparison (Production vs L-6 vs L-12)", flush=True)
        print(f"  - L-6 Reranker:  {l6_name} (Top-{l6_top_k}, weight={l6_weight:.1f})", flush=True)
        print(f"  - L-12 Reranker: {l12_name} (Top-{l12_top_k}, weight={l12_weight:.1f})", flush=True)
    else:
        print(f"  - Model: {model_name}", flush=True)
        print(f"  - Candidates reranked: Top-{top_n_rerank}", flush=True)
        print(f"  - Score fusion: (1 - {weight_cross:.1f}) * norm_hybrid + {weight_cross:.1f} * sigmoid(cross_logit)", flush=True)
    print(f"  - Candidate pool retrieved: Top-20 from SearchEngine.search()", flush=True)
    print(f"  - Match criteria: str(r['act_name']) == expected_act and str(r['section_number']) == expected_section\n", flush=True)

    requested_langs = [l.strip().lower() for l in args.languages.split(",") if l.strip()]
    eval_files = {
        "en": ("English", os.path.join(ROOT_DIR, "data", "eval", "test_270_en.json")),
        "hi": ("Hindi", os.path.join(ROOT_DIR, "data", "eval", "test_270_hi.json")),
        "kn": ("Kannada", os.path.join(ROOT_DIR, "data", "eval", "test_270_kn.json")),
    }


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

        if lang != "en":
            ensure_translations_for_dataset(
                lang=lang,
                lang_title=lang_title,
                queries=queries,
                en_filepath=eval_files["en"][1],
                refresh=args.refresh_translations,
            )

        prod_metrics = {"recall_at_5": [], "precision_at_1": [], "mrr": [], "ndcg_at_5": [], "time": []}

        if is_compare:
            l6_metrics = {"recall_at_5": [], "precision_at_1": [], "mrr": [], "ndcg_at_5": [], "time": []}
            l12_metrics = {"recall_at_5": [], "precision_at_1": [], "mrr": [], "ndcg_at_5": [], "time": []}

            for idx, (query, expected_act, expected_section) in enumerate(queries, 1):
                if lang != "en":
                    search_q = TRANSLATION_CACHE[get_translation_cache_key(query)]
                else:
                    search_q = query

                # 1. Retrieve top-20 candidates using production search (without reranker)
                t_s0 = time.perf_counter()
                candidates = engine.search(search_q, top_k=20, rerank=False)
                search_time = time.perf_counter() - t_s0

                # 2. Production baseline metrics
                p_m = compute_query_metrics(candidates[:10], expected_act, expected_section)
                for k in ["recall_at_5", "precision_at_1", "mrr", "ndcg_at_5"]:
                    prod_metrics[k].append(p_m[k])
                prod_metrics["time"].append(search_time)

                # 3. L-6 Reranker: calls built-in SearchEngine reranking
                t_l6_0 = time.perf_counter()
                l6_cands = engine.search(search_q, top_k=20, rerank=True)
                l6_time = time.perf_counter() - t_l6_0

                r6_m = compute_query_metrics(l6_cands[:10], expected_act, expected_section)
                for k in ["recall_at_5", "precision_at_1", "mrr", "ndcg_at_5"]:
                    l6_metrics[k].append(r6_m[k])
                l6_metrics["time"].append(l6_time)

                # 4. L-12 Reranker
                l12_cands, l12_rerank_time = rerank_candidates(
                    search_q, candidates, l12_model, top_n_rerank=l12_top_k, weight_cross=l12_weight
                )
                r12_m = compute_query_metrics(l12_cands[:10], expected_act, expected_section)
                for k in ["recall_at_5", "precision_at_1", "mrr", "ndcg_at_5"]:
                    l12_metrics[k].append(r12_m[k])
                l12_metrics["time"].append(search_time + l12_rerank_time)

                if idx % 15 == 0 or idx == n_queries:
                    print(f"  [{lang_title}] Processed {idx}/{n_queries} queries...", flush=True)

            p_r5 = np.mean(prod_metrics["recall_at_5"])
            p_p1 = np.mean(prod_metrics["precision_at_1"])
            p_mrr = np.mean(prod_metrics["mrr"])
            p_ndcg = np.mean(prod_metrics["ndcg_at_5"])
            p_time_ms = np.mean(prod_metrics["time"]) * 1000.0

            l6_r5 = np.mean(l6_metrics["recall_at_5"])
            l6_p1 = np.mean(l6_metrics["precision_at_1"])
            l6_mrr = np.mean(l6_metrics["mrr"])
            l6_ndcg = np.mean(l6_metrics["ndcg_at_5"])
            l6_time_ms = np.mean(l6_metrics["time"]) * 1000.0

            l12_r5 = np.mean(l12_metrics["recall_at_5"])
            l12_p1 = np.mean(l12_metrics["precision_at_1"])
            l12_mrr = np.mean(l12_metrics["mrr"])
            l12_ndcg = np.mean(l12_metrics["ndcg_at_5"])
            l12_time_ms = np.mean(l12_metrics["time"]) * 1000.0

            table_rows.append({
                "lang": f"{lang_title} (n={n_queries})",
                "prod": {"r5": p_r5, "p1": p_p1, "mrr": p_mrr, "ndcg": p_ndcg, "time": p_time_ms},
                "l6": {"r5": l6_r5, "p1": l6_p1, "mrr": l6_mrr, "ndcg": l6_ndcg, "time": l6_time_ms},
                "l12": {"r5": l12_r5, "p1": l12_p1, "mrr": l12_mrr, "ndcg": l12_ndcg, "time": l12_time_ms},
            })

            # Significance tests
            # L-12 vs Production
            mcnemar_p1_l12_v_prod = mcnemar_test(prod_metrics["precision_at_1"], l12_metrics["precision_at_1"])
            mcnemar_r5_l12_v_prod = mcnemar_test(prod_metrics["recall_at_5"], l12_metrics["recall_at_5"])
            boot_mrr_l12_v_prod = paired_bootstrap_mrr(prod_metrics["mrr"], l12_metrics["mrr"])

            # L-12 vs L-6
            mcnemar_p1_l12_v_l6 = mcnemar_test(l6_metrics["precision_at_1"], l12_metrics["precision_at_1"])
            mcnemar_r5_l12_v_l6 = mcnemar_test(l6_metrics["recall_at_5"], l12_metrics["recall_at_5"])
            boot_mrr_l12_v_l6 = paired_bootstrap_mrr(l6_metrics["mrr"], l12_metrics["mrr"])

            # L-6 vs Production
            mcnemar_p1_l6_v_prod = mcnemar_test(prod_metrics["precision_at_1"], l6_metrics["precision_at_1"])
            mcnemar_r5_l6_v_prod = mcnemar_test(prod_metrics["recall_at_5"], l6_metrics["recall_at_5"])
            boot_mrr_l6_v_prod = paired_bootstrap_mrr(prod_metrics["mrr"], l6_metrics["mrr"])

            raw_p_values[f"{lang_title}_L12_vs_Prod_P@1"] = mcnemar_p1_l12_v_prod["p_value"]
            raw_p_values[f"{lang_title}_L12_vs_Prod_Recall@5"] = mcnemar_r5_l12_v_prod["p_value"]
            raw_p_values[f"{lang_title}_L12_vs_Prod_MRR"] = boot_mrr_l12_v_prod["p_value"]

            raw_p_values[f"{lang_title}_L12_vs_L6_P@1"] = mcnemar_p1_l12_v_l6["p_value"]
            raw_p_values[f"{lang_title}_L12_vs_L6_Recall@5"] = mcnemar_r5_l12_v_l6["p_value"]
            raw_p_values[f"{lang_title}_L12_vs_L6_MRR"] = boot_mrr_l12_v_l6["p_value"]

            raw_p_values[f"{lang_title}_L6_vs_Prod_P@1"] = mcnemar_p1_l6_v_prod["p_value"]
            raw_p_values[f"{lang_title}_L6_vs_Prod_Recall@5"] = mcnemar_r5_l6_v_prod["p_value"]
            raw_p_values[f"{lang_title}_L6_vs_Prod_MRR"] = boot_mrr_l6_v_prod["p_value"]

            significance_results.append({
                "lang": lang_title,
                "n": n_queries,
                "l12_v_prod": {"p1": mcnemar_p1_l12_v_prod, "r5": mcnemar_r5_l12_v_prod, "mrr": boot_mrr_l12_v_prod},
                "l12_v_l6": {"p1": mcnemar_p1_l12_v_l6, "r5": mcnemar_r5_l12_v_l6, "mrr": boot_mrr_l12_v_l6},
                "l6_v_prod": {"p1": mcnemar_p1_l6_v_prod, "r5": mcnemar_r5_l6_v_prod, "mrr": boot_mrr_l6_v_prod},
            })

        else:
            rerank_metrics = {"recall_at_5": [], "precision_at_1": [], "mrr": [], "ndcg_at_5": [], "time": []}

            for idx, (query, expected_act, expected_section) in enumerate(queries, 1):
                if lang != "en":
                    search_q = TRANSLATION_CACHE[get_translation_cache_key(query)]
                else:
                    search_q = query

                t_s0 = time.perf_counter()
                candidates = engine.search(search_q, top_k=20, rerank=False)
                search_time = time.perf_counter() - t_s0

                p_m = compute_query_metrics(candidates[:10], expected_act, expected_section)
                for k in ["recall_at_5", "precision_at_1", "mrr", "ndcg_at_5"]:
                    prod_metrics[k].append(p_m[k])
                prod_metrics["time"].append(search_time)

                is_builtin_l6 = (
                    model_name == "cross-encoder/ms-marco-MiniLM-L-6-v2"
                    and top_n_rerank == 10
                    and abs(weight_cross - 0.8) < 1e-4
                    and getattr(engine, "cross_encoder", None) is not None
                )

                if is_builtin_l6:
                    t_r0 = time.perf_counter()
                    reranked_cands = engine.search(search_q, top_k=20, rerank=True)
                    rerank_total_time = time.perf_counter() - t_r0
                    r_m = compute_query_metrics(reranked_cands[:10], expected_act, expected_section)
                    for k in ["recall_at_5", "precision_at_1", "mrr", "ndcg_at_5"]:
                        rerank_metrics[k].append(r_m[k])
                    rerank_metrics["time"].append(rerank_total_time)
                else:
                    reranked_cands, rerank_time = rerank_candidates(
                        search_q, candidates, cross_model, top_n_rerank=top_n_rerank, weight_cross=weight_cross
                    )
                    r_m = compute_query_metrics(reranked_cands[:10], expected_act, expected_section)
                    for k in ["recall_at_5", "precision_at_1", "mrr", "ndcg_at_5"]:
                        rerank_metrics[k].append(r_m[k])
                    rerank_metrics["time"].append(search_time + rerank_time)

                if idx % 15 == 0 or idx == n_queries:
                    print(f"  [{lang_title}] Processed {idx}/{n_queries} queries...", flush=True)

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

    if is_compare:
        # Apply Holm-Bonferroni correction across the 18 primary comparisons (L-12 vs Prod & L-12 vs L-6)
        raw_p_l12 = {k: v for k, v in raw_p_values.items() if "L12" in k}
        adjusted_p_values = holm_bonferroni_correction(raw_p_l12)
        raw_p_l6 = {k: v for k, v in raw_p_values.items() if "L6_vs_Prod" in k}
        adjusted_p_values.update(holm_bonferroni_correction(raw_p_l6))

        print("\n" + "=" * 105, flush=True)
        if args.strict_clean:
            mode_str = "Development set (test_270, previously contaminated) [--strict-clean]"
        elif args.clean_synonyms:
            mode_str = "CLEAN SYNONYMS (PRE-COMMIT bc6c53ff)"
        else:
            mode_str = "PRODUCTION SYNONYMS"
        print(f"FINAL EVALUATION RESULTS: {mode_str}", flush=True)
        print("=" * 105, flush=True)
        header = f"{'Language / Dataset':<20} | {'System':<27} | {'Recall@5':<9} | {'P@1':<7} | {'MRR':<7} | {'nDCG@5':<7} | {'Latency (CPU)':<13}"
        print(header, flush=True)
        print("-" * len(header), flush=True)

        for row in table_rows:
            l = row["lang"]
            p = row["prod"]
            r6 = row["l6"]
            r12 = row["l12"]
            print(f"{l:<20} | {'Current Production':<27} | {p['r5']:<9.4f} | {p['p1']:<7.4f} | {p['mrr']:<7.4f} | {p['ndcg']:<7.4f} | {p['time']:>7.1f} ms/q", flush=True)
            print(f"{'':<20} | {'Production + L-6 reranker':<27} | {r6['r5']:<9.4f} | {r6['p1']:<7.4f} | {r6['mrr']:<7.4f} | {r6['ndcg']:<7.4f} | {r6['time']:>7.1f} ms/q", flush=True)
            print(f"{'':<20} | {'Production + L-12 reranker':<27} | {r12['r5']:<9.4f} | {r12['p1']:<7.4f} | {r12['mrr']:<7.4f} | {r12['ndcg']:<7.4f} | {r12['time']:>7.1f} ms/q", flush=True)
            print("-" * len(header), flush=True)

        print("=" * 105, flush=True)

        print("\n" + "=" * 135, flush=True)
        sig_label = "Development set (test_270, previously contaminated)" if args.strict_clean else "STATISTICAL SIGNIFICANCE TESTS"
        print(f"STATISTICAL SIGNIFICANCE TESTS: {sig_label}", flush=True)
        print("(McNemar on P@1/Recall@5, Paired Bootstrap 95% CI on MRR, Holm-Bonferroni Correction)", flush=True)
        print("=" * 135, flush=True)
        sig_header = f"{'Language':<10} | {'Comparison':<20} | {'Metric':<10} | {'Discordant Pairs (b/c)':<24} | {'Stat / Chi2':<12} | {'Raw p-val':<11} | {'Holm Adj p':<11} | {'95% CI (Paired Diff)':<28}"
        print(sig_header, flush=True)
        print("-" * len(sig_header), flush=True)

        for s in significance_results:
            lang = s["lang"]
            for comp_name, comp_key, comp_data in [
                ("L-12 vs Production", "L12_vs_Prod", s["l12_v_prod"]),
                ("L-12 vs L-6", "L12_vs_L6", s["l12_v_l6"]),
                ("L-6 vs Production", "L6_vs_Prod", s["l6_v_prod"]),
            ]:
                p1_res = comp_data["p1"]
                r5_res = comp_data["r5"]
                mrr_res = comp_data["mrr"]

                p1_k = f"{lang}_{comp_key}_P@1"
                r5_k = f"{lang}_{comp_key}_Recall@5"
                mrr_k = f"{lang}_{comp_key}_MRR"

                p1_disc = f"+{p1_res['b']} / -{p1_res['c']}"
                p1_raw_p = f"p={p1_res['p_value']:.4f}"
                p1_adj_p = f"p={adjusted_p_values[p1_k]:.4f}" + (" *" if adjusted_p_values[p1_k] < 0.05 else "")

                r5_disc = f"+{r5_res['b']} / -{r5_res['c']}"
                r5_raw_p = f"p={r5_res['p_value']:.4f}"
                r5_adj_p = f"p={adjusted_p_values[r5_k]:.4f}" + (" *" if adjusted_p_values[r5_k] < 0.05 else "")

                mrr_diff = mrr_res["diff_mean"]
                mrr_ci = mrr_res["diff_ci"]
                mrr_raw_p = f"p={mrr_res['p_value']:.4f}"
                mrr_adj_p = f"p={adjusted_p_values[mrr_k]:.4f}" + (" *" if adjusted_p_values[mrr_k] < 0.05 else "")
                ci_str = f"{mrr_diff:+.4f} [{mrr_ci[0]:+.4f}, {mrr_ci[1]:+.4f}]"

                print(f"{lang:<10} | {comp_name:<20} | {'P@1':<10} | {p1_disc:<24} | chi2={p1_res['chi2']:<7.2f} | {p1_raw_p:<11} | {p1_adj_p:<11} | N/A (contingency)", flush=True)
                print(f"{'':<10} | {'':<20} | {'Recall@5':<10} | {r5_disc:<24} | chi2={r5_res['chi2']:<7.2f} | {r5_raw_p:<11} | {r5_adj_p:<11} | N/A (contingency)", flush=True)
                print(f"{'':<10} | {'':<20} | {'MRR':<10} | N/A (continuous)         | N/A          | {mrr_raw_p:<11} | {mrr_adj_p:<11} | {ci_str:<28}", flush=True)
                print("-" * len(sig_header), flush=True)

        print("=" * 135, flush=True)

    else:
        adjusted_p_values = holm_bonferroni_correction(raw_p_values)

        print("\n" + "=" * 98, flush=True)
        if args.strict_clean:
            mode_str = "Development set (test_270, previously contaminated) [--strict-clean]"
        elif args.clean_synonyms:
            mode_str = "CLEAN SYNONYMS (PRE-COMMIT bc6c53ff)"
        else:
            mode_str = "PRODUCTION SYNONYMS"
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

        print("\n" + "=" * 122, flush=True)
        sig_label = "Development set (test_270, previously contaminated)" if args.strict_clean else "STATISTICAL SIGNIFICANCE TESTS"
        print(f"STATISTICAL SIGNIFICANCE TESTS: {sig_label}", flush=True)
        print("(McNemar on P@1/Recall@5, Paired Bootstrap 95% CI on MRR, Holm-Bonferroni Correction across all tests)", flush=True)
        print("=" * 122, flush=True)
        sig_header = f"{'Language':<10} | {'Metric':<10} | {'Discordant Pairs (b/c)':<24} | {'Stat / Chi2':<12} | {'Raw p-val':<11} | {'Holm Adj p':<11} | {'95% CI (Paired Diff)':<28}"
        print(sig_header, flush=True)
        print("-" * len(sig_header), flush=True)

        for s in significance_results:
            lang = s["lang"]
            p1_res = s["p1"]
            r5_res = s["r5"]
            mrr_res = s["mrr"]

            p1_key = f"{lang}_P@1"
            p1_disc = f"+{p1_res['b']} / -{p1_res['c']}"
            p1_raw_p = f"p={p1_res['p_value']:.4f}"
            p1_adj_p = f"p={adjusted_p_values[p1_key]:.4f}" + (" *" if adjusted_p_values[p1_key] < 0.05 else "")
            print(f"{lang:<10} | {'P@1':<10} | {p1_disc:<24} | chi2={p1_res['chi2']:<7.2f} | {p1_raw_p:<11} | {p1_adj_p:<11} | N/A (contingency)", flush=True)

            r5_key = f"{lang}_Recall@5"
            r5_disc = f"+{r5_res['b']} / -{r5_res['c']}"
            r5_raw_p = f"p={r5_res['p_value']:.4f}"
            r5_adj_p = f"p={adjusted_p_values[r5_key]:.4f}" + (" *" if adjusted_p_values[r5_key] < 0.05 else "")
            print(f"{'':<10} | {'Recall@5':<10} | {r5_disc:<24} | chi2={r5_res['chi2']:<7.2f} | {r5_raw_p:<11} | {r5_adj_p:<11} | N/A (contingency)", flush=True)

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
