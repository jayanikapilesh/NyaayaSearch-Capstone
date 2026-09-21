final_test_batch3 = [
    ("Am I still guilty of a crime if someone forced me to do it under threat?", "Bharatiya Nyaya Sanhita, 2023", "32"),
    ("What's the punishment for selling a child into prostitution?", "Bharatiya Nyaya Sanhita, 2023", "98"),
    ("What's the punishment for an acid attack?", "Bharatiya Nyaya Sanhita, 2023", "124"),
    ("What counts as 'grievous hurt' under the law?", "Bharatiya Nyaya Sanhita, 2023", "116"),
    ("Can I be punished for carelessly handling explosives?", "Bharatiya Nyaya Sanhita, 2023", "288"),
    ("What's the punishment for reckless driving?", "Bharatiya Nyaya Sanhita, 2023", "281"),
    ("Can I be penalized for leaking confidential information I agreed to protect?", "Information Technology Act, 2000", "72A"),
    ("What's the punishment for pretending to be someone else online to cheat them?", "Information Technology Act, 2000", "66D"),
    ("Can I appeal a rent tribunal's decision?", "Karnataka Rent Act, 1999", "26"),
    ("Can a court set a temporary rent amount while a dispute is ongoing?", "Karnataka Rent Act, 1999", "13"),
    ("Who appoints Protection Officers under the domestic violence law?", "Protection of Women from Domestic Violence Act, 2005", "8"),
    ("What counts as legal consent in a contract?", "Indian Contract Act, 1872", "13"),
    ("Is a guarantee void if someone hid important facts to get it?", "Indian Contract Act, 1872", "143"),
    ("Can I cancel a contract I was pressured into signing?", "Indian Contract Act, 1872", "19A"),
    ("Who is legally allowed to enter into a contract?", "Indian Contract Act, 1872", "11"),
    ("How do I legally get back my stolen movable property?", "Specific Relief Act, 1963", "7"),
    ("What's the fine for speeding?", "Motor Vehicles Act, 1988", "183"),
    ("Can the licensing authority ban me from driving?", "Motor Vehicles Act, 1988", "34"),
    ("Can I get relief if my lease is being forfeited?", "Transfer of Property Act, 1882", "114A"),
    ("What are my rights in an exchange of property?", "Transfer of Property Act, 1882", "120"),
    ("Do police have to ensure my health and safety after arrest?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "56"),
    ("Can armed forces disperse an unlawful gathering?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "150"),
    ("Can a court dismiss my complaint without a trial?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "226"),
    ("Is it a crime to hide that I know someone plans to commit a crime?", "Bharatiya Nyaya Sanhita, 2023", "60"),
    ("Can a child under 7 be held criminally responsible?", "Bharatiya Nyaya Sanhita, 2023", "20"),
    ("Can a 10-year-old be punished for a crime?", "Bharatiya Nyaya Sanhita, 2023", "21"),
    ("Can I have a lawyer represent me in a Cyber Tribunal case?", "Information Technology Act, 2000", "59"),
    ("Can an official be punished for knowingly detaining someone illegally?", "Bharatiya Nyaya Sanhita, 2023", "258"),
    ("Is it a crime to alter a product's trademark to cause harm?", "Bharatiya Nyaya Sanhita, 2023", "346"),
    ("Does the court keep an official record of questioning the accused?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "316"),
]

import json
with open("../data/eval/final_test_set_batch3.json", "w", encoding="utf-8") as f:
    json.dump(final_test_batch3, f, indent=2)
print(f"Saved {len(final_test_batch3)} queries to final_test_set_batch3.json")
