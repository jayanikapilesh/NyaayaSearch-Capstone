from search_core import SearchEngine

engine = SearchEngine()

test_queries = [
    ("What is IPC 302?", "Bharatiya Nyaya Sanhita, 2023", "103"),
    ("What does IPC section 420 say about cheating?", "Bharatiya Nyaya Sanhita, 2023", "318"),
    ("Explain IPC 376", "Bharatiya Nyaya Sanhita, 2023", "64"),
    ("What is section 498A IPC?", "Bharatiya Nyaya Sanhita, 2023", "85"),
    ("What is IPC 307 about?", "Bharatiya Nyaya Sanhita, 2023", "109"),
]

hits = 0
for query, expected_act, expected_section in test_queries:
    results = engine.search(query, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    status = "PASS" if hit else "FAIL"
    if hit:
        hits += 1
    if results:
        top_act = results[0]["act_name"]
        top_section = results[0]["section_number"]
        top_result = f"{top_act} S{top_section}"
    else:
        top_result = "no results"
    print(f"{status} | {query} -> top result: {top_result}")

print(f"\n{hits}/{len(test_queries)} IPC-referencing queries correctly resolved to BNS")
