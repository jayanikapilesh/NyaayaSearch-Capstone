from search_core import SearchEngine

engine = SearchEngine()

holdout_queries_2 = [
    ("When does an agent's authority to act for someone officially end?", "Indian Contract Act, 1872", "201"),
    ("What happens if I drive without a proper licence?", "Motor Vehicles Act, 1988", "181"),
    ("Is it a crime to give police false information to get someone else in trouble?", "Bharatiya Nyaya Sanhita, 2023", "217"),
    ("What's the difference between a temporary and a permanent court injunction?", "Specific Relief Act, 1963", "37"),
    ("Can I get in trouble for parking my car somewhere unsafe?", "Motor Vehicles Act, 1988", "122"),
    ("What's the punishment for kidnapping someone for ransom?", "Bharatiya Nyaya Sanhita, 2023", "140"),
    ("If I settle my consumer complaint, does the commission record that officially?", "Consumer Protection Act, 2019", "81"),
    ("Can a court order my abuser to stay away from me?", "Protection of Women from Domestic Violence Act, 2005", "18"),
    ("Can police search me after they arrest me?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "49"),
    ("Is it a crime to convince a soldier to disobey orders?", "Bharatiya Nyaya Sanhita, 2023", "159"),
]

precisions, recalls, rrs = [], [], []

print(f"{'QUERY':<75} {'P@5':<6} {'R@5':<6} {'RR':<6}")
print("-" * 100)

for query, expected_act, expected_section in holdout_queries_2:
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
print(f"\nHELD-OUT SET 2 (never tuned against): {len(holdout_queries_2)} queries")
print(f"Mean Precision@5: {sum(precisions)/len(precisions):.3f}")
print(f"Mean Recall@5: {sum(recalls)/len(recalls):.3f}")
print(f"Mean Reciprocal Rank (MRR): {sum(rrs)/len(rrs):.3f}")
