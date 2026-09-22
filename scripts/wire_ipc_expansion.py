content = open("search_core.py", encoding="utf-8").read()
old = "        expanded_query = expand_query(query)"
new = """        query = expand_ipc_references(query)
        expanded_query = expand_query(query)"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("search_core.py", "w", encoding="utf-8").write(content)
    print("Wired expand_ipc_references into search()")
