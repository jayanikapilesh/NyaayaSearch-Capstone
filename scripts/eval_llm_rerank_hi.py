"""
Experiment: does an LLM rerank of the top-20 candidates beat the current
production system (--strict-clean settings + L-6 cross-encoder reranker)?

Pipeline per query:
  1. engine.search(query, top_k=20, rerank=True) -> 20 candidates.
  2. LLM (openai/gpt-oss-120b, temperature 0, reasoning_effort low) reads the
     question + a numbered list of "act name, section number, section title"
     and returns the 5 most relevant candidate numbers as JSON, best first.
  3. Compare baseline (top 5 of the 20) vs LLM-reranked top 5 on Recall@5,
     P@1, MRR, a McNemar test on Recall@5, and report the top-20 "ceiling".

Does NOT modify search_core.py, the live app, or any test files.
Every LLM reply is cached to ../data/eval/llm_rerank_cache.json so reruns are free.
Uses GROQ_API_KEY_EVAL if set, else GROQ_API_KEY. Don't commit this run's outputs.
"""

import os
import sys
import json
import time
import argparse

import numpy as np
import groq
from groq import Groq
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from search_core import SearchEngine
from eval_reranker import apply_strict_clean

load_dotenv()

CACHE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "eval", "llm_rerank_cache.json"))
TEST_SET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "eval", "test_270_hi_as_en.json"))
MODEL = "openai/gpt-oss-120b"

client = Groq(api_key=os.environ.get("GROQ_API_KEY_EVAL") or os.environ.get("GROQ_API_KEY"))


def _is_daily_limit_error(e: Exception) -> bool:
    msg = str(e).lower()
    body_str = ""
    if hasattr(e, "body"):
        try:
            body_str = str(e.body).lower()
        except Exception:
            pass
    combined = f"{msg} {body_str}"
    indicators = ("tokens per day", "tokens-per-day", "tokens_per_day", "tpd", "daily limit", "daily-limit", "daily_limit", "day limit")
    return any(ind in combined for ind in indicators)


def load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    tmp_path = CACHE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, CACHE_PATH)


def make_cache_key(query, candidates):
    cand_key = [[str(c.get("act_name") or ""), str(c.get("section_number") or "")] for c in candidates]
    return json.dumps(["v1", MODEL, query.strip().lower(), cand_key], ensure_ascii=False)


SYSTEM_PROMPT = (
    "You are given a legal question and a numbered list of candidate law sections "
    "(act name, section number, section title only). Pick the 5 candidates most "
    "relevant to answering the question, best first. "
    "Return ONLY a JSON object of the form {\"top5\": [n1, n2, n3, n4, n5]} using the "
    "candidate numbers shown, nothing else."
)


def build_candidate_list(candidates):
    lines = []
    for i, c in enumerate(candidates, start=1):
        act = str(c.get("act_name") or "").strip()
        sec = str(c.get("section_number") or "").strip()
        title = str(c.get("section_title") or "").strip()
        lines.append(f"{i}. {act}, Section {sec}: {title}")
    return "\n".join(lines)


def parse_top5(content, n_candidates):
    picked = []
    try:
        data = json.loads(content)
        raw = data.get("top5", [])
    except Exception:
        raw = [int(tok) for tok in __import__("re").findall(r"\d+", content)]

    for n in raw:
        try:
            n = int(n)
        except (TypeError, ValueError):
            continue
        if 1 <= n <= n_candidates and n not in picked:
            picked.append(n)
        if len(picked) == 5:
            break

    if len(picked) < 5:
        for n in range(1, n_candidates + 1):
            if n not in picked:
                picked.append(n)
            if len(picked) == 5:
                break
    return picked[:5]


def llm_rerank(query, candidates, cache):
    key = make_cache_key(query, candidates)
    if key in cache:
        return cache[key]["top5_indices"], cache[key].get("total_tokens", 0), True

    user_content = f"Question: {query}\n\nCandidates:\n{build_candidate_list(candidates)}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    content = ""
    total_tokens = 0
    for use_json_mode in (True, False):
        kwargs = dict(
            model=MODEL,
            messages=messages,
            temperature=0,
            reasoning_effort="low",
            max_tokens=200,
        )
        if use_json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            total_tokens = response.usage.total_tokens if response.usage else 0
            break
        except groq.RateLimitError:
            raise
        except groq.BadRequestError:
            continue

    top5_1indexed = parse_top5(content, len(candidates))
    cache[key] = {"top5_indices": top5_1indexed, "total_tokens": total_tokens, "raw": content}
    return top5_1indexed, total_tokens, False


def rank_of_expected(results, expected_act, expected_section):
    for i, r in enumerate(results, start=1):
        if str(r.get("act_name")) == expected_act and str(r.get("section_number")) == expected_section:
            return i
    return None


def metrics_from_rank(rank):
    recall_at_5 = 1.0 if (rank is not None and rank <= 5) else 0.0
    precision_at_1 = 1.0 if rank == 1 else 0.0
    reciprocal_rank = (1.0 / rank) if rank is not None else 0.0
    return recall_at_5, precision_at_1, reciprocal_rank


