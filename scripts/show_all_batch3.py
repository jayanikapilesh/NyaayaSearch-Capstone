import json
with open("../data/training_pairs_batch3.jsonl") as f:
    pairs = [json.loads(l) for l in f]
for i, p in enumerate(pairs):
    print(f"{i}: [{p['act_name']} S{p['section_number']}] {p['query']}")
