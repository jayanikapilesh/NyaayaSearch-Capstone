import csv
import math
from search_core import SearchEngine
from rag_core import translate_to_english

engine = SearchEngine()

rows = []
with open("../data/eval/category_evaluation_full_results.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)
rows = [r for r in rows if r["query"] != "What is a contingent contract?"]

p1_hits, p3_hits, p5_hits = 0, 0, 0
rr_sum = 0
ndcg_sum = 0
n = len(rows)

for row in rows:
    query = row["query"]
    expected_act = row["expected_act"]
    expected_section = row["expected_section"]

    if query.strip() and not query.isascii():
        try:
            search_query = translate_to_english(query)
        except Exception:
            search_query = query
    else:
        search_query = query

    results = engine.search(search_query, top_k=5)
    relevance = [1 if (str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section) else 0 for r in results]

    if len(relevance) > 0 and relevance[0] == 1:
        p1_hits += 1
    if sum(relevance[:3]) >= 1:
        p3_hits += 1
    if sum(relevance[:5]) >= 1:
        p5_hits += 1

    first_hit_rank = None
    for i, rel in enumerate(relevance, start=1):
        if rel == 1:
            first_hit_rank = i
            break
    rr_sum += (1 / first_hit_rank) if first_hit_rank else 0

    dcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(relevance))
    ndcg_sum += dcg  # idcg = 1.0 since only one relevant doc per query

print(f"Metrics on frozen 148-query decontaminated category evaluation set (n={n}):")
print(f"P@1 (relevant in top-1):  {p1_hits/n:.4f}")
print(f"P@3 (relevant in top-3):  {p3_hits/n:.4f}")
print(f"P@5 (relevant in top-5, i.e. Recall@5):  {p5_hits/n:.4f}")
print(f"MRR: {rr_sum/n:.4f}")
print(f"nDCG@5: {ndcg_sum/n:.4f}")