def mcnemar_test(baseline_hits, rerank_hits):
    """McNemar's test (with continuity correction) on paired binary Recall@5 outcomes."""
    b = sum(1 for base, rer in zip(baseline_hits, rerank_hits) if base == 1 and rer == 0)
    c = sum(1 for base, rer in zip(baseline_hits, rerank_hits) if base == 0 and rer == 1)
    if b + c == 0:
        return b, c, 0.0, 1.0
    chi2 = ((abs(b - c) - 1) ** 2) / (b + c)
    from scipy.stats import chi2 as chi2_dist
    p_value = 1.0 - chi2_dist.cdf(chi2, df=1)
    return b, c, chi2, p_value


def main():
    parser = argparse.ArgumentParser(description="Experiment: LLM rerank of top-20 candidates vs current production (strict-clean + L-6 reranker). Does not touch the live app.")
    parser.add_argument("--limit", type=int, default=150, help="Number of questions to run (default: 150, English only)")
    args = parser.parse_args()

    print("Loading search engine and applying --strict-clean settings...")
    engine = SearchEngine()
    apply_strict_clean(engine)

    with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    queries = [(q, act, sec) for q, act, sec in test_data][: args.limit]
    print(f"Running {len(queries)} English queries.\n")

    cache = load_cache()

    baseline_hits, rerank_hits = [], []
    baseline_p1, rerank_p1 = [], []
    baseline_rr, rerank_rr = [], []
    ceiling_hits = []
    token_counts = []

    n_completed = 0
    stopped_early = False

    for i, (query, expected_act, expected_section) in enumerate(queries, start=1):
        candidates = engine.search(query, top_k=20, rerank=True)

        base_rank = rank_of_expected(candidates[:5], expected_act, expected_section)
        b_recall, b_p1, b_rr = metrics_from_rank(base_rank)
        baseline_hits.append(b_recall)
        baseline_p1.append(b_p1)
        baseline_rr.append(b_rr)

        ceiling_rank = rank_of_expected(candidates, expected_act, expected_section)
        ceiling_hits.append(1.0 if ceiling_rank is not None else 0.0)

        try:
            top5_indices, total_tokens, from_cache = llm_rerank(query, candidates, cache)
        except groq.RateLimitError as e:
            if _is_daily_limit_error(e):
                print(f"\nStopped at query {i}/{len(queries)}: daily token limit reached.")
                stopped_early = True
                break
            raise

        if not from_cache:
            save_cache(cache)
            token_counts.append(total_tokens)

        reranked_top5 = [candidates[idx - 1] for idx in top5_indices]
        rer_rank = rank_of_expected(reranked_top5, expected_act, expected_section)
        r_recall, r_p1, r_rr = metrics_from_rank(rer_rank)
        rerank_hits.append(r_recall)
        rerank_p1.append(r_p1)
        rerank_rr.append(r_rr)

        n_completed = i
        if i % 25 == 0 or i == len(queries):
            print(f"  ...{i}/{len(queries)} done")

    if n_completed == 0:
        print("No queries completed.")
        return

    n = n_completed

    def avg(xs):
        return sum(xs) / len(xs) if xs else 0.0

    b_recall5, r_recall5 = avg(baseline_hits), avg(rerank_hits)
    b_p1_avg, r_p1_avg = avg(baseline_p1), avg(rerank_p1)
    b_mrr, r_mrr = avg(baseline_rr), avg(rerank_rr)
    ceiling = avg(ceiling_hits)
    b, c, chi2, p_value = mcnemar_test(baseline_hits, rerank_hits)
    avg_tokens = avg(token_counts) if token_counts else None

    print("\n" + "=" * 78)
    print(f"RESULTS (n={n}{' — stopped early' if stopped_early else ''})")
    print("=" * 78)
    print(f"{'Metric':<15} {'Baseline (top-5)':<20} {'LLM-rerank (top-5)':<20}")
    print(f"{'Recall@5':<15} {b_recall5:<20.4f} {r_recall5:<20.4f}")
    print(f"{'P@1':<15} {b_p1_avg:<20.4f} {r_p1_avg:<20.4f}")
    print(f"{'MRR':<15} {b_mrr:<20.4f} {r_mrr:<20.4f}")
    print("-" * 78)
    print(f"Ceiling (correct section anywhere in top-20): {ceiling:.4f}")
    print(f"McNemar on Recall@5: b(baseline-only hits)={b}, c(rerank-only hits)={c}, chi2={chi2:.4f}, p={p_value:.4f}")
    if avg_tokens is not None:
        print(f"Average tokens per LLM call (fresh calls only, n={len(token_counts)}): {avg_tokens:.1f}")
    else:
        print("Average tokens per LLM call: n/a (all calls served from cache)")
    print("=" * 78)


if __name__ == "__main__":
    main()
