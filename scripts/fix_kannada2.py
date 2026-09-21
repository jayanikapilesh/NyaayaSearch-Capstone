import base64
import json

with open("kannada2_b64.txt", "r", encoding="ascii") as f:
    encoded_data = json.load(f)

decoded = []
for lang, q_b64, act, section in encoded_data:
    query = base64.b64decode(q_b64).decode("utf-8")
    decoded.append([lang, query, act, section])

with open("../data/eval/final_test_kannada2.json", "w", encoding="utf-8") as f:
    json.dump(decoded, f, indent=2, ensure_ascii=False)

print(f"Fixed: {len(decoded)} Kannada queries correctly decoded and saved")
# Verify by printing first one
print("Sample check:", decoded[0][1])
