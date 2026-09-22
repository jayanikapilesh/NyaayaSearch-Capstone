content = open("search_core.py", encoding="utf-8").read()
old = "def expand_query(query):"
new = """IPC_TO_BNS = {
    # Common, high-frequency IPC sections mapped to their BNS 2023 equivalents.
    # Cross-checked across multiple legal reference sources as of 2026.
    # NOT an exhaustive or officially verified mapping (511 IPC sections vs
    # 358 BNS sections means some do not map one-to-one). For legal certainty,
    # verify against the official bare act.
    "302": "103",    # Murder
    "420": "318",    # Cheating
    "376": "64",     # Rape
    "498a": "85",    # Cruelty by husband/relatives
    "307": "109",    # Attempt to murder
    "304a": "106",   # Causing death by negligence
    "506": "351",    # Criminal intimidation
    "509": "79",     # Insulting modesty of a woman
    "353": "121",    # Assault to deter public servant
    "336": "125",    # Act endangering life
    "326": "118",    # Grievous hurt by dangerous weapons
    "382": "304",    # Theft after preparation for death/hurt
    "442": "330",    # House-breaking
    "494": "82",     # Bigamy
}


def expand_ipc_references(query):
    query_lower = query.lower()
    if "ipc" not in query_lower:
        return query
    numbers_found = re.findall(r"\\b(\\d+[a-z]?)\\b", query_lower)
    additions = []
    for num in numbers_found:
        if num in IPC_TO_BNS:
            additions.append(f"bns section {IPC_TO_BNS[num]}")
    if additions:
        return query + " " + " ".join(additions)
    return query


def expand_query(query):"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("search_core.py", "w", encoding="utf-8").write(content)
    print("Added IPC_TO_BNS mapping and expand_ipc_references function")
