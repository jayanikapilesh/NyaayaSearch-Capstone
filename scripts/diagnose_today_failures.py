from search_core import SearchEngine
from evaluate import load_test_set

engine = SearchEngine()
queries = load_test_set("en")

failures = []
for query, expected_act, expected_section in queries:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if not hit:
        failures.append((query, expected_act, expected_section))

print(f"Total failures: {len(failures)} out of {len(queries)}\n")
for query, act, sec in failures:
    print(f"FAIL: \"{query}\" (expected: {act} S{sec})")
