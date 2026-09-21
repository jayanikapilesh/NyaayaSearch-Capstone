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

never_changed = 0
changed = 0

for i, row in enumerate(rows[:20]):
    query = row["query"]
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
            "hybrid_score": r["hybrid_score"], "semantic_score": r["semantic_score"],
            "bm25_score": r["bm25_score"], "matched_term_count": matched_count,
            "rank": rank, "reciprocal_rank": 1.0 / rank, "query_length": query_word_count,
            "matched_term_ratio": matched_count / query_word_count if query_word_count > 0 else 0,
            "semantic_minus_bm25": r["semantic_score"] - r["bm25_score"],
        })
    feat_df = pd.DataFrame(feature_rows)
    probs = model.predict_proba(feat_df)[:, 1]
    best_idx = probs.argmax()

    if best_idx == 0:
        never_changed += 1
    else:
        changed += 1
        print(f"Query {i}: reranker picked rank {best_idx+1} instead of rank 1 (probs: {probs.round(3)})")

print(f"\nOut of first 20 queries: reranker kept rank-1 pick {never_changed} times, changed pick {changed} times")
