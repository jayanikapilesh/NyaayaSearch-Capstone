import json
import os
import re
import numpy as np
import openpyxl
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

DATASET = os.path.join(os.path.dirname(__file__), "..", "Legal_Knowledge_Base_combined.xlsx")
EVAL_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "eval", "eval_queries.json")

STOP_WORDS = {
    "the", "a", "an", "is", "are", "am", "my", "me", "i",
    "what", "which", "who", "how", "can", "could", "would",
    "should", "do", "does", "did", "if", "to", "of", "for",
    "and", "or", "in", "on", "with", "from", "about", "law",
    "legal", "rights", "section", "not"
}


def tokenize(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


print("Loading legal dataset...")
wb = openpyxl.load_workbook(DATASET, read_only=True)
ws = wb.active
headers = list(next(ws.values))
records = []
for row in ws.iter_rows(values_only=True):
    record = dict(zip(headers, row))
    title = str(record.get("section_title") or "").strip().lower()
    if title in {"repeal.", "[repealed.]", "[repealed .].", "[omitted.]."}:
        continue
    records.append(record)

print(f"Loaded {len(records)} records")

documents = []
texts = []
for record in records:
    tok_text = (
        str(record.get("act_name") or "") + " " +
        str(record.get("section_number") or "") + " " +
        str(record.get("section_title") or "") + " " +
        str(record.get("legal_text") or "")
    )
    documents.append(tokenize(tok_text))
    embed_text = (
        str(record.get("act_name") or "") + ". " +
        str(record.get("section_title") or "") + ". " +
        str(record.get("legal_text") or "")
    )
    texts.append(embed_text)

print("Building BM25 index...")
bm25 = BM25Okapi(documents)

print("Building semantic embeddings...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

with open(EVAL_FILE, "r", encoding="utf-8") as f:
    eval_queries = json.load(f)


def evaluate_variant(name, score_fn):
    precisions, recalls, rrs = [], [], []
    for item in eval_queries:
        query = item["query"]
        expected_act = item["act_name"].lower()
        expected_sections = {str(s) for s in item["expected_sections"]}

        scores = score_fn(query)
        top_indices = np.argsort(scores)[::-1][:5]

        hits = 0
        first_hit_rank = None
        for rank, idx in enumerate(top_indices, start=1):
            record = records[idx]
            if str(record.get("act_name")).lower() == expected_act and str(record.get("section_number")) in expected_sections:
                hits += 1
                if first_hit_rank is None:
                    first_hit_rank = rank

        precisions.append(hits / 5)
        recalls.append(min(hits, len(expected_sections)) / len(expected_sections) if expected_sections else 0)
        rrs.append(1 / first_hit_rank if first_hit_rank else 0)

    print(f"\n{name}:")
    print(f"  Mean Precision@5: {sum(precisions)/len(precisions):.3f}")
    print(f"  Mean Recall@5:    {sum(recalls)/len(recalls):.3f}")
    print(f"  MRR:              {sum(rrs)/len(rrs):.3f}")
    return sum(precisions)/len(precisions), sum(recalls)/len(recalls), sum(rrs)/len(rrs)


def bm25_only_scores(query):
    tokens = tokenize(query)
    scores = np.array(bm25.get_scores(tokens), dtype=float)
    return scores


def semantic_only_scores(query):
    q_emb = model.encode([query], normalize_embeddings=True)[0]
    return np.dot(embeddings, q_emb)


def hybrid_scores(query):
    tokens = tokenize(query)
    bm25_s = np.array(bm25.get_scores(tokens), dtype=float)
    if bm25_s.max() > 0:
        bm25_s = bm25_s / bm25_s.max()
    q_emb = model.encode([query], normalize_embeddings=True)[0]
    sem_s = np.clip(np.dot(embeddings, q_emb), 0, 1)
    return 0.15 * bm25_s + 0.85 * sem_s


print("\n" + "=" * 60)
print("BASELINE COMPARISON")
print("=" * 60)

evaluate_variant("BM25 only (keyword matching)", bm25_only_scores)
evaluate_variant("Semantic only (embeddings)", semantic_only_scores)
evaluate_variant("Hybrid (BM25 15% + Semantic 85%) - no synonym/boost logic", hybrid_scores)

print("\nNote: This hybrid variant excludes the synonym expansion and domain-specific")
print("boost rules present in the production search_core.py, to isolate the effect")
print("of score-combination alone. Run evaluate_search.py for the full production system.")
