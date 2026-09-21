import csv

rows = []
with open("../data/eval/category_evaluation_full_results.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Exclude the one contaminated duplicate
clean_rows = [r for r in rows if r["query"] != "What is a contingent contract?"]

print(f"Original: {len(rows)} queries")
print(f"After removing 1 contaminated duplicate: {len(clean_rows)} queries")

hits = sum(1 for r in clean_rows if r["hit"] == "1")
recall_at_5 = hits / len(clean_rows)

print(f"\nFINAL FROZEN METRICS (n={len(clean_rows)}):")
print(f"Recall@5: {hits}/{len(clean_rows)} = {recall_at_5:.4f}")
