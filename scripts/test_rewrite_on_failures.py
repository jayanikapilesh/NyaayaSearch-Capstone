from search_core import SearchEngine
from rag_core import rewrite_query_for_search

engine = SearchEngine()

failures = [
    ("What's the punishment for seriously injuring someone on purpose?", "Bharatiya Nyaya Sanhita, 2023", "117"),
    ("Can a domestic violence victim get financial compensation?", "Protection of Women from Domestic Violence Act, 2005", "20"),
    ("Do I have to give the property back empty when I move out?", "Karnataka Rent Act, 1999", "41"),
    ("Does the court try to settle rent disputes outside trial?", "Karnataka Rent Act, 1999", "44"),
    ("Can I get my mortgaged property back after paying off the loan?", "Transfer of Property Act, 1882", "62"),
    ("Is it illegal to create a fake digital certificate to scam someone?", "Information Technology Act, 2000", "74"),
    ("Is it illegal to stop someone from receiving a court summons?", "Bharatiya Nyaya Sanhita, 2023", "207"),
    ("How does the court officially deliver a summons?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "64"),
    ("What does it mean for a court to take cognizance of a crime?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "221"),
    ("Am I required to help someone who's executing an arrest warrant?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "32"),
    ("Does the magistrate check if a complaint is true before acting?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "135"),
    ("How does a court grant an injunction to prevent something?", "Specific Relief Act, 1963", "36"),
    ("Can a public servant be punished for deliberately letting a criminal escape?", "Bharatiya Nyaya Sanhita, 2023", "260"),
    ("What's the punishment for hurting someone to force them to pay you?", "Bharatiya Nyaya Sanhita, 2023", "119"),
    ("Can something still be a crime even if no one was harmed?", "Bharatiya Nyaya Sanhita, 2023", "29"),
    ("What's the punishment for encouraging a large group to commit a crime?", "Bharatiya Nyaya Sanhita, 2023", "57"),
    ("Can I let someone off from fulfilling their part of a contract?", "Indian Contract Act, 1872", "63"),
    ("What counts as 'grievous hurt' under the law?", "Bharatiya Nyaya Sanhita, 2023", "116"),
    ("What's the punishment for reckless driving?", "Bharatiya Nyaya Sanhita, 2023", "281"),
    ("Can I appeal a rent tribunal's decision?", "Karnataka Rent Act, 1999", "26"),
]

hits = 0
for query, expected_act, expected_section in failures:
    rewritten = rewrite_query_for_search(query)
    results = engine.search(rewritten, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    status = "FIXED" if hit else "still fails"
    if hit:
        hits += 1
    print(f"{status:12} | rewritten: {rewritten}")

print(f"\n{hits}/{len(failures)} previously-failing queries now succeed with query rewriting")
