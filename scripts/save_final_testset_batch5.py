final_test_batch5 = [
    ("How is the standard rent for a property determined?", "Karnataka Rent Act, 1999", "7"),
    ("Can I get compensation if someone falsely accused me of a crime?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "273"),
    ("Where do I file a consumer complaint?", "Consumer Protection Act, 2019", "17"),
    ("How is notice served in a domestic violence case?", "Protection of Women from Domestic Violence Act, 2005", "13"),
    ("What's the punishment for using force to try to illegally trap someone?", "Bharatiya Nyaya Sanhita, 2023", "135"),
    ("Are hearings before the Rent Controller treated like a court case?", "Karnataka Rent Act, 1999", "60"),
    ("Can I be punished for something I did on a judge's order?", "Bharatiya Nyaya Sanhita, 2023", "16"),
    ("Can police offer me an incentive to confess?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "182"),
    ("What happens if I break the rules around my driving licence?", "Motor Vehicles Act, 1988", "182"),
    ("What's the punishment for attacking a foreign country India is at peace with?", "Bharatiya Nyaya Sanhita, 2023", "154"),
    ("Does the court keep records during a quick/summary trial?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "286"),
    ("If I owe multiple debts and don't specify which payment is for which, how is it applied?", "Indian Contract Act, 1872", "60"),
    ("Can a government official be punished for hiding knowledge of a planned crime?", "Bharatiya Nyaya Sanhita, 2023", "59"),
    ("What legally counts as a 'sale' of property?", "Transfer of Property Act, 1882", "54"),
    ("Do driving schools need a license to operate?", "Motor Vehicles Act, 1988", "12"),
    ("What actions are protected under the right to self-defence?", "Bharatiya Nyaya Sanhita, 2023", "34"),
    ("Can a landlord waive their own eviction notice?", "Transfer of Property Act, 1882", "113"),
    ("Can a Certifying Authority's license be suspended?", "Information Technology Act, 2000", "25"),
    ("Can I get relief against someone who later claims rights to my property?", "Specific Relief Act, 1963", "19"),
    ("Can a court order more evidence to be gathered after a trial starts?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "408"),
    ("Which tribunal handles appeals under the IT Act?", "Information Technology Act, 2000", "48"),
    ("What's the punishment for secretly photographing someone in a private moment?", "Information Technology Act, 2000", "66E"),
    ("Are e-rickshaws covered under the Motor Vehicles Act?", "Motor Vehicles Act, 1988", "2A"),
    ("Do I need to physically bring my vehicle for registration?", "Motor Vehicles Act, 1988", "44"),
    ("Can my rent be revised under special circumstances?", "Karnataka Rent Act, 1999", "9"),
    ("Am I protected if I did something believing I was legally justified?", "Bharatiya Nyaya Sanhita, 2023", "17"),
    ("What are 'service providers' under the Domestic Violence Act?", "Protection of Women from Domestic Violence Act, 2005", "10"),
    ("Can I appeal a District Consumer Commission's decision?", "Consumer Protection Act, 2019", "41"),
    ("What happens if I can't pay a fine - do I go to jail instead?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "24"),
    ("Can accident victims get interim financial relief before the case is resolved?", "Motor Vehicles Act, 1988", "164A"),
]

import json
with open("../data/eval/final_test_set_batch5.json", "w", encoding="utf-8") as f:
    json.dump(final_test_batch5, f, indent=2)
print(f"Saved {len(final_test_batch5)} queries to final_test_set_batch5.json")
