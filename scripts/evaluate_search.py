import json
import os
from search_core import SearchEngine

EVAL_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "eval", "eval_queries.json")


def evaluate():
    engine = SearchEngine()

    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        eval_queries = json.load(f)

    precisions = []
    recalls = []
    reciprocal_ranks = []

    print(f"{'QUERY':<70} {'P@5':<6} {'R@5':<6} {'RR':<6}")
    print("-" * 97)

    for item in eval_queries:
        query = item["query"]
        expected_act = item["act_name"].lower()
        expected_sections = {str(s) for s in item["expected_sections"]}

        results = engine.search(query, top_k=5)

        hits = 0
        first_hit_rank = None
        for rank, r in enumerate(results, start=1):
            act_matches = str(r["act_name"]).lower() == expected_act
            section_matches = str(r["section_number"]) in expected_sections
            if act_matches and section_matches:
                hits += 1
                if first_hit_rank is None:
                    first_hit_rank = rank

        precision = hits / 5
        recall = min(hits, len(expected_sections)) / len(expected_sections) if expected_sections else 0
        rr = 1 / first_hit_rank if first_hit_rank else 0

        precisions.append(precision)
        recalls.append(recall)
        reciprocal_ranks.append(rr)

        display_query = query if len(query) <= 68 else query[:65] + "..."
        print(f"{display_query:<70} {precision:<6.2f} {recall:<6.2f} {rr:<6.2f}")

    print("-" * 97)
    print(f"\nTotal queries evaluated: {len(eval_queries)}")
    print(f"Mean Precision@5: {sum(precisions)/len(precisions):.3f}")
    print(f"Mean Recall@5: {sum(recalls)/len(recalls):.3f}")
    print(f"Mean Reciprocal Rank (MRR): {sum(reciprocal_ranks)/len(reciprocal_ranks):.3f}")


if __name__ == "__main__":
    evaluate()
