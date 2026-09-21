final_test_batch1 = [
    ("What's the punishment for trying to kill someone but failing?", "Bharatiya Nyaya Sanhita, 2023", "109"),
    ("What's the punishment for seriously injuring someone on purpose?", "Bharatiya Nyaya Sanhita, 2023", "117"),
    ("Can a company be punished for false advertising?", "Consumer Protection Act, 2019", "89"),
    ("Can a shop be held responsible for selling a defective product?", "Consumer Protection Act, 2019", "86"),
    ("Can a manufacturer be sued for a faulty product?", "Consumer Protection Act, 2019", "84"),
    ("Do police have to tell me why I'm being arrested?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "47"),
    ("Can a domestic violence victim get financial compensation?", "Protection of Women from Domestic Violence Act, 2005", "20"),
    ("Can a domestic violence case affect child custody?", "Protection of Women from Domestic Violence Act, 2005", "21"),
    ("Do I have to give the property back empty when I move out?", "Karnataka Rent Act, 1999", "41"),
    ("Does the court try to settle rent disputes outside trial?", "Karnataka Rent Act, 1999", "44"),
    ("Can I get my mortgaged property back after paying off the loan?", "Transfer of Property Act, 1882", "62"),
    ("When will a court refuse to grant an injunction?", "Specific Relief Act, 1963", "41"),
    ("Can I force someone to complete a personal service contract?", "Specific Relief Act, 1963", "14"),
    ("How do I legally recover my property from someone occupying it?", "Specific Relief Act, 1963", "5"),
    ("Can I get my pawned item back even after missing the deadline?", "Indian Contract Act, 1872", "177"),
    ("Can my agent hire someone else to do my work without asking me?", "Indian Contract Act, 1872", "190"),
    ("What happens if both parties agree to change a contract?", "Indian Contract Act, 1872", "62"),
    ("Is it illegal to create a fake digital certificate to scam someone?", "Information Technology Act, 2000", "74"),
    ("Can I appeal a Cyber Tribunal decision to the High Court?", "Information Technology Act, 2000", "62"),
    ("Can the government tap my internet communications?", "Information Technology Act, 2000", "69"),
    ("What's the punishment for sabotaging a train?", "Bharatiya Nyaya Sanhita, 2023", "327"),
    ("Is it a crime to knowingly spread a dangerous disease?", "Bharatiya Nyaya Sanhita, 2023", "272"),
    ("What's the punishment for recklessly endangering someone's life?", "Bharatiya Nyaya Sanhita, 2023", "125"),
    ("Is it illegal to stop someone from receiving a court summons?", "Bharatiya Nyaya Sanhita, 2023", "207"),
    ("How does the court officially deliver a summons?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "64"),
    ("What does it mean for a court to take cognizance of a crime?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "221"),
    ("Does a magistrate investigate suspicious deaths?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "196"),
    ("Am I required to help someone who's executing an arrest warrant?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "32"),
    ("Does the magistrate check if a complaint is true before acting?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "135"),
    ("Can my insurance company settle a claim directly with me?", "Motor Vehicles Act, 1988", "153"),
]

import json
with open("../data/eval/final_test_set_batch1.json", "w", encoding="utf-8") as f:
    json.dump(final_test_batch1, f, indent=2)
print(f"Saved {len(final_test_batch1)} queries to final_test_set_batch1.json")
