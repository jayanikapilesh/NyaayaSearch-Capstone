from search_core import SearchEngine

engine = SearchEngine()

case_law_style = [
    ("A person was released by the court on condition that they sign a bond promising to appear when summoned. What section covers this power to require such a bond?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "91"),
    ("When police arrest someone, is the officer required to tell them the general reason mentioned in the arrest warrant even if they don't have the actual paper on them?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "77"),
    ("A transport company applied for a permit to legally operate trucks carrying goods between states. What governs the process for granting them this permit?", "Motor Vehicles Act, 1988", "79"),
    ("During a criminal trial, must the witness testimony be given while the accused person is physically present in the courtroom?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "308"),
    ("A lender delayed suing a borrower for a long time, but never let the guarantor off the hook. Is the guarantor still liable even though the lender waited?", "Indian Contract Act, 1872", "137"),
    ("A magistrate finds the accused may be mentally unsound and unable to defend himself, but there is no strong case against him. What should the magistrate do?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "369"),
    ("A company ran an advertisement making false claims about their product's benefits, misleading buyers. What punishment could they face?", "Consumer Protection Act, 2019", "89"),
    ("Someone threatened to hurt a person to stop them from going to the police for help. What crime does that constitute?", "Bharatiya Nyaya Sanhita, 2023", "225"),
    ("A consumer lost their case at a lower commission and wants to challenge that decision at a higher forum. What allows them to do that?", "Consumer Protection Act, 2019", "24"),
    ("A person needs to swear an affidavit for their court case. In front of which authorities can this be legally done?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "333"),
    ("In a fight, one person intentionally injured the other without any weapon involved. What offence would this fall under?", "Bharatiya Nyaya Sanhita, 2023", "115"),
    ("A court ordered someone to maintain good behaviour for a set period as a security condition. From when does that period actually start counting?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "138"),
    ("A driver was caught going faster than the posted limit on the highway. What governs speed restrictions for vehicles?", "Motor Vehicles Act, 1988", "112"),
    ("After winning a case, can the court order the losing party to pay the legal costs incurred by the winning side?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "381"),
    ("If someone lets an unlicensed person drive their car and that person breaks the law, is the vehicle owner also responsible?", "Motor Vehicles Act, 1988", "5"),
    ("What qualifications must someone have to be appointed President of a District Consumer Commission?", "Consumer Protection Act, 2019", "29"),
    ("Is it mandatory for vehicle owners to carry insurance that covers damage they might cause to other people?", "Motor Vehicles Act, 1988", "146"),
    ("If someone fails to comply with a specific court-ordered obligation under section 154, what penalty applies?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "155"),
    ("In a contract dispute, one party claims they didn't freely agree to the terms. What legally counts as free consent?", "Indian Contract Act, 1872", "14"),
    ("A foreign company wants their digital certificates to be recognized as valid in India. What allows the Controller to recognize them?", "Information Technology Act, 2000", "19"),
]

hits5 = 0
for query, expected_act, expected_section in case_law_style:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        hits5 += 1

print(f"Case-law style: {hits5}/{len(case_law_style)} = {hits5/len(case_law_style):.3f} Recall@5")
