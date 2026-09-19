import sys
from search_core import SearchEngine

engine = SearchEngine()

test_cases = [
    ("I bought a house but the seller doesn't actually own it, is the sale valid?", "Transfer of Property Act, 1882", "41"),
    ("The other party won't complete the property sale we agreed to, what can I do?", "Specific Relief Act, 1963", "10"),
    ("How do I stop someone from doing something harmful through a court order?", "Specific Relief Act, 1963", "36"),
]

for query, expected_act, expected_section in test_cases:
    print(f"\n=== {query} ===")
    print(f"Expecting: {expected_act}, Section {expected_section}")
    results = engine.search(query, top_k=50)

    found_rank = None
    for rank, r in enumerate(results, start=1):
        if str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section:
            found_rank = rank
            break

    if found_rank:
        print(f"FOUND at rank {found_rank}")
    else:
        print("NOT FOUND in top 50")

    print("Top 3 actual results:")
    for r in results[:3]:
        print(f"  - {r['act_name']} Section {r['section_number']} (score: {r['hybrid_score']:.3f})")
