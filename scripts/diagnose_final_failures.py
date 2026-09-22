import json
from search_core import SearchEngine
from rag_core import translate_to_english

engine = SearchEngine()

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

batch1 = load("../data/eval/final_test_set_batch1.json")
batch2 = load("../data/eval/final_test_set_batch2.json")
batch3 = load("../data/eval/final_test_set_batch3.json")
batch4 = load("../data/eval/final_test_set_batch4.json")
batch5 = load("../data/eval/final_test_set_batch5.json")
hindi1 = load("../data/eval/final_test_hindi.json")
hindi2 = load("../data/eval/final_test_hindi2.json")

english_all = batch1 + batch2 + batch3 + batch4 + batch5
hindi_all = hindi1 + hindi2

print("=" * 70)
print("ENGLISH FAILURES")
print("=" * 70)
for query, expected_act, expected_section in english_all:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if not hit:
        print(f"FAIL: \"{query}\" (expected: {expected_act} S{expected_section})")

print("\n" + "=" * 70)
print("HINDI FAILURES")
print("=" * 70)
for lang, query, expected_act, expected_section in hindi_all:
    try:
        translated = translate_to_english(query)
    except Exception as e:
        translated = f"[TRANSLATION FAILED: {e}]"
    results = engine.search(translated, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if not hit:
        print(f"FAIL: \"{translated}\" (expected: {expected_act} S{expected_section})")
