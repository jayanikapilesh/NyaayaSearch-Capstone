content = open("rag_core.py", encoding="utf-8").read()
old = """        temperature=0,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()"""
new = """        temperature=0,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("rag_core.py", "w", encoding="utf-8").write(content)
    print("Increased translate_to_english max_tokens from 200 to 500")
