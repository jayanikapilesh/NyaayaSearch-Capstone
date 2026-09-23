content = open("extract_citations.py", encoding="utf-8").read()
old = """PATTERN_CODE_SECTION = re.compile(
    rf"((?:{WORD}\\s+){{0,5}}(?:Penal Code|Code of Criminal Procedure|Code of Civil Procedure|Insolvency and Bankruptcy Code)),?\\s*\\d{{4}}\\s*[:\\-\u2013\u2014]?\\s*(?:ss?\\.?|Sections?)\\s*(\\d+[A-Za-z]?(?:/\\d+[A-Za-z]?)*(?:\\(\\w+\\))?)",
)"""
new = """PATTERN_CODE_SECTION = re.compile(
    rf"((?:{WORD}\\s+){{0,5}}(?:Penal Code|Code of Criminal Procedure|Code of Civil Procedure|Insolvency and Bankruptcy Code)),?\\s*\\d{{4}}\\s*[:\\-\u2013\u2014]?\\s*(?:ss?\\.?|Sections?)\\s*(\\d+[A-Za-z]?(?:/\\d+[A-Za-z]?)*(?:\\(\\w+\\))?)",
)

# NEW: "u/s(s) X (and Y) of (the) Z Code" - parallel to PATTERN_US_OF but for Code names, not Acts
PATTERN_US_OF_CODE = re.compile(
    rf"u[/l1]ss?\\.?\\s*((?:\\d+[A-Za-z]?(?:\\(\\w+\\))?\\s*(?:,\\s*|and\\s+))*\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*of\\s*(?:the\\s*)?((?:{WORD}\\s+){{0,5}}(?:Penal Code|Code of Criminal Procedure|Code of Civil Procedure|Insolvency and Bankruptcy Code))",
)"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("extract_citations.py", "w", encoding="utf-8").write(content)
    print("Added PATTERN_US_OF_CODE")
