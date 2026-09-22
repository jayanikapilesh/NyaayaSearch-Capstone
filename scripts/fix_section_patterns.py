content = open("extract_citations.py", encoding="utf-8").read()

old1 = 'rf"((?:{WORD}\\s+){{1,6}}Act,?\\s*\\d{{4}})\\s*-?\\s*[:\\-]?\\s*s\\.?\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)",'
new1 = 'rf"((?:{WORD}\\s+){{1,6}}Act,?\\s*\\d{{4}})\\s*-?\\s*[:\\-]?\\s*(?:s\\.?|Sections?)\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)",'
count1 = content.count(old1)
print(f"PATTERN_ACT_SECTION fix: found {count1}")
if count1 == 1:
    content = content.replace(old1, new1)

old2 = 'rf"((?:{WORD}\\s+){{0,5}}(?:Penal Code|Code of Criminal Procedure|Insolvency and Bankruptcy Code)),?\\s*\\d{{4}}\\s*[:\\-]?\\s*ss?\\.?\\s*(\\d+[A-Za-z]?(?:/\\d+[A-Za-z]?)*(?:\\(\\w+\\))?)",'
new2 = 'rf"((?:{WORD}\\s+){{0,5}}(?:Penal Code|Code of Criminal Procedure|Insolvency and Bankruptcy Code)),?\\s*\\d{{4}}\\s*[:\\-]?\\s*(?:ss?\\.?|Sections?)\\s*(\\d+[A-Za-z]?(?:/\\d+[A-Za-z]?)*(?:\\(\\w+\\))?)",'
count2 = content.count(old2)
print(f"PATTERN_CODE_SECTION fix: found {count2}")
if count2 == 1:
    content = content.replace(old2, new2)

open("extract_citations.py", "w", encoding="utf-8").write(content)
print("Done")
