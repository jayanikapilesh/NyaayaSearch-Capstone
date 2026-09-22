import json

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

en = load("../data/eval/final_test_set_batch1.json") + load("../data/eval/final_test_set_batch2.json") + \
     load("../data/eval/final_test_set_batch3.json") + load("../data/eval/final_test_set_batch4.json") + \
     load("../data/eval/final_test_set_batch5.json")

hi = load("../data/eval/final_test_hindi.json") + load("../data/eval/final_test_hindi2.json")
kn = load("../data/eval/final_test_kannada.json") + load("../data/eval/final_test_kannada2.json")

with open("../data/eval/test_270_en.json", "w", encoding="utf-8") as f:
    json.dump(en, f, indent=2, ensure_ascii=False)
with open("../data/eval/test_270_hi.json", "w", encoding="utf-8") as f:
    json.dump(hi, f, indent=2, ensure_ascii=False)
with open("../data/eval/test_270_kn.json", "w", encoding="utf-8") as f:
    json.dump(kn, f, indent=2, ensure_ascii=False)

print(f"English: {len(en)} queries")
print(f"Hindi: {len(hi)} queries")
print(f"Kannada: {len(kn)} queries")
print(f"Total: {len(en) + len(hi) + len(kn)} queries")
