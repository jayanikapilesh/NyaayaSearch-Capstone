content = open("extract_citations.py", encoding="utf-8").read()

# Fix the two [:\-]? occurrences to also accept en-dash (U+2013) and em-dash (U+2014)
old1 = "[:\\-]?"
new1 = "[:\\-\u2013\u2014]?"
count1 = content.count(old1)
print(f"[:\\-]? occurrences found: {count1}")
content = content.replace(old1, new1)

# Fix the standalone "-?" on the ACT_SECTION pattern too
old2 = 'Act,?\\s*\\d{{4}})\\s*-?\\s*'
new2 = 'Act,?\\s*\\d{{4}})\\s*[\\-\u2013\u2014]?\\s*'
count2 = content.count(old2)
print(f"Standalone -? occurrences found: {count2}")
content = content.replace(old2, new2)

open("extract_citations.py", "w", encoding="utf-8").write(content)
print("Done - all dash patterns now accept regular hyphen, en-dash, and em-dash")
