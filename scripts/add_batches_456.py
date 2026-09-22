content = open("build_classifier_data_clean.py", encoding="utf-8").read()

old = """with open("../data/training_pairs_batch3.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

print(f"Total labeled query->section pairs (excludes eval/held-out sets): {len(queries_and_targets)}")"""

new = """with open("../data/training_pairs_batch3.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

with open("../data/training_pairs_batch4.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

with open("../data/training_pairs_batch5.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

with open("../data/training_pairs_batch6.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

print(f"Total labeled query->section pairs (excludes eval/held-out sets): {len(queries_and_targets)}")"""

count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("build_classifier_data_clean.py", "w", encoding="utf-8").write(content)
    print("Updated to include batches 4, 5, 6")
