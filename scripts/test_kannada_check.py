import json
from search_core import SearchEngine
from rag_core import translate_to_english

engine = SearchEngine()

with open("../data/eval/kannada_check_set.json", "r", encoding="utf-8") as f:
    queries = json.load(f)

hits = 0
for query, expected_act, expected_section in queries:
    try:
        translated = translate_to_english(query)
    except Exception as e:
        translated = f"[FAILED: {e}]"
    results = engine.search(translated, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        hits += 1
    status = "YES" if hit else "NO"
    print(f"{status:<5} Translated: {translated}")
    print(f"      Expected: {expected_act} S{expected_section}")
    print()

n = len(queries)
print(f"\nFresh Kannada check set: {hits}/{n} = {hits/n:.4f}")
