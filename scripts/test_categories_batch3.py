from search_core import SearchEngine

engine = SearchEngine()

specific_concepts = [
    ("What is seizure or attachment of property?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "117"),
    ("What happens when a pledge is made by someone with only a limited interest?", "Indian Contract Act, 1872", "179"),
    ("What is a Claims Tribunal under the Motor Vehicles Act?", "Motor Vehicles Act, 1988", "165"),
    ("What is a contingent contract?", "Indian Contract Act, 1872", "31"),
    ("What are the liabilities of a mortgagee in possession?", "Transfer of Property Act, 1882", "76"),
    ("What are special provisions for infrastructure project contracts?", "Specific Relief Act, 1963", "20A"),
    ("How do I file an appeal under the RTI Act?", "Right to Information Act, 2005", "19"),
    ("What is tender of pardon to an accomplice?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "343"),
    ("What is unlawful compulsory labour?", "Bharatiya Nyaya Sanhita, 2023", "146"),
    ("What is the procedure when the accused is of unsound mind?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "367"),
    ("How do I apply for compensation after a motor vehicle accident?", "Motor Vehicles Act, 1988", "166"),
    ("What is a mercy petition in a death sentence case?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "472"),
    ("When does the right of private defence extend to causing harm other than death?", "Bharatiya Nyaya Sanhita, 2023", "42"),
    ("What is release on probation of good conduct?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "401"),
    ("What happens if consent is given under fear or misconception?", "Bharatiya Nyaya Sanhita, 2023", "28"),
    ("What is the right to inspection and production of documents?", "Transfer of Property Act, 1882", "60B"),
    ("What is subrogation in property law?", "Transfer of Property Act, 1882", "92"),
    ("What is the punishment for a public servant disobeying law to cause injury?", "Bharatiya Nyaya Sanhita, 2023", "198"),
    ("What constitutes organised crime?", "Bharatiya Nyaya Sanhita, 2023", "111"),
    ("What is the punishment for disturbing a religious assembly?", "Bharatiya Nyaya Sanhita, 2023", "300"),
]

natural_language = [
    ("Do court judgments have to be in a specific language?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "288"),
    ("My tenant sublet the place without telling me, is there supposed to be a notice for that?", "Karnataka Rent Act, 1999", "33"),
    ("My neighbor lied on some official form, can that get him in trouble?", "Bharatiya Nyaya Sanhita, 2023", "236"),
    ("Where do I even go to complain about a store near me?", "Consumer Protection Act, 2019", "28"),
    ("What if someone doesn't follow the court's evidence rules?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "509"),
    ("Does my driving licence work everywhere in India?", "Motor Vehicles Act, 1988", "13"),
    ("Can I get in trouble for parking in the wrong spot?", "Motor Vehicles Act, 1988", "117"),
    ("When is someone actually allowed to get bail?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "478"),
    ("Can the High Court just make up its own rules?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "523"),
    ("What happens with empty plots of land under this rent law?", "Karnataka Rent Act, 1999", "40"),
    ("So if there's a warrant out for me, what actually happens when they catch me?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "82"),
    ("Once a judge decides my case, is that really the final word?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "295"),
    ("Am I supposed to help the police if they ask?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "31"),
    ("Can someone else handle my prosecution for me?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "339"),
    ("Can I take my traffic case to a regular civil court?", "Motor Vehicles Act, 1988", "175"),
    ("I got in an accident driving too fast, what am I looking at legally?", "Bharatiya Nyaya Sanhita, 2023", "281"),
    ("What can the police actually search on me after they arrest me?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "49"),
    ("What defences do I have if someone sues me over a contract?", "Specific Relief Act, 1963", "9"),
    ("How does the prosecution actually present evidence in my case?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "254"),
    ("What if I plead guilty but I'm not even there in court?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "276"),
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
h1, n1 = run_category("Specific Legal Concepts", specific_concepts)
h2, n2 = run_category("Natural-language", natural_language)
print("=" * 60)
print(f"\nCombined category batch 3: {h1+h2}/{n1+n2} = {(h1+h2)/(n1+n2):.3f}")
