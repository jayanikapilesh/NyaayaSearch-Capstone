import json
with open("../data/training_pairs_batch3.jsonl") as f:
    pairs = [json.loads(l) for l in f]
for p in pairs[:8]:
    print(f"[{p['act_name']} S{p['section_number']}] {p['query']}")
