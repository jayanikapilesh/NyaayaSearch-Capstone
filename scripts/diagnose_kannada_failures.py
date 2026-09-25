import json
from search_core import SearchEngine
from rag_core import translate_to_english

engine = SearchEngine()

with open("../data/eval/test_270_kn.json", "r", encoding="utf-8") as f:
    queries = json.load(f)

failures = []
for lang, query, expected_act, expected_section in queries:
    try:
        translated = translate_to_english(query)
    except Exception as e:
        translated = f"[TRANSLATION FAILED: {e}]"
    results = engine.search(translated, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if not hit:
        failures.append((query, translated, expected_act, expected_section))

print(f"Total Kannada failures: {len(failures)} out of {len(queries)}\n")
for original, translated, act, sec in failures:
    print(f"Original: {original}")
    print(f"Translated: {translated}")
    print(f"Expected: {act} S{sec}")
    print()
