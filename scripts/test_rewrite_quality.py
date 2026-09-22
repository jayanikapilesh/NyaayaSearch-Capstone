from rag_core import rewrite_query_for_search

test_queries = [
    "What's the punishment for seriously injuring someone on purpose?",
    "What's the punishment for reckless driving?",
    "How does the court officially deliver a summons?",
    "What does it mean for a court to take cognizance of a crime?",
    "Can I get my mortgaged property back after paying off the loan?",
    "What happens if I can't pay a fine - do I go to jail instead?",
]

for q in test_queries:
    rewritten = rewrite_query_for_search(q)
    print(f"Original:  {q}")
    print(f"Rewritten: {rewritten}")
    print()
