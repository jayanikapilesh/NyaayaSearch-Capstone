from search_core import SearchEngine

engine = SearchEngine()

fresh_synonym_validation = [
    ("What happens if I ride a bus without a ticket?", "Motor Vehicles Act, 1988", "178"),
    ("Can I find out info about someone else through RTI?", "Right to Information Act, 2005", "11"),
    ("Is lying to officials against the law?", "Bharatiya Nyaya Sanhita, 2023", "212"),
    ("Can I challenge a Motor Vehicles decision?", "Motor Vehicles Act, 1988", "90"),
    ("Does a junior cop have to write up findings after investigating?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "188"),
    ("How do I get a permit to run a private hire vehicle?", "Motor Vehicles Act, 1988", "73"),
    ("Is it illegal to use a fake certificate as if it's real?", "Bharatiya Nyaya Sanhita, 2023", "340"),
    ("How does the prosecution side present its case?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "265"),
    ("Who can go to court to get their mortgaged property back?", "Transfer of Property Act, 1882", "91"),
    ("When does a sub-agent stop being allowed to act?", "Indian Contract Act, 1872", "210"),
    ("Is catcalling a woman illegal?", "Bharatiya Nyaya Sanhita, 2023", "79"),
    ("Can a judge personally arrest someone?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "41"),
    ("Can I appeal if a court makes me post bail money for keeping the peace?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "414"),
    ("If I follow a court order, can I get in trouble for it?", "Bharatiya Nyaya Sanhita, 2023", "16"),
    ("Does the consumer authority have to keep financial records?", "Consumer Protection Act, 2019", "26"),
]

hits = 0
for query, expected_act, expected_section in fresh_synonym_validation:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        hits += 1
    print(f"{'YES' if hit else 'NO':<5} {query}")

n = len(fresh_synonym_validation)
print(f"\nFresh synonym-heavy validation (never used before): {hits}/{n} = {hits/n:.3f}")
