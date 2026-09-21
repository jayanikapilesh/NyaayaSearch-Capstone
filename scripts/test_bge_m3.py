import json
import numpy as np
import openpyxl
from sentence_transformers import SentenceTransformer

print("Loading BGE-M3 model (this will download ~2GB on first run)...")
model = SentenceTransformer("BAAI/bge-m3")

print("Loading legal dataset...")
wb = openpyxl.load_workbook("../Legal_Knowledge_Base_combined.xlsx", read_only=True)
ws = wb.active
headers = list(next(ws.values))
records = []
for row in ws.iter_rows(values_only=True):
    record = dict(zip(headers, row))
    records.append(record)

texts = [
    str(r.get("section_title") or "") + " " + str(r.get("legal_text") or "")
    for r in records
]

print(f"Embedding {len(texts)} sections with BGE-M3 (this will take a while)...")
embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True, batch_size=16)
np.save("bge_m3_embeddings.npy", embeddings)
print("Saved embeddings to bge_m3_embeddings.npy")


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

hindi = load("../data/eval/final_test_hindi.json")
kannada = load("../data/eval/final_test_kannada.json")

def run_direct(name, queries):
    hits = 0
    for lang, query, expected_act, expected_section in queries:
        query_emb = model.encode([query], normalize_embeddings=True)[0]
        scores = np.dot(embeddings, query_emb)
        top5_idx = np.argsort(scores)[::-1][:5]
        hit = False
        for idx in top5_idx:
            r = records[idx]
            if str(r.get("act_name")) == expected_act and str(r.get("section_number")) == expected_section:
                hit = True
                break
        if hit:
            hits += 1
    print(f"{name}: {hits}/{len(queries)} = {hits/len(queries):.4f}")
    return hits, len(queries)

print("\n" + "=" * 60)
print("BGE-M3 DIRECT MULTILINGUAL SEARCH (no translation step)")
print("=" * 60)
h1, n1 = run_direct("Hindi (direct, no translation)", hindi)
h2, n2 = run_direct("Kannada (direct, no translation)", kannada)
print(f"\nCombined: {h1+h2}/{n1+n2} = {(h1+h2)/(n1+n2):.4f}")
print("\nFor comparison, current translate-then-search pipeline scored:")
print("Hindi: 63.33%, Kannada: 66.67% (n=30 each)")
