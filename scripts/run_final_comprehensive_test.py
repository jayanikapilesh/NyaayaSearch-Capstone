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
kannada1 = load("../data/eval/final_test_kannada.json")
kannada2 = load("../data/eval/final_test_kannada2.json")

english_all = batch1 + batch2 + batch3 + batch4 + batch5
hindi_all = hindi1 + hindi2
kannada_all = kannada1 + kannada2

def run_set(name, queries, translate=False):
    hits = 0
    for item in queries:
        if translate:
            lang, query, expected_act, expected_section = item
            try:
                search_query = translate_to_english(query)
            except Exception:
                search_query = query
        else:
            query, expected_act, expected_section = item
            search_query = query

        results = engine.search(search_query, top_k=5)
        hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
        if hit:
            hits += 1
    recall = hits / len(queries)
    print(f"{name}: {hits}/{len(queries)} = {recall:.4f}")
    return hits, len(queries)

print("=" * 70)
print("FINAL COMPREHENSIVE UNTOUCHED TEST SET (270 queries total)")
print("Tested ONCE. No follow-up tuning based on these results.")
print("=" * 70)

h1, n1 = run_set("English (150, batches 1-5)", english_all)
h2, n2 = run_set("Hindi (paired, 60)", hindi_all, translate=True)
h3, n3 = run_set("Kannada (paired, 60)", kannada_all, translate=True)

print("-" * 70)
total_h = h1 + h2 + h3
total_n = n1 + n2 + n3
print(f"GRAND TOTAL (all 270): {total_h}/{total_n} = {total_h/total_n:.4f}")
