import csv
import joblib
import pandas as pd
from collections import defaultdict
from search_core import SearchEngine
from rag_core import translate_to_english

engine = SearchEngine()
model = joblib.load("../relevance_classifier.pkl")

rows = []
with open("../data/eval/category_evaluation_full_results.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

rows = [r for r in rows if r["query"] != "What is a contingent contract?"]

category_stats = defaultdict(lambda: {"n": 0, "search_hits": 0, "reranked_hits": 0})

for row in rows:
    query = row["query"]
    category = row["category"]
    expected_act = row["expected_act"]
    expected_section = row["expected_section"]

    if query.strip() and not query.isascii():
        try:
            search_query = translate_to_english(query)
        except Exception:
            search_query = query
    else:
        search_query = query

    results = engine.search(search_query, top_k=10)
    if not results:
        continue

    query_word_count = len(search_query.split())
    feature_rows = []
    for rank, r in enumerate(results, start=1):
        matched_count = len(r.get("matched_terms", []))
        feature_rows.append({
            "hybrid_score": r["hybrid_score"],
            "semantic_score": r["semantic_score"],
            "bm25_score": r["bm25_score"],
            "matched_term_count": matched_count,
            "rank": rank,
            "reciprocal_rank": 1.0 / rank,
            "query_length": query_word_count,
            "matched_term_ratio": matched_count / query_word_count if query_word_count > 0 else 0,
            "semantic_minus_bm25": r["semantic_score"] - r["bm25_score"],
        })
    feat_df = pd.DataFrame(feature_rows)
    probs = model.predict_proba(feat_df)[:, 1]

    category_stats[category]["n"] += 1

    top_search = results[0]
    if str(top_search["act_name"]) == expected_act and str(top_search["section_number"]) == expected_section:
        category_stats[category]["search_hits"] += 1

    best_idx = probs.argmax()
    top_reranked = results[best_idx]
    if str(top_reranked["act_name"]) == expected_act and str(top_reranked["section_number"]) == expected_section:
        category_stats[category]["reranked_hits"] += 1

print(f"{'Category':<25} {'n':<5} {'Search-only':<14} {'Reranked':<12} {'Delta'}")
print("-" * 75)

total_n, total_search, total_reranked = 0, 0, 0
for cat, stats in sorted(category_stats.items()):
    n = stats["n"]
    s = stats["search_hits"]
    r = stats["reranked_hits"]
    total_n += n
    total_search += s
    total_reranked += r
    delta = (r - s) / n * 100
    print(f"{cat:<25} {n:<5} {s/n:<14.3f} {r/n:<12.3f} {delta:+.1f}pp")

print("-" * 75)
print(f"{'TOTAL':<25} {total_n:<5} {total_search/total_n:<14.3f} {total_reranked/total_n:<12.3f} {(total_reranked-total_search)/total_n*100:+.1f}pp")
