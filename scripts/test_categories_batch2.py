from search_core import SearchEngine

engine = SearchEngine()

bns_terminology = [
    ("What is the punishment for bribery?", "Bharatiya Nyaya Sanhita, 2023", "173"),
    ("How are contracts contingent on an event happening enforced?", "Indian Contract Act, 1872", "32"),
    ("What is an oral transfer of property?", "Transfer of Property Act, 1882", "9"),
    ("Do intermediaries have to preserve and retain information?", "Information Technology Act, 2000", "67C"),
    ("What is a contract of guarantee?", "Indian Contract Act, 1872", "126"),
    ("Can the licensing authority disqualify someone from holding a licence?", "Motor Vehicles Act, 1988", "34"),
    ("How is a transfer of actionable claim executed?", "Transfer of Property Act, 1882", "130"),
    ("What is dishonest misappropriation of property possessed by a deceased person?", "Bharatiya Nyaya Sanhita, 2023", "315"),
    ("What is the jurisdiction under the Domestic Violence Act?", "Protection of Women from Domestic Violence Act, 2005", "27"),
    ("What happens with sentencing for an offender already sentenced for another offence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "467"),
    ("What is a mortgagor's right of redemption?", "Transfer of Property Act, 1882", "60"),
    ("What is the punishment for counterfeiting currency notes?", "Bharatiya Nyaya Sanhita, 2023", "178"),
    ("What is the punishment for attempting suicide to compel exercise of lawful power?", "Bharatiya Nyaya Sanhita, 2023", "226"),
    ("What is a continuing offence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "518"),
    ("What happens upon conviction on a plea of guilty?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "252"),
    ("What is house-trespass and house-breaking?", "Bharatiya Nyaya Sanhita, 2023", "330"),
    ("What is substituted performance of a contract?", "Specific Relief Act, 1963", "20"),
    ("Can police arrest someone for refusing to give their name and residence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "39"),
    ("What is the punishment for trespassing on burial places?", "Bharatiya Nyaya Sanhita, 2023", "301"),
    ("What is the punishment for giving false evidence?", "Bharatiya Nyaya Sanhita, 2023", "229"),
]

broad_ambiguous = [
    ("What are my rights regarding insurance?", "Motor Vehicles Act, 1988", "151"),
    ("What happens if a Protection Officer commits an offence?", "Protection of Women from Domestic Violence Act, 2005", "34"),
    ("Can I get my property back?", "Karnataka Rent Act, 1999", "35"),
    ("Who has authority over cyber matters?", "Information Technology Act, 2000", "27"),
    ("What happens with public rights disputes?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "156"),
    ("What about reducing someone's sentence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "475"),
    ("What powers does the High Court have?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "528"),
    ("Can I get my money back from my landlord?", "Karnataka Rent Act, 1999", "15"),
    ("What happens to someone who isn't mentally well?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "378"),
    ("What about exchanging money?", "Transfer of Property Act, 1882", "121"),
    ("Can a court take away my rights to drive?", "Motor Vehicles Act, 1988", "20"),
    ("What about people being exploited?", "Bharatiya Nyaya Sanhita, 2023", "144"),
    ("What about bringing children from abroad?", "Bharatiya Nyaya Sanhita, 2023", "141"),
    ("What happens to profits from goods given to someone?", "Indian Contract Act, 1872", "163"),
    ("What are the rules about vehicle signals?", "Motor Vehicles Act, 1988", "121"),
    ("What if an agreement can't be done?", "Indian Contract Act, 1872", "56"),
    ("What happens if there's not enough evidence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "189"),
    ("What about helping someone commit a serious crime?", "Bharatiya Nyaya Sanhita, 2023", "55"),
    ("How do I get my property back?", "Specific Relief Act, 1963", "5"),
    ("What happens during a medical exam for a victim?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "184"),
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
h1, n1 = run_category("BNS/BNSS Terminology", bns_terminology)
h2, n2 = run_category("Broad/Ambiguous", broad_ambiguous)
print("=" * 60)
print(f"\nCombined category batch 2: {h1+h2}/{n1+n2} = {(h1+h2)/(n1+n2):.3f}")
