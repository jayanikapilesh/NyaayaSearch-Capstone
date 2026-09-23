from search_core import SearchEngine

engine = SearchEngine()

query = "Can my driver's license be revoked if I am convicted of a crime?"
results = engine.search(query, top_k=5)
print(f"Query: {query}")
print("Top 5 results:")
for r in results:
    print(f"  {r['act_name']} S{r['section_number']} (score: {r['hybrid_score']:.3f})")
