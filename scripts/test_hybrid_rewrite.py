import json
from search_core import SearchEngine
from rag_core import rewrite_query_for_search

engine = SearchEngine()

with open("../data/eval/rewrite_validation_set.json", "r", encoding="utf-8") as f:
    queries = json.load(f)

hybrid_hits = 0
used_rewritten_count = 0

print(f"{'Used':<12} {'Hit?':<6} Query")
print("-" * 80)

for query, expected_act, expected_section in queries:
    baseline_results = engine.search(query, top_k=5)
    baseline_top_score = baseline_results[0]["hybrid_score"] if baseline_results else 0

    rewritten_query = rewrite_query_for_search(query)
    rewritten_results = engine.search(rewritten_query, top_k=5)
    rewritten_top_score = rewritten_results[0]["hybrid_score"] if rewritten_results else 0

    if rewritten_top_score > baseline_top_score:
        chosen_results = rewritten_results
        used = "rewritten"
        used_rewritten_count += 1
    else:
        chosen_results = baseline_results
        used = "original"

    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in chosen_results)
    if hit:
        hybrid_hits += 1

    print(f"{used:<12} {'YES' if hit else 'NO':<6} {query[:50]}")

n = len(queries)
print("-" * 80)
print(f"\nHybrid approach (pick higher-confidence version): {hybrid_hits}/{n} = {hybrid_hits/n:.4f}")
print(f"Used rewritten version: {used_rewritten_count}/{n} times")
print(f"\nFor comparison:")
print(f"Baseline only:  26/40 = 0.6500")
print(f"Rewritten only: 26/40 = 0.6500")
