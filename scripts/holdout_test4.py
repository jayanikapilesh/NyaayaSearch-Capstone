from search_core import SearchEngine

engine = SearchEngine()

holdout_queries_4 = [
    ("Where can I file a big consumer complaint at the national level?", "Consumer Protection Act, 2019", "53"),
    ("Is it a crime to hide that you know someone plans to commit a serious crime?", "Bharatiya Nyaya Sanhita, 2023", "58"),
    ("Can the government take action against misleading advertisements?", "Consumer Protection Act, 2019", "21"),
    ("Can I question witnesses in my own court case?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "322"),
    ("Can I file a defamation case against someone?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "222"),
    ("Can I get information about a third party through an RTI request?", "Right to Information Act, 2005", "11"),
    ("Is it illegal to resist arrest?", "Bharatiya Nyaya Sanhita, 2023", "265"),
    ("What is a continuing offence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "518"),
    ("Can I be protected if I help someone in an emergency without their consent?", "Bharatiya Nyaya Sanhita, 2023", "30"),
    ("What makes an electronic signature legally secure?", "Information Technology Act, 2000", "15"),
]

precisions, recalls, rrs = [], [], []

print(f"{'QUERY':<75} {'P@5':<6} {'R@5':<6} {'RR':<6}")
print("-" * 100)

for query, expected_act, expected_section in holdout_queries_4:
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
print(f"\nHELD-OUT SET 4 (post synonym-expansion, genuinely fresh): {len(holdout_queries_4)} queries")
print(f"Mean Precision@5: {sum(precisions)/len(precisions):.3f}")
print(f"Mean Recall@5: {sum(recalls)/len(recalls):.3f}")
print(f"Mean Reciprocal Rank (MRR): {sum(rrs)/len(rrs):.3f}")
