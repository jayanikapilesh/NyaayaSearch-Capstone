content = open("rag_core.py", encoding="utf-8").read()

old = (
    '                            "You rewrite everyday legal questions into the formal legal "\n'
    '                            "terminology an Indian statute would actually use, to improve "\n'
    "                            \"search matching. For example: 'seriously injuring someone' -> \"\n"
    "                            \"'grievous hurt'. 'reckless driving' -> 'rash driving'. \"\n"
    "                            \"'getting property back from someone occupying it' -> 'recovery \"\n"
    "                            \"of possession'. 'sending a court notice' -> 'service of summons'. \"\n"
    '                            "Keep the rewritten question short and natural, just replacing "\n'
    '                            "vague everyday words with the specific legal terms they map to. "\n'
    '                            "Return ONLY the rewritten question, nothing else - Use current Indian law names (Bharatiya Nyaya Sanhita/BNS, Bharatiya Nagarik Suraksha Sanhita/BNSS), never the old repealed IPC or CrPC. Return ONLY the rewritten question, nothing else - no explanation, "\n'
    '                            "no quotes."'
)

new = (
    '                            "You rewrite everyday legal questions into the formal legal "\n'
    '                            "terminology an Indian statute would actually use, to improve "\n'
    "                            \"search matching. For example: 'seriously injuring someone' -> \"\n"
    "                            \"'grievous hurt'. 'reckless driving' -> 'rash driving'. \"\n"
    "                            \"'getting property back from someone occupying it' -> 'recovery \"\n"
    "                            \"of possession'. 'sending a court notice' -> 'service of summons'. \"\n"
    '                            "Keep the rewritten question short and natural, just replacing "\n'
    '                            "vague everyday words with the specific legal terms they map to. "\n'
    '                            "Use current Indian law names (Bharatiya Nyaya Sanhita/BNS, "\n'
    '                            "Bharatiya Nagarik Suraksha Sanhita/BNSS), never the old repealed "\n'
    '                            "IPC or CrPC. Return ONLY the rewritten question, nothing else - "\n'
    '                            "no explanation, no quotes."'
)

count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("rag_core.py", "w", encoding="utf-8").write(content)
    print("Fixed cleanly")
