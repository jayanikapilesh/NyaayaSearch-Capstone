content = open("extract_citations.py", encoding="utf-8").read()
old = '    "SARFAESI Act": "SARFAESI Act",\n}'
new = '''    "SARFAESI Act": "SARFAESI Act",
    "I.P.C.": "Indian Penal Code",
    "Cr.P.C.": "Code of Criminal Procedure",
    "C.P.C.": "Code of Civil Procedure",
}'''
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("extract_citations.py", "w", encoding="utf-8").write(content)
    print("Added 3 period-variant acronyms")
