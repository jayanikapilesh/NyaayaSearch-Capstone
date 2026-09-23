import json
import importlib.util

spec = importlib.util.spec_from_file_location("search_core_before3", "search_core_BEFORE_BATCH3.py")
search_core_before3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search_core_before3)

engine = search_core_before3.SearchEngine()

with open("../data/eval/jayani_validation_set2.json", "r", encoding="utf-8") as f:
    queries = json.load(f)

hits = 0
for query, expected_act, expected_section in queries:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        hits += 1

n = len(queries)
print(f"\nBEFORE batch3 (6 entries) on the SAME new fresh 29-query set: {hits}/{n} = {hits/n:.4f}")
