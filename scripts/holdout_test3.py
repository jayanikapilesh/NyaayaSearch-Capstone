from search_core import SearchEngine

engine = SearchEngine()

holdout_queries_3 = [
    ("Who appoints the Chief Information Commissioner?", "Right to Information Act, 2005", "12"),
    ("Can I appeal a decision made under the Motor Vehicles Act?", "Motor Vehicles Act, 1988", "89"),
    ("Can a boss be punished for sexual relations with an employee by misusing his position?", "Bharatiya Nyaya Sanhita, 2023", "68"),
    ("What's the punishment for kidnapping a woman to force her into marriage?", "Bharatiya Nyaya Sanhita, 2023", "87"),
    ("What types of criminal courts exist in India?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "6"),
    ("Can the High Court review a lower court's decision?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "442"),
    ("Which police officer rank can investigate cyber crimes?", "Information Technology Act, 2000", "78"),
    ("What happens if I break my bail bond?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "491"),
    ("Who is legally allowed to act as an agent in a contract?", "Indian Contract Act, 1872", "184"),
    ("What happens if I don't show up in court after being released on bail?", "Bharatiya Nyaya Sanhita, 2023", "269"),
    ("What's the punishment for robbery where the robber tries to kill someone?", "Bharatiya Nyaya Sanhita, 2023", "311"),
    ("What's the punishment for making fake currency notes?", "Bharatiya Nyaya Sanhita, 2023", "178"),
    ("Can one co-owner sell their share of jointly owned property?", "Transfer of Property Act, 1882", "47"),
    ("Is it a crime to not report information to police when legally required to?", "Bharatiya Nyaya Sanhita, 2023", "211"),
    ("Can I use force to defend myself even if it risks hurting an innocent bystander?", "Bharatiya Nyaya Sanhita, 2023", "44"),
    ("What happens if I plead guilty in court?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "264"),
    ("Is it a crime to give false information about a crime to the police?", "Bharatiya Nyaya Sanhita, 2023", "240"),
    ("Is singing an obscene song in public illegal?", "Bharatiya Nyaya Sanhita, 2023", "296"),
    ("Can the accused testify as a witness in their own trial?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "353"),
    ("What's the punishment for lying to get a digital certificate?", "Information Technology Act, 2000", "71"),
    ("What is a charge on property under property law?", "Transfer of Property Act, 1882", "100"),
    ("Can a magistrate order me to give a handwriting sample?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "349"),
    ("Can police sell seized perishable goods before the trial ends?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "505"),
    ("What happens if someone doesn't show up after a court order to appear?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "84"),
    ("How long is an arrest warrant valid?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "72"),
]

precisions, recalls, rrs = [], [], []

print(f"{'QUERY':<75} {'P@5':<6} {'R@5':<6} {'RR':<6}")
print("-" * 100)

for query, expected_act, expected_section in holdout_queries_3:
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
print(f"\nHELD-OUT SET 3 (never tuned against): {len(holdout_queries_3)} queries")
print(f"Mean Precision@5: {sum(precisions)/len(precisions):.3f}")
print(f"Mean Recall@5: {sum(recalls)/len(recalls):.3f}")
print(f"Mean Reciprocal Rank (MRR): {sum(rrs)/len(rrs):.3f}")
