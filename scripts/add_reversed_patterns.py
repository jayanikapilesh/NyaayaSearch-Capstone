content = open("extract_citations.py", encoding="utf-8").read()
old = """PATTERN_US_OF_ACRONYM = re.compile(
    rf"u[/l1]s\\.?\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*of\\s*(?:the\\s*)?({_acronym_alternation})\\b",
)

# NEW: Constitution Article references, e.g. "Art. 14 of the Constitution", "Article 21"
PATTERN_ARTICLE = re.compile("""
new = """PATTERN_US_OF_ACRONYM = re.compile(
    rf"u[/l1]s\\.?\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*of\\s*(?:the\\s*)?({_acronym_alternation})\\b",
)

# NEW: "Section X of (the) Y Act" - full word "Section" instead of "u/s", number-then-Act order
PATTERN_SECTION_OF_ACT = re.compile(
    rf"Sections?\\.?\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*(?:of|under)\\s*(?:the\\s*)?((?:{WORD}\\s+){{1,6}}Act)",
)

# NEW: "Section X of (the) Y Code/Cr.P.C./I.P.C." - number-then-Code order, full word "Section"
PATTERN_SECTION_OF_CODE = re.compile(
    rf"Sections?\\.?\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*(?:of|under)\\s*(?:the\\s*)?((?:{WORD}\\s+){{0,5}}(?:Penal Code|Code of Criminal Procedure|Insolvency and Bankruptcy Code))",
)

# NEW: "Section X ACRONYM" (no "of") and "Section X of (the) ACRONYM"
PATTERN_SECTION_ACRONYM = re.compile(
    rf"Sections?\\.?\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*(?:of\\s*(?:the\\s*)?)?({_acronym_alternation})\\b",
)

# NEW: Constitution Article references, e.g. "Art. 14 of the Constitution", "Article 21"
PATTERN_ARTICLE = re.compile("""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("extract_citations.py", "w", encoding="utf-8").write(content)
    print("Added 3 new patterns for the number-before-Act-name citation order")
