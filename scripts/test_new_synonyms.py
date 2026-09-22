import pandas as pd
from search_core import SearchEngine

print("Loading 148-query frozen set...")
df = pd.read_csv("../data/eval/category_evaluation_full_results.csv")
queries = list(zip(df["query"], df["expected_act"], df["expected_section"].astype(str)))

print("Loading search engine with new synonyms...")
engine = SearchEngine()

hits = 0
for query, expected_act, expected_section in queries:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        hits += 1

recall = hits / len(queries)
print(f"\nWith new synonym entries: {hits}/{len(queries)} = {recall:.4f}")
print(f"Previous baseline: 0.7919")
print(f"Delta: {recall - 0.7919:+.4f}")
