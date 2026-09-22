import json
from search_core import SearchEngine
from rag_core import rewrite_query_for_search

engine = SearchEngine()

with open("../data/eval/rewrite_validation_set.json", "r", encoding="utf-8") as f:
    queries = json.load(f)

baseline_hits = 0
rewritten_hits = 0

print(f"{'Baseline':<10} {'Rewritten':<10} Query")
print("-" * 80)

for query, expected_act, expected_section in queries:
    baseline_results = engine.search(query, top_k=5)
    baseline_hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in baseline_results)
    if baseline_hit:
        baseline_hits += 1

    rewritten_query = rewrite_query_for_search(query)
    rewritten_results = engine.search(rewritten_query, top_k=5)
    rewritten_hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in rewritten_results)
    if rewritten_hit:
        rewritten_hits += 1

    print(f"{'YES' if baseline_hit else 'NO':<10} {'YES' if rewritten_hit else 'NO':<10} {query[:55]}")

n = len(queries)
print("-" * 80)
print(f"\nBaseline (no rewriting):   {baseline_hits}/{n} = {baseline_hits/n:.4f}")
print(f"With query rewriting:      {rewritten_hits}/{n} = {rewritten_hits/n:.4f}")
print(f"Delta: {(rewritten_hits - baseline_hits)/n*100:+.1f}pp")
