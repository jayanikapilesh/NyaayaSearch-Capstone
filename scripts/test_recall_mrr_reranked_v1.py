import csv
import joblib
import pandas as pd
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

search_recall5_hits = 0
reranked_recall5_hits = 0
search_rr_sum = 0
reranked_rr_sum = 0

for row in rows:
    query = row["query"]
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

    top5_search = results[:5]
    search_hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in top5_search)
    if search_hit:
        search_recall5_hits += 1
    search_rank = next((i+1 for i, r in enumerate(results) if str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section), None)
    search_rr_sum += (1/search_rank) if search_rank else 0

    query_word_count = len(search_query.split())
    feature_rows = []
    for rank, r in enumerate(results, start=1):
        matched_count = len(r.get("matched_terms", []))
        feature_rows.append({
            "hybrid_score": r["hybrid_score"], "semantic_score": r["semantic_score"],
            "bm25_score": r["bm25_score"], "matched_term_count": matched_count,
            "rank": rank, "reciprocal_rank": 1.0 / rank, "query_length": query_word_count,
            "matched_term_ratio": matched_count / query_word_count if query_word_count > 0 else 0,
            "semantic_minus_bm25": r["semantic_score"] - r["bm25_score"],
        })
    feat_df = pd.DataFrame(feature_rows)
    probs = model.predict_proba(feat_df)[:, 1]
    reranked_order = [results[i] for i in probs.argsort()[::-1]]

    top5_reranked = reranked_order[:5]
    reranked_hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in top5_reranked)
    if reranked_hit:
        reranked_recall5_hits += 1
    reranked_rank = next((i+1 for i, r in enumerate(reranked_order) if str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section), None)
    reranked_rr_sum += (1/reranked_rank) if reranked_rank else 0

n = len(rows)
print(f"On frozen 148-query set (n={n}), V1 baseline system:")
print(f"\nSearch-only:  Recall@5={search_recall5_hits/n:.4f}  MRR={search_rr_sum/n:.4f}")
print(f"Reranked:     Recall@5={reranked_recall5_hits/n:.4f}  MRR={reranked_rr_sum/n:.4f}")
print(f"\nDelta: Recall@5={((reranked_recall5_hits-search_recall5_hits)/n*100):+.2f}pp  MRR={(reranked_rr_sum-search_rr_sum)/n:+.4f}")
