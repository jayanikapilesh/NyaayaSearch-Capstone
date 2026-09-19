from search_core import SearchEngine

engine = SearchEngine()
results = engine.search("My driving licence was suspended, can I appeal?", top_k=20)

for rank, r in enumerate(results, start=1):
    marker = " <-- EXPECTED" if r["act_name"] == "Motor Vehicles Act, 1988" and str(r["section_number"]) == "17" else ""
    print(f"{rank}. {r['act_name']} Section {r['section_number']} (score: {r['hybrid_score']:.3f}) - {r['section_title']}{marker}")
