import json
import pandas as pd
from search_core import SearchEngine

engine = SearchEngine()

rows = []

# Source 1: original eval queries (tuned + held-out batches already used)
with open("../data/eval/eval_queries.json", "r", encoding="utf-8") as f:
    eval_queries = json.load(f)

queries_and_targets = []
for q in eval_queries:
    for section in q["expected_sections"]:
        queries_and_targets.append((q["query"], q["act_name"], str(section)))

# Source 2: the 446 verified query->section pairs built for fine-tuning
with open("../data/training_pairs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

print(f"Total labeled query->section pairs to process: {len(queries_and_targets)}")

for i, (query, expected_act, expected_section) in enumerate(queries_and_targets):
    results = engine.search(query, top_k=10)
    for r in results:
        is_relevant = int(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section)
        rows.append({
            "query": query,
            "act_name": r["act_name"],
            "section_number": r["section_number"],
            "hybrid_score": r["hybrid_score"],
            "semantic_score": r["semantic_score"],
            "bm25_score": r["bm25_score"],
            "matched_term_count": len(r.get("matched_terms", [])),
            "is_relevant": is_relevant,
        })
    if (i + 1) % 50 == 0:
        print(f"Processed {i + 1}/{len(queries_and_targets)} queries...")

df = pd.DataFrame(rows)
df.to_csv("../data/eval/classifier_training_data_large.csv", index=False)
print(f"\nBuilt {len(df)} labeled examples")
print(f"Relevant: {df['is_relevant'].sum()}, Not relevant: {(df['is_relevant']==0).sum()}")
