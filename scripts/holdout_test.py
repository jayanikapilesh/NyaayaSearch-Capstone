from search_core import SearchEngine

engine = SearchEngine()

holdout_queries = [
    ("Can I leave property to my grandchild who hasn't been born yet?", "Transfer of Property Act, 1882", "13"),
    ("Someone took my car without asking me, is that a crime?", "Motor Vehicles Act, 1988", "197"),
    ("The other person flat out refused to do their part of the deal, can I cancel the contract?", "Indian Contract Act, 1872", "39"),
    ("If my agent's authority ends, does that also end my sub-agent's authority?", "Indian Contract Act, 1872", "210"),
    ("Does my landlord have to give me notice before increasing my rent?", "Karnataka Rent Act, 1999", "10"),
    ("Police say my complaint is non-cognizable, what happens to my case now?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "174"),
    ("Someone physically blocked me from walking away, what crime is that?", "Bharatiya Nyaya Sanhita, 2023", "126"),
    ("There's an arrest warrant against me, what happens when the police come?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "82"),
    ("Can the government change traffic fine amounts after they're set?", "Motor Vehicles Act, 1988", "199B"),
    ("Is there a time limit to appeal to the IT Appellate Tribunal?", "Information Technology Act, 2000", "60"),
]

precisions, recalls, rrs = [], [], []

print(f"{'QUERY':<75} {'P@5':<6} {'R@5':<6} {'RR':<6}")
print("-" * 100)

for query, expected_act, expected_section in holdout_queries:
    results = engine.search(query, top_k=5)

    hits = 0
    first_hit_rank = None
    for rank, r in enumerate(results, start=1):
        if str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section:
            hits += 1
            if first_hit_rank is None:
                first_hit_rank = rank

    precision = hits / 5
    recall = hits / 1
    rr = 1 / first_hit_rank if first_hit_rank else 0

    precisions.append(precision)
    recalls.append(recall)
    rrs.append(rr)

    display_query = query if len(query) <= 73 else query[:70] + "..."
    print(f"{display_query:<75} {precision:<6.2f} {recall:<6.2f} {rr:<6.2f}")

print("-" * 100)
print(f"\nHELD-OUT SET (never tuned against): {len(holdout_queries)} queries")
print(f"Mean Precision@5: {sum(precisions)/len(precisions):.3f}")
print(f"Mean Recall@5: {sum(recalls)/len(recalls):.3f}")
print(f"Mean Reciprocal Rank (MRR): {sum(rrs)/len(rrs):.3f}")
