from search_core import SearchEngine

engine = SearchEngine()
results = engine.search("My RTI request was rejected, can I appeal?", top_k=10)
for rank, r in enumerate(results, start=1):
    act = r["act_name"]
    section = r["section_number"]
    score = r["hybrid_score"]
    title = r["section_title"]
    print(f"{rank}. {act} Section {section} (score: {score:.3f}) - {title}")
