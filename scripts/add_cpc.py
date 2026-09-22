content = open("extract_citations.py", encoding="utf-8").read()
old = "Penal Code|Code of Criminal Procedure|Insolvency and Bankruptcy Code"
new = "Penal Code|Code of Criminal Procedure|Code of Civil Procedure|Insolvency and Bankruptcy Code"
count = content.count(old)
print(f"Found {count} occurrence(s)")
content = content.replace(old, new)
open("extract_citations.py", "w", encoding="utf-8").write(content)
print(f"Replaced all {count} occurrences - added Code of Civil Procedure")
