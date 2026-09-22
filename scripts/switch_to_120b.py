content = open("rag_core.py", encoding="utf-8").read()
old = 'model="openai/gpt-oss-20b"'
new = 'model="openai/gpt-oss-120b"'
count = content.count(old)
print(f"Found {count} occurrence(s)")
content = content.replace(old, new)
open("rag_core.py", "w", encoding="utf-8").write(content)
print("Replaced all occurrences")
