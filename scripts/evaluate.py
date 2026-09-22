import json
import math
import argparse
import datetime
import os

import numpy as np

from search_core import SearchEngine


def compute_query_metrics(results, expected_act, expected_section):
    """Given a ranked list of results for ONE query, compute whether the
    correct (act, section) appears, and at what rank. Returns a dict of
    per-query metric contributions."""
    rank_of_correct = None
    for i, r in enumerate(results, start=1):
        if str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section:
            rank_of_correct = i
            break

    recall_at_5 = 1.0 if (rank_of_correct is not None and rank_of_correct <= 5) else 0.0
    precision_at_1 = 1.0 if rank_of_correct == 1 else 0.0
    precision_at_3 = 1.0 if (rank_of_correct is not None and rank_of_correct <= 3) else 0.0
    reciprocal_rank = (1.0 / rank_of_correct) if rank_of_correct is not None else 0.0

    if rank_of_correct is not None and rank_of_correct <= 5:
        ndcg_at_5 = 1.0 / math.log2(rank_of_correct + 1)
    else:
        ndcg_at_5 = 0.0

    return {
        "rank_of_correct": rank_of_correct,
        "recall_at_5": recall_at_5,
        "precision_at_1": precision_at_1,
        "precision_at_3": precision_at_3,
        "reciprocal_rank": reciprocal_rank,
        "ndcg_at_5": ndcg_at_5,
    }


def load_test_set(language):
    path = f"../data/eval/test_270_{language}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if language == "en":
        return [(q, act, sec) for q, act, sec in data]
    else:
        return [(q, act, sec) for lang, q, act, sec in data]


def run_evaluation(engine, queries, translate=False):
    """Run the real search engine on every query and aggregate metrics.
    If translate=True, uses rag_core.translate_to_english first (for hi/kn)."""
    per_query_results = []
    for query, expected_act, expected_section in queries:
        search_query = query
        if translate:
            from rag_core import translate_to_english
            try:
                search_query = translate_to_english(query)
            except Exception:
                search_query = query
        results = engine.search(search_query, top_k=10)
        metrics = compute_query_metrics(results, expected_act, expected_section)
        metrics["query"] = query
        per_query_results.append(metrics)

    n = len(per_query_results)
    aggregated = {
        "n": n,
        "recall_at_5": sum(m["recall_at_5"] for m in per_query_results) / n,
        "precision_at_1": sum(m["precision_at_1"] for m in per_query_results) / n,
        "precision_at_3": sum(m["precision_at_3"] for m in per_query_results) / n,
        "mrr": sum(m["reciprocal_rank"] for m in per_query_results) / n,
        "ndcg_at_5": sum(m["ndcg_at_5"] for m in per_query_results) / n,
    }
    return aggregated, per_query_results


def run_ablation(engine, queries):
    """Re-run the same queries with different scoring configurations to see
    each component's real, measured contribution. Uses the actual search_core
    scoring internals, not simulated numbers."""
    import re as _re
    from search_core import expand_query, tokenize

    configs = {}

    def score_config(use_bm25, use_semantic, use_expansion, use_boost):
        hits = 0
        for query, expected_act, expected_section in queries:
            q = expand_query(query) if use_expansion else query.lower()
            query_tokens = tokenize(q)
            bm25_scores = np.array(engine.bm25.get_scores(query_tokens), dtype=float)
            if bm25_scores.max() > 0:
                bm25_scores = bm25_scores / bm25_scores.max()
            query_embedding = engine.model.encode([q], normalize_embeddings=True)[0]
            semantic_scores = np.dot(engine.embeddings, query_embedding)
            semantic_scores = np.clip(semantic_scores, 0, 1)

            if use_bm25 and use_semantic:
                final_scores = (0.15 * bm25_scores) + (0.85 * semantic_scores)
            elif use_bm25:
                final_scores = bm25_scores
            else:
                final_scores = semantic_scores

            if use_boost:
                results = engine.search(query, top_k=5)
            else:
                top_indices = np.argsort(final_scores)[::-1][:5]
                results = [
                    {"act_name": engine.records[i].get("act_name"), "section_number": engine.records[i].get("section_number")}
                    for i in top_indices
                ]

            hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
            if hit:
                hits += 1
        return hits / len(queries)

    configs["BM25 only"] = score_config(True, False, False, False)
    configs["Semantic only"] = score_config(False, True, False, False)
    configs["Hybrid"] = score_config(True, True, False, False)
    configs["Hybrid + Expansion"] = score_config(True, True, True, False)
    configs["Full (+ Boosting)"] = score_config(True, True, True, True)

    return configs


