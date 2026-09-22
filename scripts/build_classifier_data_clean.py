import json
import pandas as pd
from search_core import SearchEngine

engine = SearchEngine()

rows = []
queries_and_targets = []

# ONLY use sources that were purpose-built for classifier/fine-tuning training,
# NEVER the 42 tuned eval queries or the 55 held-out queries - those must
# remain genuinely unseen by the classifier for evaluation to be valid.
with open("../data/training_pairs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

with open("../data/training_pairs_batch2.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

with open("../data/training_pairs_batch3.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

with open("../data/training_pairs_batch4.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

with open("../data/training_pairs_batch5.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

with open("../data/training_pairs_batch6.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

print(f"Total labeled query->section pairs (excludes eval/held-out sets): {len(queries_and_targets)}")

for i, (query, expected_act, expected_section) in enumerate(queries_and_targets):
    results = engine.search(query, top_k=10)
    query_word_count = len(query.split())

    for rank, r in enumerate(results, start=1):
        is_relevant = int(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section)
        matched_count = len(r.get("matched_terms", []))
        rows.append({
            "query": query,
            "act_name": r["act_name"],
            "section_number": r["section_number"],
            "hybrid_score": r["hybrid_score"],
            "semantic_score": r["semantic_score"],
            "bm25_score": r["bm25_score"],
            "matched_term_count": matched_count,
            "rank": rank,
            "reciprocal_rank": 1.0 / rank,
            "query_length": query_word_count,
            "matched_term_ratio": matched_count / query_word_count if query_word_count > 0 else 0,
            "semantic_minus_bm25": r["semantic_score"] - r["bm25_score"],
            "is_relevant": is_relevant,
        })

    if (i + 1) % 50 == 0:
        print(f"Processed {i + 1}/{len(queries_and_targets)} queries...")

df = pd.DataFrame(rows)
df.to_csv("../data/eval/classifier_training_data_clean.csv", index=False)
print(f"\nBuilt {len(df)} labeled examples")
print(f"Relevant: {df['is_relevant'].sum()}, Not relevant: {(df['is_relevant']==0).sum()}")
print(f"Unique queries: {df['query'].nunique()}")

