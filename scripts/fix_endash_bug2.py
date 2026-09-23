content = open("extract_citations.py", encoding="utf-8").read()
old = "[-:]?"
new = "[\u2013\u2014\\-:]?"
count = content.count(old)
print(f"Found {count} occurrence(s)")
content = content.replace(old, new)
open("extract_citations.py", "w", encoding="utf-8").write(content)
print("Fixed")
