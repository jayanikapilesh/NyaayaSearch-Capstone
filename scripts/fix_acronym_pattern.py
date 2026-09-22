content = open("extract_citations.py", encoding="utf-8").read()
old = 'rf"\\b({_acronym_alternation})\\b\\s*[-:]?\\s*ss?\\.?\\s*(\\d+[A-Za-z]?(?:/\\d+[A-Za-z]?)*(?:\\(\\w+\\))?)",'
new = 'rf"\\b({_acronym_alternation})\\b\\s*[-:]?\\s*(?:ss?\\.?|Sections?)\\s*(\\d+[A-Za-z]?(?:/\\d+[A-Za-z]?)*(?:\\(\\w+\\))?)",'
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("extract_citations.py", "w", encoding="utf-8").write(content)
    print("Fixed PATTERN_ACRONYM_SECTION")
