import sys
from search_core import SearchEngine

engine = SearchEngine()

draft_queries = [
    ("I lost my consumer case at the District Commission, can I appeal?", "Consumer Protection Act, 2019", "24"),
    ("My digital signature certificate was revoked, will I be notified?", "Information Technology Act, 2000", "39"),
    ("Can an RTI officer be punished for releasing information in good faith?", "Right to Information Act, 2005", "21"),
    ("How is the amount of rent payable decided under the Rent Act?", "Karnataka Rent Act, 1999", "6"),
    ("Someone took over my property without my consent, what can I do?", "Specific Relief Act, 1963", "6"),
    ("Do I have to give information about my vehicle if the police ask?", "Motor Vehicles Act, 1988", "133"),
    ("Someone is selling fake branded goods with a counterfeit mark, is that a crime?", "Bharatiya Nyaya Sanhita, 2023", "349"),
    ("Can police ask a repeat offender to give a bond for good behaviour?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "129"),
    ("Can a domestic violence victim get monetary compensation for injuries?", "Protection of Women from Domestic Violence Act, 2005", "22"),
]

for query, expected_act, expected_section in draft_queries:
    print(f"\n=== {query} ===")
    print(f"Expecting: {expected_act}, Section {expected_section}")
    results = engine.search(query, top_k=100)

    found_rank = None
    for rank, r in enumerate(results, start=1):
        if str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section:
            found_rank = rank
            break

    if found_rank:
        status = "GOOD (top 5)" if found_rank <= 5 else f"WEAK (rank {found_rank})"
        print(f"Result: FOUND at rank {found_rank} - {status}")
    else:
        print("Result: NOT FOUND in top 100 - query or expected section may be wrong")

    print("Actual top 3:")
    for r in results[:3]:
        print(f"  - {r['act_name']} Section {r['section_number']}: {r['section_title']}")
