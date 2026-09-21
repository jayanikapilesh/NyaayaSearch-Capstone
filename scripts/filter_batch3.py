import json

bad_indices = {0, 1, 4, 5}

with open("../data/training_pairs_batch3.jsonl") as f:
    pairs = [json.loads(l) for l in f]

filtered = [p for i, p in enumerate(pairs) if i not in bad_indices]

with open("../data/training_pairs_batch3.jsonl", "w", encoding="utf-8") as f:
    for p in filtered:
        f.write(json.dumps(p) + "\n")

print(f"Kept {len(filtered)} of {len(pairs)} pairs (removed {len(pairs) - len(filtered)} low-quality administrative-amendment entries)")
