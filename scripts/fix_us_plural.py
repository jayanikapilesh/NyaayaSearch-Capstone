content = open("extract_citations.py", encoding="utf-8").read()
old = 'u[/l1]s\\.?\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*of\\s*(?:the\\s*)?'
new = 'u[/l1]ss?\\.?\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*of\\s*(?:the\\s*)?'
count = content.count(old)
print(f"Found {count} occurrence(s)")
content = content.replace(old, new)
open("extract_citations.py", "w", encoding="utf-8").write(content)
print(f"Fixed both PATTERN_US_OF and PATTERN_US_OF_ACRONYM to accept plural u/ss")
