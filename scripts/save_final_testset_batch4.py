final_test_batch4 = [
    ("Can I sue someone for defamation?", "Bharatiya Nyaya Sanhita, 2023", "356"),
    ("What's the difference between murder and culpable homicide?", "Bharatiya Nyaya Sanhita, 2023", "105"),
    ("What legally counts as rape under Indian law?", "Bharatiya Nyaya Sanhita, 2023", "63"),
    ("What's the penalty for overloading a truck?", "Motor Vehicles Act, 1988", "194"),
    ("Can my driving licence be revoked due to a medical condition?", "Motor Vehicles Act, 1988", "16"),
    ("Can I force a trust to fulfill its contractual obligations?", "Specific Relief Act, 1963", "11"),
    ("Can a contract be enforced with modified terms?", "Specific Relief Act, 1963", "18"),
    ("Does my agent have to hand over money they collected on my behalf?", "Indian Contract Act, 1872", "218"),
    ("Is a contract void if I made a mistake about the law?", "Indian Contract Act, 1872", "21"),
    ("What's the punishment for taking away someone's wife against her will?", "Bharatiya Nyaya Sanhita, 2023", "84"),
    ("Is it illegal to fake the label on a product container?", "Bharatiya Nyaya Sanhita, 2023", "350"),
    ("What are the penalties for violating the Rent Act?", "Karnataka Rent Act, 1999", "54"),
    ("Do I need to notify the landlord if I sublet my rented place?", "Karnataka Rent Act, 1999", "33"),
    ("Can a sub-tenant become a full tenant in some situations?", "Karnataka Rent Act, 1999", "34"),
    ("Can I get compensation if I was wrongly arrested?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "399"),
    ("Can police prevent damage to public property?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "171"),
    ("Is it illegal to obstruct a bus or taxi driver while they're driving?", "Motor Vehicles Act, 1988", "125"),
    ("Are there legal safety requirements for motorcycle riders?", "Motor Vehicles Act, 1988", "128"),
    ("Can a transport permit be cancelled?", "Motor Vehicles Act, 1988", "86"),
    ("How is compensation calculated after a motor vehicle accident?", "Motor Vehicles Act, 1988", "105"),
    ("Who has authority to make rules under the Domestic Violence Act?", "Protection of Women from Domestic Violence Act, 2005", "37"),
    ("Can a court require additional security for the remaining bond period?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "143"),
    ("Can I be prosecuted for disrespecting a public official's lawful order?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "215"),
    ("Can the government seize copies of a banned publication?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "98"),
    ("What does a court have to include in its judgment?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "294"),
    ("Can a witness avoid attending court and give evidence another way?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "319"),
    ("Can a paused court case resume later?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "370"),
    ("What's the punishment for encouraging a soldier to attack a superior officer?", "Bharatiya Nyaya Sanhita, 2023", "161"),
    ("How is property divided when multiple people jointly buy it?", "Transfer of Property Act, 1882", "45"),
    ("Can a Sessions Judge review a lower court's decision?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "440"),
]

import json
with open("../data/eval/final_test_set_batch4.json", "w", encoding="utf-8") as f:
    json.dump(final_test_batch4, f, indent=2)
print(f"Saved {len(final_test_batch4)} queries to final_test_set_batch4.json")
