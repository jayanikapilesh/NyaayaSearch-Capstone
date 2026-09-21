import csv
import joblib
import pandas as pd
from search_core import SearchEngine

engine = SearchEngine()
model = joblib.load("../relevance_classifier.pkl")

rows = []
with open("../data/eval/category_evaluation_full_results.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Exclude the same 1 contaminated duplicate as before
rows = [r for r in rows if r["query"] != "What is a contingent contract?"]
print(f"Running on frozen, decontaminated set: {len(rows)} queries")

search_only_hits = 0
reranked_hits = 0

for row in rows:
    query = row["query"]
    expected_act = row["expected_act"]
    expected_section = row["expected_section"]

    # Multilingual queries need translation first, same as the app does
    if query.strip() and not query.isascii():
        from rag_core import translate_to_english
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

    top_search = results[0]
    if str(top_search["act_name"]) == expected_act and str(top_search["section_number"]) == expected_section:
        search_only_hits += 1

    best_idx = probs.argmax()
    top_reranked = results[best_idx]
    if str(top_reranked["act_name"]) == expected_act and str(top_reranked["section_number"]) == expected_section:
        reranked_hits += 1

n = len(rows)
print(f"\nFROZEN 148-query set - Search vs Reranked Top-1 accuracy:")
print(f"Search-only:        {search_only_hits}/{n} = {search_only_hits/n:.4f}")
print(f"Classifier-reranked: {reranked_hits}/{n} = {reranked_hits/n:.4f}")
print(f"Improvement: {(reranked_hits-search_only_hits)/n*100:.1f} percentage points")
