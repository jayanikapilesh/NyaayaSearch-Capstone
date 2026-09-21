import json
from search_core import SearchEngine
from rag_core import translate_to_english

engine = SearchEngine()

with open("../data/eval/final_test_kannada2.json", "r", encoding="utf-8") as f:
    kannada2 = json.load(f)

print("Checking first 10 Kannada queries from the FIXED file:\n")
for i, (lang, query, expected_act, expected_section) in enumerate(kannada2[:10]):
    print(f"{i}: Original: {query[:40]}...")
    try:
        translated = translate_to_english(query)
        print(f"   Translated: {translated}")
    except Exception as e:
        print(f"   TRANSLATION FAILED: {e}")
    print()
