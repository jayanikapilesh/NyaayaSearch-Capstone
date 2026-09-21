from search_core import SearchEngine

engine = SearchEngine()

simple_direct = [
    ("What is the punishment for kidnapping a child under 10 to steal from them?", "Bharatiya Nyaya Sanhita, 2023", "97"),
    ("What liability does a transferee of an actionable claim have?", "Transfer of Property Act, 1882", "132"),
    ("Who is allowed to act as an agent under contract law?", "Indian Contract Act, 1872", "184"),
    ("What is the punishment for causing death while attempting to cause a miscarriage?", "Bharatiya Nyaya Sanhita, 2023", "90"),
    ("What is the Central Consumer Protection Authority?", "Consumer Protection Act, 2019", "10"),
    ("Who has the power to make rules under the RTI Act?", "Right to Information Act, 2005", "28"),
    ("What counts as making a false document?", "Bharatiya Nyaya Sanhita, 2023", "335"),
    ("Can the licensing authority revoke my driving licence?", "Motor Vehicles Act, 1988", "19"),
    ("Does the Domestic Violence Act provide for counselling?", "Protection of Women from Domestic Violence Act, 2005", "14"),
    ("What is the legal definition of cheating?", "Bharatiya Nyaya Sanhita, 2023", "318"),
    ("What is the punishment for rioting?", "Bharatiya Nyaya Sanhita, 2023", "191"),
    ("What is the punishment for encouraging a soldier to disobey orders?", "Bharatiya Nyaya Sanhita, 2023", "166"),
    ("Does the Certifying Authority have to notify me if my Digital Signature Certificate is revoked?", "Information Technology Act, 2000", "39"),
    ("What is a surety's liability under contract law?", "Indian Contract Act, 1872", "128"),
    ("Can I get relief if my lease is forfeited for not paying rent?", "Transfer of Property Act, 1882", "114"),
    ("What is the punishment for conspiracy to commit rioting?", "Bharatiya Nyaya Sanhita, 2023", "148"),
    ("What is the punishment for fraudulently obtaining a court decree for money not owed?", "Bharatiya Nyaya Sanhita, 2023", "247"),
    ("Can I deposit money instead of a recognizance bond?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "490"),
    ("What is the punishment for procuring a child for illegal purposes?", "Bharatiya Nyaya Sanhita, 2023", "96"),
    ("What is the punishment for assaulting a public servant to stop them doing their duty?", "Bharatiya Nyaya Sanhita, 2023", "132"),
]

synonym_heavy = [
    ("Someone snatched a young kid to rob them, what crime is that?", "Bharatiya Nyaya Sanhita, 2023", "97"),
    ("If someone owes me money and sells that debt to another person, what happens to me?", "Transfer of Property Act, 1882", "132"),
    ("Who's allowed to act on my behalf in a deal?", "Indian Contract Act, 1872", "184"),
    ("A person died because someone tried to end a pregnancy, what's the punishment?", "Bharatiya Nyaya Sanhita, 2023", "90"),
    ("Who makes the rulebook for RTI?", "Right to Information Act, 2005", "28"),
    ("Is faking a document illegal?", "Bharatiya Nyaya Sanhita, 2023", "335"),
    ("Can they take away my license?", "Motor Vehicles Act, 1988", "19"),
    ("Can victims get therapy under this law?", "Protection of Women from Domestic Violence Act, 2005", "14"),
    ("Someone tricked me out of my money, what crime is that?", "Bharatiya Nyaya Sanhita, 2023", "318"),
    ("A mob got violent in public, what's the charge?", "Bharatiya Nyaya Sanhita, 2023", "191"),
    ("Do they have to tell me if my digital certificate gets cancelled?", "Information Technology Act, 2000", "39"),
    ("If I guarantee someone's loan, what am I on the hook for?", "Indian Contract Act, 1872", "128"),
    ("Can I stop my landlord from kicking me out over late rent?", "Transfer of Property Act, 1882", "114"),
    ("If I plan a riot with others but it doesn't happen, am I still in trouble?", "Bharatiya Nyaya Sanhita, 2023", "148"),
    ("Someone tricked a court into giving them money I don't owe, is that illegal?", "Bharatiya Nyaya Sanhita, 2023", "247"),
    ("Can I pay cash instead of signing a bond?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "490"),
    ("Is it illegal to arrange for a child to be used for bad purposes?", "Bharatiya Nyaya Sanhita, 2023", "96"),
    ("Someone pushed a cop to stop them from doing their job, what's the charge?", "Bharatiya Nyaya Sanhita, 2023", "132"),
    ("Encouraging a soldier to defy commands, is that a crime?", "Bharatiya Nyaya Sanhita, 2023", "166"),
    ("Is there a government body that protects buyers?", "Consumer Protection Act, 2019", "10"),
]

def run_category(name, queries):
    hits5 = 0
    for query, expected_act, expected_section in queries:
        results = engine.search(query, top_k=5)
        hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
        if hit:
            hits5 += 1
    print(f"{name}: {hits5}/{len(queries)} = {hits5/len(queries):.3f} Recall@5")
    return hits5, len(queries)

print("=" * 60)
h1, n1 = run_category("Simple/Direct", simple_direct)
h2, n2 = run_category("Synonym-heavy", synonym_heavy)
print("=" * 60)
print(f"\nCombined category batch: {h1+h2}/{n1+n2} = {(h1+h2)/(n1+n2):.3f}")
