import sys
sys.path.insert(0, ".")
from search_core import SearchEngine

engine = SearchEngine()

test_cases = [
    ("seller doesn't own the house", "Transfer of Property Act", "41"),
    ("minor valid contract", "Indian Contract Act", "11"),
    ("hacked computer stole data", "Information Technology Act", "43"),
    ("driving licence suspended appeal", "Motor Vehicles Act", "17"),
    ("property sale won't complete", "Specific Relief Act", "10"),
]

for query, expected_act, expected_section in test_cases:
    print(f"\n=== QUERY: {query} ===")
    print(f"Expected: {expected_act}, Section {expected_section}")

    results = engine.search(query, top_k=100)

    found_rank = None
    for rank, r in enumerate(results, start=1):
        if expected_act.lower() in str(r["act_name"]).lower() and str(r["section_number"]) == expected_section:
            found_rank = rank
            break

    if found_rank:
        print(f"FOUND at rank {found_rank}")
    else:
        print("NOT FOUND in top 100")

    print("Top 3 actual results:")
    for r in results[:3]:
        print(f"  - {r['act_name']} Section {r['section_number']} (score: {r['hybrid_score']:.3f})")
