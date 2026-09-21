content = open("main.py", encoding="utf-8").read()
old = """    try:
        explanation = generate_explanation(request.query, results)
    except groq.RateLimitError:"""
new = """    try:
        explanation = generate_explanation(request.query, results)
        is_valid, unverified_sections = verify_citations(explanation, results)
        if not is_valid:
            explanation += "\\n\\n[Note: this explanation may reference a section number not confirmed in our search results (" + ", ".join(unverified_sections) + "). Please cross-check with the original statutory text shown above.]"
    except groq.RateLimitError:"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("main.py", "w", encoding="utf-8").write(content)
    print("Added citation verification call")
