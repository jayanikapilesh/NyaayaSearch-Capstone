from search_core import SearchEngine

engine = SearchEngine()

failures = [
    ("What's the punishment for seriously injuring someone on purpose?", "Bharatiya Nyaya Sanhita, 2023", "117"),
    ("What's the punishment for reckless driving?", "Bharatiya Nyaya Sanhita, 2023", "281"),
    ("How does the court officially deliver a summons?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "64"),
    ("What does it mean for a court to take cognizance of a crime?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "221"),
    ("Can I get my mortgaged property back after paying off the loan?", "Transfer of Property Act, 1882", "62"),
    ("Can a domestic violence victim get financial compensation?", "Protection of Women from Domestic Violence Act, 2005", "20"),
    ("Is it illegal to create a fake digital certificate to scam someone?", "Information Technology Act, 2000", "74"),
    ("Does the court try to settle rent disputes outside trial?", "Karnataka Rent Act, 1999", "44"),
    ("Can a public servant be punished for deliberately letting a criminal escape?", "Bharatiya Nyaya Sanhita, 2023", "260"),
    ("What's the punishment for hurting someone to force them to pay you?", "Bharatiya Nyaya Sanhita, 2023", "119"),
    ("What's the punishment for encouraging a large group to commit a crime?", "Bharatiya Nyaya Sanhita, 2023", "57"),
    ("Can I let someone off from fulfilling their part of a contract?", "Indian Contract Act, 1872", "63"),
    ("Who has authority to make rules under the Domestic Violence Act?", "Protection of Women from Domestic Violence Act, 2005", "37"),
    ("Can I be prosecuted for disrespecting a public official's lawful order?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "215"),
    ("Do small mistakes in my case automatically cancel the trial?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "506"),
]

hits = 0
for query, expected_act, expected_section in failures:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    status = "FIXED" if hit else "still fails"
    if hit:
        hits += 1
    print(f"{status:12} | {query}")

print(f"\n{hits}/{len(failures)} targeted failures now succeed with new synonyms")
