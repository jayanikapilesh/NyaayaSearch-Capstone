import numpy as np
import pandas as pd
from search_core import SearchEngine, expand_query, tokenize


class AuditableSearchEngine(SearchEngine):
    def search_with_disabled_rules(self, query, disabled_rules, top_k=5):
        expanded_query = expand_query(query)
        query_tokens = tokenize(expanded_query)

        bm25_scores = np.array(self.bm25.get_scores(query_tokens), dtype=float)
        if bm25_scores.max() > 0:
            bm25_scores = bm25_scores / bm25_scores.max()

        query_embedding = self.model.encode([expanded_query], normalize_embeddings=True)[0]
        semantic_scores = np.dot(self.embeddings, query_embedding)
        semantic_scores = np.clip(semantic_scores, 0, 1)

        boost = np.ones(len(self.records))
        query_lower = query.lower()

        for i, record in enumerate(self.records):
            title = str(record.get("section_title") or "").lower()
            legal_text = str(record.get("legal_text") or "").lower()
            act_name = str(record.get("act_name") or "").lower()
            section_number = str(record.get("section_number") or "")
            combined = title + " " + legal_text + " " + act_name

            if "landlord" not in disabled_rules:
                if "landlord" in query_lower and "landlord" in combined:
                    boost[i] *= 1.25
            if "tenant" not in disabled_rules:
                if "tenant" in query_lower and "tenant" in combined:
                    boost[i] *= 1.25
            if "security_deposit" not in disabled_rules:
                if "security deposit" in query_lower:
                    if "security" in combined and "deposit" in combined:
                        boost[i] *= 1.5
            if "return_refund" not in disabled_rules:
                if "return" in query_lower or "refund" in query_lower:
                    if any(word in combined for word in ["return", "refund", "repay"]):
                        boost[i] *= 1.2
            if "minor_contract" not in disabled_rules:
                if "minor" in query_lower and "contract" in query_lower:
                    if "contract act" in act_name and ("minor" in combined or "competent" in combined or "age of majority" in combined):
                        boost[i] *= 2.0
            if "hacking" not in disabled_rules:
                if ("hacked" in query_lower or "stole data" in query_lower or "hacking" in query_lower):
                    if "information technology" in act_name and (
                        "unauthorised access" in combined or "unauthorized access" in combined
                        or "damage to computer" in combined or "data" in combined and "steal" in combined
                    ):
                        boost[i] *= 2.0
            if "driving_licence" not in disabled_rules:
                if "driving" in query_lower and "licence" in query_lower:
                    if "motor vehicles act" in act_name:
                        boost[i] *= 2.0
                    elif "information technology" in act_name:
                        boost[i] *= 0.3
            if "driving_licence_appeal" not in disabled_rules:
                if "driving" in query_lower and "licence" in query_lower and "appeal" in query_lower:
                    if "motor vehicles act" in act_name and "appeal" in combined:
                        boost[i] *= 3.0
            if "rti" not in disabled_rules:
                if "rti" in query_lower or "right to information" in query_lower:
                    if "right to information act" in act_name:
                        boost[i] *= 2.0
            if "specific_performance" not in disabled_rules:
                if "won't complete" in query_lower or "specific performance" in expanded_query:
                    if "specific relief act" in act_name and "specific performance" in combined:
                        boost[i] *= 2.5
                        if section_number == "10":
                            boost[i] *= 2.0
            if "ostensible_owner" not in disabled_rules:
                if "doesn't own" in query_lower or "doesn't actually own" in query_lower:
                    if "transfer of property act" in act_name and "ostensible owner" in combined:
                        boost[i] *= 3.0
                    elif "transfer of property act" in act_name:
                        boost[i] *= 0.7
            if "injunction" not in disabled_rules:
                if "stop someone" in query_lower or ("stop" in query_lower and "harmful" in query_lower):
                    if "specific relief act" in act_name and "injunction" in combined:
                        boost[i] *= 2.5

        final_scores = (0.15 * bm25_scores) + (0.85 * semantic_scores)

        if "landlord_tenant_broad" not in disabled_rules:
            if "landlord" in query_lower or "tenant" in query_lower:
                for i, record in enumerate(self.records):
                    text = (
                        str(record.get("section_title") or "") + " " +
                        str(record.get("legal_text") or "")
                    ).lower()
                    if any(word in text for word in [
                        "tenant", "landlord", "lessee", "lessor", "rent", "lease", "tenancy"
                    ]):
                        final_scores[i] *= 1.5
                    if "security deposit" in query_lower:
                        if "deposit" not in text:
                            final_scores[i] *= 0.3

        final_scores = final_scores * boost

        top_indices = np.argsort(final_scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            r = self.records[idx]
            results.append({
                "act_name": r.get("act_name"),
                "section_number": r.get("section_number"),
            })
        return results


def run_recall5(engine, queries, disabled_rules):
    hits = 0
    for query, expected_act, expected_section in queries:
        results = engine.search_with_disabled_rules(query, disabled_rules, top_k=5)
        hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
        if hit:
            hits += 1
    return hits / len(queries)


if __name__ == "__main__":
    print("Loading 148-query frozen set...")
    df = pd.read_csv("../data/eval/category_evaluation_full_results.csv")
    queries = list(zip(df["query"], df["expected_act"], df["expected_section"].astype(str)))
    print(f"Loaded {len(queries)} queries")

    print("Loading search engine...")
    engine = AuditableSearchEngine()

    all_rules = [
        "landlord", "tenant", "security_deposit", "return_refund",
        "minor_contract", "hacking", "driving_licence", "driving_licence_appeal",
        "rti", "specific_performance", "ostensible_owner", "injunction",
        "landlord_tenant_broad",
    ]

    print("\nBaseline (all rules ON)...")
    baseline = run_recall5(engine, queries, disabled_rules=set())
    print(f"Baseline Recall@5: {baseline:.4f}")

    print("\nTesting each rule OFF individually...")
    results = {}
    for rule in all_rules:
        recall = run_recall5(engine, queries, disabled_rules={rule})
        delta = recall - baseline
        results[rule] = (recall, delta)
        print(f"  {rule:<25} Recall@5={recall:.4f}  delta={delta:+.4f}")

    print("\n" + "=" * 60)
    print("SUMMARY (sorted by impact)")
    print("=" * 60)
    for rule, (recall, delta) in sorted(results.items(), key=lambda x: x[1][1]):
        sign = "HURTS to remove (rule helps)" if delta < 0 else ("HELPS to remove (rule hurts)" if delta > 0 else "no effect")
        print(f"  {rule:<25} delta={delta:+.4f}  ({sign})")
