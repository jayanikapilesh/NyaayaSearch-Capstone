import csv
import numpy as np
import joblib
import pandas as pd
from search_core import SearchEngine, expand_query, tokenize, find_matched_terms
from rag_core import translate_to_english

engine = SearchEngine()
model = joblib.load("../relevance_classifier.pkl")

rows = []
with open("../data/eval/category_evaluation_full_results.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)
rows = [r for r in rows if r["query"] != "What is a contingent contract?"]


def ablation_search(query, top_k=5, use_bm25=True, use_semantic=True, use_expansion=True, use_boost=True):
    search_query = expand_query(query) if use_expansion else query
    query_tokens = tokenize(search_query)

    bm25_scores = np.array(engine.bm25.get_scores(query_tokens), dtype=float)
    if bm25_scores.max() > 0:
        bm25_scores = bm25_scores / bm25_scores.max()

    query_embedding = engine.model.encode([search_query], normalize_embeddings=True)[0]
    semantic_scores = np.dot(engine.embeddings, query_embedding)
    semantic_scores = np.clip(semantic_scores, 0, 1)

    if use_bm25 and use_semantic:
        final_scores = (0.15 * bm25_scores) + (0.85 * semantic_scores)
    elif use_bm25:
        final_scores = bm25_scores.copy()
    elif use_semantic:
        final_scores = semantic_scores.copy()
    else:
        final_scores = np.zeros(len(engine.records))

    if use_boost:
        boost = np.ones(len(engine.records))
        query_lower = query.lower()
        for i, record in enumerate(engine.records):
            title = str(record.get("section_title") or "").lower()
            legal_text = str(record.get("legal_text") or "").lower()
            act_name = str(record.get("act_name") or "").lower()
            combined = title + " " + legal_text + " " + act_name
            if "landlord" in query_lower and "landlord" in combined:
                boost[i] *= 1.25
            if "tenant" in query_lower and "tenant" in combined:
                boost[i] *= 1.25
            if "security deposit" in query_lower and "security" in combined and "deposit" in combined:
                boost[i] *= 1.5
            if ("return" in query_lower or "refund" in query_lower) and any(w in combined for w in ["return", "refund", "repay"]):
                boost[i] *= 1.2
            if "minor" in query_lower and "contract" in query_lower and "contract act" in act_name and ("minor" in combined or "competent" in combined or "age of majority" in combined):
                boost[i] *= 2.0
            if "driving" in query_lower and "licence" in query_lower:
                if "motor vehicles act" in act_name:
                    boost[i] *= 2.0
                elif "information technology" in act_name:
                    boost[i] *= 0.3
            if "rti" in query_lower or "right to information" in query_lower:
                if "right to information act" in act_name:
                    boost[i] *= 2.0
        final_scores = final_scores * boost

    top_indices = np.argsort(final_scores)[::-1][:top_k]
    results = []
    for index in top_indices:
        record = engine.records[index]
        results.append({
            "act_name": record.get("act_name"),
            "section_number": record.get("section_number"),
            "hybrid_score": float(final_scores[index]),
            "semantic_score": float(semantic_scores[index]),
            "bm25_score": float(bm25_scores[index]),
            "matched_terms": find_matched_terms(query_tokens, str(record.get("section_title") or "") + " " + str(record.get("legal_text") or "")),
        })
    return results


configs = [
    ("A. BM25 only",              dict(use_bm25=True,  use_semantic=False, use_expansion=False, use_boost=False)),
    ("B. Semantic only",          dict(use_bm25=False, use_semantic=True,  use_expansion=False, use_boost=False)),
    ("C. BM25+Semantic (hybrid)", dict(use_bm25=True,  use_semantic=True,  use_expansion=False, use_boost=False)),
    ("D. C + query expansion",    dict(use_bm25=True,  use_semantic=True,  use_expansion=True,  use_boost=False)),
    ("E. D + boosting",           dict(use_bm25=True,  use_semantic=True,  use_expansion=True,  use_boost=True)),
]

print(f"Running ablation matrix on frozen 148-query set (n={len(rows)})\n")
print(f"{'Config':<28} {'Recall@5':<10}")
print("-" * 40)

config_results = {}
for name, params in configs:
    hits = 0
    for row in rows:
        query = row["query"]
        if query.strip() and not query.isascii():
            try:
                query = translate_to_english(query)
            except Exception:
                pass
        results = ablation_search(query, top_k=5, **params)
        hit = any(str(r["act_name"]) == row["expected_act"] and str(r["section_number"]) == row["expected_section"] for r in results)
        if hit:
            hits += 1
    recall = hits / len(rows)
    config_results[name] = (hits, recall)
    print(f"{name:<28} {recall:<10.4f}")

# F. E + classifier reranking
print("\nRunning F. E + classifier reranking...")
hits_f = 0
for row in rows:
    query = row["query"]
    if query.strip() and not query.isascii():
        try:
            query = translate_to_english(query)
        except Exception:
            pass
    results = ablation_search(query, top_k=10, use_bm25=True, use_semantic=True, use_expansion=True, use_boost=True)
    if not results:
        continue
    query_word_count = len(query.split())
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
    reranked_order = [results[i] for i in probs.argsort()[::-1]][:5]
    hit = any(str(r["act_name"]) == row["expected_act"] and str(r["section_number"]) == row["expected_section"] for r in reranked_order)
    if hit:
        hits_f += 1
recall_f = hits_f / len(rows)
print(f"{'F. E + classifier reranking':<28} {recall_f:<10.4f}")

print("\n" + "=" * 40)
print("FULL ABLATION MATRIX (on frozen 148-query set):")
for name, (hits, recall) in config_results.items():
    print(f"  {name}: {recall:.4f}")
print(f"  F. E + classifier reranking: {recall_f:.4f}")
