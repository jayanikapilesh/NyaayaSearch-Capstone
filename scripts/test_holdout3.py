import json
from search_core import SearchEngine

engine = SearchEngine()

with open("../data/eval/holdout3.json", "r", encoding="utf-8") as f:
    queries = json.load(f)

hits = 0
for query, expected_act, expected_section in queries:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        hits += 1
    print(f"{'YES' if hit else 'NO':<5} {query}")

n = len(queries)
print(f"\nFresh holdout Recall@5: {hits}/{n} = {hits/n:.4f}")
