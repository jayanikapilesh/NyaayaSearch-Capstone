content = open("extract_citations.py", encoding="utf-8").read()
old = "({_acronym_alternation})\\b"
new = "({_acronym_alternation})(?!\\w)"
count = content.count(old)
print(f"Found {count} occurrence(s)")
content = content.replace(old, new)
open("extract_citations.py", "w", encoding="utf-8").write(content)
print(f"Fixed all {count} occurrences: replaced trailing \\b with (?!\\w) - a lookahead that correctly handles acronyms ending in periods")
