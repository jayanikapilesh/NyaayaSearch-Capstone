import json
from search_core import SearchEngine

engine = SearchEngine()

# All 149 category queries, with category label
all_category_queries = [
    ("Simple/Direct", "What is the punishment for kidnapping a child under 10 to steal from them?", "Bharatiya Nyaya Sanhita, 2023", "97"),
    ("Simple/Direct", "What liability does a transferee of an actionable claim have?", "Transfer of Property Act, 1882", "132"),
    ("Simple/Direct", "Who is allowed to act as an agent under contract law?", "Indian Contract Act, 1872", "184"),
    ("Simple/Direct", "What is the punishment for causing death while attempting to cause a miscarriage?", "Bharatiya Nyaya Sanhita, 2023", "90"),
    ("Simple/Direct", "What is the Central Consumer Protection Authority?", "Consumer Protection Act, 2019", "10"),
    ("Simple/Direct", "Who has the power to make rules under the RTI Act?", "Right to Information Act, 2005", "28"),
    ("Simple/Direct", "What counts as making a false document?", "Bharatiya Nyaya Sanhita, 2023", "335"),
    ("Simple/Direct", "Can the licensing authority revoke my driving licence?", "Motor Vehicles Act, 1988", "19"),
    ("Simple/Direct", "Does the Domestic Violence Act provide for counselling?", "Protection of Women from Domestic Violence Act, 2005", "14"),
    ("Simple/Direct", "What is the legal definition of cheating?", "Bharatiya Nyaya Sanhita, 2023", "318"),
    ("Simple/Direct", "What is the punishment for rioting?", "Bharatiya Nyaya Sanhita, 2023", "191"),
    ("Simple/Direct", "What is the punishment for encouraging a soldier to disobey orders?", "Bharatiya Nyaya Sanhita, 2023", "166"),
    ("Simple/Direct", "Does the Certifying Authority have to notify me if my Digital Signature Certificate is revoked?", "Information Technology Act, 2000", "39"),
    ("Simple/Direct", "What is a surety's liability under contract law?", "Indian Contract Act, 1872", "128"),
    ("Simple/Direct", "Can I get relief if my lease is forfeited for not paying rent?", "Transfer of Property Act, 1882", "114"),
    ("Simple/Direct", "What is the punishment for conspiracy to commit rioting?", "Bharatiya Nyaya Sanhita, 2023", "148"),
    ("Simple/Direct", "What is the punishment for fraudulently obtaining a court decree for money not owed?", "Bharatiya Nyaya Sanhita, 2023", "247"),
    ("Simple/Direct", "Can I deposit money instead of a recognizance bond?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "490"),
    ("Simple/Direct", "What is the punishment for procuring a child for illegal purposes?", "Bharatiya Nyaya Sanhita, 2023", "96"),
    ("Simple/Direct", "What is the punishment for assaulting a public servant to stop them doing their duty?", "Bharatiya Nyaya Sanhita, 2023", "132"),

    ("Synonym-heavy", "Someone snatched a young kid to rob them, what crime is that?", "Bharatiya Nyaya Sanhita, 2023", "97"),
    ("Synonym-heavy", "If someone owes me money and sells that debt to another person, what happens to me?", "Transfer of Property Act, 1882", "132"),
    ("Synonym-heavy", "Who's allowed to act on my behalf in a deal?", "Indian Contract Act, 1872", "184"),
    ("Synonym-heavy", "A person died because someone tried to end a pregnancy, what's the punishment?", "Bharatiya Nyaya Sanhita, 2023", "90"),
    ("Synonym-heavy", "Who makes the rulebook for RTI?", "Right to Information Act, 2005", "28"),
    ("Synonym-heavy", "Is faking a document illegal?", "Bharatiya Nyaya Sanhita, 2023", "335"),
    ("Synonym-heavy", "Can they take away my license?", "Motor Vehicles Act, 1988", "19"),
    ("Synonym-heavy", "Can victims get therapy under this law?", "Protection of Women from Domestic Violence Act, 2005", "14"),
    ("Synonym-heavy", "Someone tricked me out of my money, what crime is that?", "Bharatiya Nyaya Sanhita, 2023", "318"),
    ("Synonym-heavy", "A mob got violent in public, what's the charge?", "Bharatiya Nyaya Sanhita, 2023", "191"),
    ("Synonym-heavy", "Do they have to tell me if my digital certificate gets cancelled?", "Information Technology Act, 2000", "39"),
    ("Synonym-heavy", "If I guarantee someone's loan, what am I on the hook for?", "Indian Contract Act, 1872", "128"),
    ("Synonym-heavy", "Can I stop my landlord from kicking me out over late rent?", "Transfer of Property Act, 1882", "114"),
    ("Synonym-heavy", "If I plan a riot with others but it doesn't happen, am I still in trouble?", "Bharatiya Nyaya Sanhita, 2023", "148"),
    ("Synonym-heavy", "Someone tricked a court into giving them money I don't owe, is that illegal?", "Bharatiya Nyaya Sanhita, 2023", "247"),
    ("Synonym-heavy", "Can I pay cash instead of signing a bond?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "490"),
    ("Synonym-heavy", "Is it illegal to arrange for a child to be used for bad purposes?", "Bharatiya Nyaya Sanhita, 2023", "96"),
    ("Synonym-heavy", "Someone pushed a cop to stop them from doing their job, what's the charge?", "Bharatiya Nyaya Sanhita, 2023", "132"),
    ("Synonym-heavy", "Encouraging a soldier to defy commands, is that a crime?", "Bharatiya Nyaya Sanhita, 2023", "166"),
    ("Synonym-heavy", "Is there a government body that protects buyers?", "Consumer Protection Act, 2019", "10"),

    ("BNS/BNSS Terminology", "What is the punishment for bribery?", "Bharatiya Nyaya Sanhita, 2023", "173"),
    ("BNS/BNSS Terminology", "How are contracts contingent on an event happening enforced?", "Indian Contract Act, 1872", "32"),
    ("BNS/BNSS Terminology", "What is an oral transfer of property?", "Transfer of Property Act, 1882", "9"),
    ("BNS/BNSS Terminology", "Do intermediaries have to preserve and retain information?", "Information Technology Act, 2000", "67C"),
    ("BNS/BNSS Terminology", "What is a contract of guarantee?", "Indian Contract Act, 1872", "126"),
    ("BNS/BNSS Terminology", "Can the licensing authority disqualify someone from holding a licence?", "Motor Vehicles Act, 1988", "34"),
    ("BNS/BNSS Terminology", "How is a transfer of actionable claim executed?", "Transfer of Property Act, 1882", "130"),
    ("BNS/BNSS Terminology", "What is dishonest misappropriation of property possessed by a deceased person?", "Bharatiya Nyaya Sanhita, 2023", "315"),
    ("BNS/BNSS Terminology", "What is the jurisdiction under the Domestic Violence Act?", "Protection of Women from Domestic Violence Act, 2005", "27"),
    ("BNS/BNSS Terminology", "What happens with sentencing for an offender already sentenced for another offence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "467"),
    ("BNS/BNSS Terminology", "What is a mortgagor's right of redemption?", "Transfer of Property Act, 1882", "60"),
    ("BNS/BNSS Terminology", "What is the punishment for counterfeiting currency notes?", "Bharatiya Nyaya Sanhita, 2023", "178"),
    ("BNS/BNSS Terminology", "What is the punishment for attempting suicide to compel exercise of lawful power?", "Bharatiya Nyaya Sanhita, 2023", "226"),
    ("BNS/BNSS Terminology", "What is a continuing offence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "518"),
    ("BNS/BNSS Terminology", "What happens upon conviction on a plea of guilty?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "252"),
    ("BNS/BNSS Terminology", "What is house-trespass and house-breaking?", "Bharatiya Nyaya Sanhita, 2023", "330"),
    ("BNS/BNSS Terminology", "What is substituted performance of a contract?", "Specific Relief Act, 1963", "20"),
    ("BNS/BNSS Terminology", "Can police arrest someone for refusing to give their name and residence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "39"),
    ("BNS/BNSS Terminology", "What is the punishment for trespassing on burial places?", "Bharatiya Nyaya Sanhita, 2023", "301"),
    ("BNS/BNSS Terminology", "What is the punishment for giving false evidence?", "Bharatiya Nyaya Sanhita, 2023", "229"),

    ("Broad/Ambiguous", "What are my rights regarding insurance?", "Motor Vehicles Act, 1988", "151"),
    ("Broad/Ambiguous", "What happens if a Protection Officer commits an offence?", "Protection of Women from Domestic Violence Act, 2005", "34"),
    ("Broad/Ambiguous", "Can I get my property back?", "Karnataka Rent Act, 1999", "35"),
    ("Broad/Ambiguous", "Who has authority over cyber matters?", "Information Technology Act, 2000", "27"),
    ("Broad/Ambiguous", "What happens with public rights disputes?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "156"),
    ("Broad/Ambiguous", "What about reducing someone's sentence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "475"),
    ("Broad/Ambiguous", "What powers does the High Court have?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "528"),
    ("Broad/Ambiguous", "Can I get my money back from my landlord?", "Karnataka Rent Act, 1999", "15"),
    ("Broad/Ambiguous", "What happens to someone who isn't mentally well?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "378"),
    ("Broad/Ambiguous", "What about exchanging money?", "Transfer of Property Act, 1882", "121"),
    ("Broad/Ambiguous", "Can a court take away my rights to drive?", "Motor Vehicles Act, 1988", "20"),
    ("Broad/Ambiguous", "What about people being exploited?", "Bharatiya Nyaya Sanhita, 2023", "144"),
    ("Broad/Ambiguous", "What about bringing children from abroad?", "Bharatiya Nyaya Sanhita, 2023", "141"),
    ("Broad/Ambiguous", "What happens to profits from goods given to someone?", "Indian Contract Act, 1872", "163"),
    ("Broad/Ambiguous", "What are the rules about vehicle signals?", "Motor Vehicles Act, 1988", "121"),
    ("Broad/Ambiguous", "What if an agreement can't be done?", "Indian Contract Act, 1872", "56"),
    ("Broad/Ambiguous", "What happens if there's not enough evidence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "189"),
    ("Broad/Ambiguous", "What about helping someone commit a serious crime?", "Bharatiya Nyaya Sanhita, 2023", "55"),
    ("Broad/Ambiguous", "How do I get my property back?", "Specific Relief Act, 1963", "5"),
    ("Broad/Ambiguous", "What happens during a medical exam for a victim?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "184"),

    ("Specific Legal Concepts", "What is seizure or attachment of property?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "117"),
    ("Specific Legal Concepts", "What happens when a pledge is made by someone with only a limited interest?", "Indian Contract Act, 1872", "179"),
    ("Specific Legal Concepts", "What is a Claims Tribunal under the Motor Vehicles Act?", "Motor Vehicles Act, 1988", "165"),
    ("Specific Legal Concepts", "What is a contingent contract?", "Indian Contract Act, 1872", "31"),
    ("Specific Legal Concepts", "What are the liabilities of a mortgagee in possession?", "Transfer of Property Act, 1882", "76"),
    ("Specific Legal Concepts", "What are special provisions for infrastructure project contracts?", "Specific Relief Act, 1963", "20A"),
    ("Specific Legal Concepts", "How do I file an appeal under the RTI Act?", "Right to Information Act, 2005", "19"),
    ("Specific Legal Concepts", "What is tender of pardon to an accomplice?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "343"),
    ("Specific Legal Concepts", "What is unlawful compulsory labour?", "Bharatiya Nyaya Sanhita, 2023", "146"),
    ("Specific Legal Concepts", "What is the procedure when the accused is of unsound mind?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "367"),
    ("Specific Legal Concepts", "How do I apply for compensation after a motor vehicle accident?", "Motor Vehicles Act, 1988", "166"),
    ("Specific Legal Concepts", "What is a mercy petition in a death sentence case?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "472"),
    ("Specific Legal Concepts", "When does the right of private defence extend to causing harm other than death?", "Bharatiya Nyaya Sanhita, 2023", "42"),
    ("Specific Legal Concepts", "What is release on probation of good conduct?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "401"),
    ("Specific Legal Concepts", "What happens if consent is given under fear or misconception?", "Bharatiya Nyaya Sanhita, 2023", "28"),
    ("Specific Legal Concepts", "What is the right to inspection and production of documents?", "Transfer of Property Act, 1882", "60B"),
    ("Specific Legal Concepts", "What is subrogation in property law?", "Transfer of Property Act, 1882", "92"),
    ("Specific Legal Concepts", "What is the punishment for a public servant disobeying law to cause injury?", "Bharatiya Nyaya Sanhita, 2023", "198"),
    ("Specific Legal Concepts", "What constitutes organised crime?", "Bharatiya Nyaya Sanhita, 2023", "111"),
    ("Specific Legal Concepts", "What is the punishment for disturbing a religious assembly?", "Bharatiya Nyaya Sanhita, 2023", "300"),

    ("Natural-language", "Do court judgments have to be in a specific language?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "288"),
    ("Natural-language", "My tenant sublet the place without telling me, is there supposed to be a notice for that?", "Karnataka Rent Act, 1999", "33"),
    ("Natural-language", "My neighbor lied on some official form, can that get him in trouble?", "Bharatiya Nyaya Sanhita, 2023", "236"),
    ("Natural-language", "Where do I even go to complain about a store near me?", "Consumer Protection Act, 2019", "28"),
    ("Natural-language", "What if someone doesn't follow the court's evidence rules?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "509"),
    ("Natural-language", "Does my driving licence work everywhere in India?", "Motor Vehicles Act, 1988", "13"),
    ("Natural-language", "Can I get in trouble for parking in the wrong spot?", "Motor Vehicles Act, 1988", "117"),
    ("Natural-language", "When is someone actually allowed to get bail?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "478"),
    ("Natural-language", "Can the High Court just make up its own rules?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "523"),
    ("Natural-language", "What happens with empty plots of land under this rent law?", "Karnataka Rent Act, 1999", "40"),
    ("Natural-language", "So if there's a warrant out for me, what actually happens when they catch me?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "82"),
    ("Natural-language", "Once a judge decides my case, is that really the final word?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "295"),
    ("Natural-language", "Am I supposed to help the police if they ask?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "31"),
    ("Natural-language", "Can someone else handle my prosecution for me?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "339"),
    ("Natural-language", "Can I take my traffic case to a regular civil court?", "Motor Vehicles Act, 1988", "175"),
    ("Natural-language", "I got in an accident driving too fast, what am I looking at legally?", "Bharatiya Nyaya Sanhita, 2023", "281"),
    ("Natural-language", "What can the police actually search on me after they arrest me?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "49"),
    ("Natural-language", "What defences do I have if someone sues me over a contract?", "Specific Relief Act, 1963", "9"),
    ("Natural-language", "How does the prosecution actually present evidence in my case?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "254"),
    ("Natural-language", "What if I plead guilty but I'm not even there in court?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "276"),

    ("Case-law style", "A person was released by the court on condition that they sign a bond promising to appear when summoned. What section covers this power to require such a bond?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "91"),
    ("Case-law style", "When police arrest someone, is the officer required to tell them the general reason mentioned in the arrest warrant even if they don't have the actual paper on them?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "77"),
    ("Case-law style", "A transport company applied for a permit to legally operate trucks carrying goods between states. What governs the process for granting them this permit?", "Motor Vehicles Act, 1988", "79"),
    ("Case-law style", "During a criminal trial, must the witness testimony be given while the accused person is physically present in the courtroom?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "308"),
    ("Case-law style", "A lender delayed suing a borrower for a long time, but never let the guarantor off the hook. Is the guarantor still liable even though the lender waited?", "Indian Contract Act, 1872", "137"),
    ("Case-law style", "A magistrate finds the accused may be mentally unsound and unable to defend himself, but there is no strong case against him. What should the magistrate do?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "369"),
    ("Case-law style", "A company ran an advertisement making false claims about their product's benefits, misleading buyers. What punishment could they face?", "Consumer Protection Act, 2019", "89"),
    ("Case-law style", "Someone threatened to hurt a person to stop them from going to the police for help. What crime does that constitute?", "Bharatiya Nyaya Sanhita, 2023", "225"),
    ("Case-law style", "A consumer lost their case at a lower commission and wants to challenge that decision at a higher forum. What allows them to do that?", "Consumer Protection Act, 2019", "24"),
    ("Case-law style", "A person needs to swear an affidavit for their court case. In front of which authorities can this be legally done?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "333"),
    ("Case-law style", "In a fight, one person intentionally injured the other without any weapon involved. What offence would this fall under?", "Bharatiya Nyaya Sanhita, 2023", "115"),
    ("Case-law style", "A court ordered someone to maintain good behaviour for a set period as a security condition. From when does that period actually start counting?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "138"),
    ("Case-law style", "A driver was caught going faster than the posted limit on the highway. What governs speed restrictions for vehicles?", "Motor Vehicles Act, 1988", "112"),
    ("Case-law style", "After winning a case, can the court order the losing party to pay the legal costs incurred by the winning side?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "381"),
    ("Case-law style", "If someone lets an unlicensed person drive their car and that person breaks the law, is the vehicle owner also responsible?", "Motor Vehicles Act, 1988", "5"),
    ("Case-law style", "What qualifications must someone have to be appointed President of a District Consumer Commission?", "Consumer Protection Act, 2019", "29"),
    ("Case-law style", "Is it mandatory for vehicle owners to carry insurance that covers damage they might cause to other people?", "Motor Vehicles Act, 1988", "146"),
    ("Case-law style", "If someone fails to comply with a specific court-ordered obligation under section 154, what penalty applies?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "155"),
    ("Case-law style", "In a contract dispute, one party claims they didn't freely agree to the terms. What legally counts as free consent?", "Indian Contract Act, 1872", "14"),
    ("Case-law style", "A foreign company wants their digital certificates to be recognized as valid in India. What allows the Controller to recognize them?", "Information Technology Act, 2000", "19"),

    ("Multilingual-Hindi", "मकान मालिक मेरी जमा राशि वापस नहीं कर रहा है", "Karnataka Rent Act, 1999", "17"),
    ("Multilingual-Hindi", "बिना वारंट के गिरफ्तारी", "Bharatiya Nagarik Suraksha Sanhita, 2023", "35"),
    ("Multilingual-Hindi", "उपभोक्ता शिकायत कैसे दर्ज करें", "Consumer Protection Act, 2019", "35"),
    ("Multilingual-Kannada", "ಮನೆ ಮಾಲೀಕ ಠೇವಣಿ ಹಿಂತಿರುಗಿಸುತ್ತಿಲ್ಲ", "Karnataka Rent Act, 1999", "17"),
    ("Multilingual-Kannada", "ವಾರಂಟ್ ಇಲ್ಲದೆ ಬಂಧನ", "Bharatiya Nagarik Suraksha Sanhita, 2023", "35"),
    ("Multilingual-Hindi", "बाल विवाह के लिए अपहरण की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "87"),
    ("Multilingual-Kannada", "ನಕಲಿ ಕರೆನ್ಸಿ ನೋಟುಗಳಿಗೆ ಶಿಕ್ಷೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "178"),
    ("Multilingual-Kannada", "RTI ಅರ್ಜಿ ಹೇಗೆ ಸಲ್ಲಿಸುವುದು", "Right to Information Act, 2005", "6"),
    ("Multilingual-Hindi", "यदि मैं अदालत में उपस्थित नहीं होता तो क्या होगा", "Bharatiya Nagarik Suraksha Sanhita, 2023", "84"),
]

print(f"Total category queries compiled: {len(all_category_queries)}")

# ===== 1. Check independence: are any of these queries duplicates of training data? =====
print("\n" + "=" * 70)
print("1. INDEPENDENCE CHECK - overlap with training/tuning data")
print("=" * 70)

training_texts = set()
with open("../data/eval/eval_queries.json", "r", encoding="utf-8") as f:
    for q in json.load(f):
        training_texts.add(q["query"].strip().lower())

with open("../data/training_pairs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        training_texts.add(json.loads(line)["query"].strip().lower())

with open("../data/training_pairs_batch2.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        training_texts.add(json.loads(line)["query"].strip().lower())

overlaps = []
for cat, query, act, section in all_category_queries:
    from rag_core import translate_to_english
    q_to_check = query.strip().lower()
    if q_to_check in training_texts:
        overlaps.append((cat, query))

print(f"Training data sources checked: eval_queries.json (42), training_pairs.jsonl (446), training_pairs_batch2.jsonl (380)")
print(f"Exact text-match overlaps found: {len(overlaps)}")
for cat, q in overlaps:
    print(f"  - [{cat}] {q}")

# ===== 2. Category counts =====
print("\n" + "=" * 70)
print("2. CATEGORY DEFINITION CHECK - counts per category")
print("=" * 70)
from collections import Counter
cat_counts = Counter(cat for cat, q, a, s in all_category_queries)
for cat, count in cat_counts.items():
    print(f"  {cat}: {count}")

# ===== 3-6. Run every query, record hit/miss, compute exact Recall@5 =====
print("\n" + "=" * 70)
print("3-6. RUNNING ALL QUERIES - exact Recall@5 and per-query results")
print("=" * 70)

from rag_core import translate_to_english

results_log = []
total_hits = 0

for cat, query, expected_act, expected_section in all_category_queries:
    search_text = query
    if cat.startswith("Multilingual"):
        try:
            search_text = translate_to_english(query)
        except Exception:
            search_text = query

    results = engine.search(search_text, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        total_hits += 1
    results_log.append((cat, query, expected_act, expected_section, hit))

n = len(all_category_queries)
print(f"\nEXACT OVERALL Recall@5 across all {n} category queries: {total_hits}/{n} = {total_hits/n:.4f}")

# ===== 7. List all failures, grouped by category =====
print("\n" + "=" * 70)
print("7. ALL FAILURES, GROUPED BY CATEGORY")
print("=" * 70)

failures_by_cat = {}
for cat, query, act, section, hit in results_log:
    if not hit:
        failures_by_cat.setdefault(cat, []).append((query, act, section))

for cat, fails in failures_by_cat.items():
    print(f"\n[{cat}] - {len(fails)} failures:")
    for q, a, s in fails:
        print(f"  - \"{q}\" (expected: {a} S{s})")

# Save full results to CSV for records
import csv
with open("../data/eval/category_evaluation_full_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["category", "query", "expected_act", "expected_section", "hit"])
    for cat, query, act, section, hit in results_log:
        writer.writerow([cat, query, act, section, int(hit)])

print(f"\n\nFull results saved to data/eval/category_evaluation_full_results.csv")