def save_results(results, output_dir="../results"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"eval_{timestamp}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {filepath}")
    return filepath


def plot_ablation(configs, output_dir="../results/figures"):
    import matplotlib.pyplot as plt
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    names = list(configs.keys())
    values = list(configs.values())

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(names, values, color="#4C72B0")
    ax.set_ylabel("Recall@5")
    ax.set_title("Ablation: Component Contribution (real, computed)")
    ax.set_ylim(0, 1.0)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, f"{val:.3f}", ha="center")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()

    filepath = os.path.join(output_dir, f"ablation_{timestamp}.png")
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"Ablation chart saved to: {filepath}")
    return filepath


def plot_recall_by_language(lang_results, output_dir="../results/figures"):
    import matplotlib.pyplot as plt
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    langs = list(lang_results.keys())
    values = [lang_results[l]["recall_at_5"] for l in langs]
    label_map = {"en": "English", "hi": "Hindi", "kn": "Kannada"}
    labels = [label_map.get(l, l) for l in langs]

    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(labels, values, color=["#4C72B0", "#DD8452", "#55A868"])
    ax.set_ylabel("Recall@5")
    ax.set_title("Recall@5 by Language (real, computed)")
    ax.set_ylim(0, 1.0)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, f"{val:.3f}", ha="center")
    plt.tight_layout()

    filepath = os.path.join(output_dir, f"recall_by_language_{timestamp}.png")
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"Language chart saved to: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Evaluate NyaayaSearch retrieval - computes REAL metrics from live search, no simulated numbers.")
    parser.add_argument("--languages", type=str, default="en", help="Comma-separated: en,hi,kn (default: en only)")
    parser.add_argument("--ablation", action="store_true", help="Also run the component ablation (slower, ~5x search passes)")
    parser.add_argument("--output", type=str, default="../results", help="Directory to save results JSON")

    args = parser.parse_args()
    languages = [l.strip() for l in args.languages.split(",")]

    print("Loading search engine (this loads the real dataset and embeddings)...")
    engine = SearchEngine()

    all_results = {"timestamp": datetime.datetime.now().isoformat(), "languages_tested": languages}
    lang_results_for_plot = {}

    for lang in languages:
        print(f"\nEvaluating language: {lang}")
        queries = load_test_set(lang)
        translate = (lang != "en")
        aggregated, per_query = run_evaluation(engine, queries, translate=translate)
        all_results[lang] = aggregated
        lang_results_for_plot[lang] = aggregated
        print(f"  n={aggregated['n']}  Recall@5={aggregated['recall_at_5']:.4f}  P@1={aggregated['precision_at_1']:.4f}  P@3={aggregated['precision_at_3']:.4f}  MRR={aggregated['mrr']:.4f}  nDCG@5={aggregated['ndcg_at_5']:.4f}")

    if len(languages) > 1:
        plot_recall_by_language(lang_results_for_plot)

    if args.ablation:
        print("\nRunning ablation (this re-runs search multiple times per query)...")
        ablation_queries = load_test_set("en")
        ablation_results = run_ablation(engine, ablation_queries)
        all_results["ablation"] = ablation_results
        for name, val in ablation_results.items():
            print(f"  {name}: {val:.4f}")
        plot_ablation(ablation_results)

    save_results(all_results, output_dir=args.output)


if __name__ == "__main__":
    main()
