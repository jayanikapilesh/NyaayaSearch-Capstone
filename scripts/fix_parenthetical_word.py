content = open("extract_citations.py", encoding="utf-8").read()
old = 'WORD = r"(?:[A-Z][a-z]+|of|the|and)"'
new = 'WORD = r"(?:[A-Z][a-z]+|of|the|and|\\([A-Z][a-z]+\\))"'
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("extract_citations.py", "w", encoding="utf-8").write(content)
    print("Extended WORD pattern to allow parenthetical qualifiers like (Regulation), (Prevention)")
