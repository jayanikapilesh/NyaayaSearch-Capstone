import json
import random

pairs = []
with open("../data/training_pairs_batch2.jsonl") as f:
    for line in f:
        pairs.append(json.loads(line))

random.seed(42)
sample = random.sample(pairs, 15)
for p in sample:
    print(f"[{p['act_name']} S{p['section_number']}] {p['query']}")
