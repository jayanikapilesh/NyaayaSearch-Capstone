content = open("extract_citations.py", encoding="utf-8").read()

old1 = "Act,?\\s*\\d{{4}}"
new1 = "Act[,.]?\\s*\\d{{4}}"
count1 = content.count(old1)
print(f"Act pattern fix: found {count1}")
content = content.replace(old1, new1)

old2 = "Code)),?\\s*\\d{{4}}"
new2 = "Code))[,.]?\\s*\\d{{4}}"
count2 = content.count(old2)
print(f"Code pattern fix: found {count2}")
content = content.replace(old2, new2)

open("extract_citations.py", "w", encoding="utf-8").write(content)
print("Done")
