content = open("main.py", encoding="utf-8").read()

old_imports = "from search_core import SearchEngine"
new_imports = "import re\nfrom search_core import SearchEngine, IPC_TO_BNS"
count1 = content.count(old_imports)
print(f"Import fix: found {count1}")
if count1 == 1:
    content = content.replace(old_imports, new_imports)

old_call = "        explanation = generate_explanation(request.query, results)"
new_call = """        explanation_query = request.query
        query_lower_check = explanation_query.lower()
        if "ipc" in query_lower_check:
            numbers_found = re.findall(r"\\b(\\d+[a-z]?)\\b", query_lower_check)
            for num in numbers_found:
                if num in IPC_TO_BNS:
                    explanation_query += f" (Note: IPC Section {num} corresponds to BNS Section {IPC_TO_BNS[num]} under the current law - please explain using the BNS section shown in the results below.)"
                    break
        explanation = generate_explanation(explanation_query, results)"""
count2 = content.count(old_call)
print(f"Call fix: found {count2}")
if count2 == 1:
    content = content.replace(old_call, new_call)

open("main.py", "w", encoding="utf-8").write(content)
print("Done")
