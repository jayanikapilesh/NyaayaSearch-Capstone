import json
import importlib.util

spec = importlib.util.spec_from_file_location("search_core_old", "search_core_OLD_BEFORE_TODAY.py")
search_core_old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search_core_old)

engine = search_core_old.SearchEngine()

with open("../data/eval/jayani_validation_set.json", "r", encoding="utf-8") as f:
    queries = json.load(f)

hits = 0
for query, expected_act, expected_section in queries:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        hits += 1

n = len(queries)
print(f"\nOLD (before today's fixes) on the SAME fresh 35-query set: {hits}/{n} = {hits/n:.4f}")
