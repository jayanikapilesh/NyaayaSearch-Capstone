content = open("generate_training_pairs_batch5.py", encoding="utf-8").read()
old = 'model="qwen/qwen3-32b",'
new = 'model="qwen/qwen3.8-27b",'
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("generate_training_pairs_batch5.py", "w", encoding="utf-8").write(content)
    print("Fixed")
