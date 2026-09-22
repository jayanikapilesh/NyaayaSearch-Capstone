import re
from search_core import expand_ipc_references, IPC_TO_BNS

query = "What is IPC 302?"
query = expand_ipc_references(query)
print(f"After expand_ipc_references: {query}")

query_lower = query.lower()
print(f"query_lower: {query_lower}")

ipc_target_section = None
if "ipc" in query_lower:
    print("'ipc' found in query_lower")
    numbers_found = re.findall(r"\b(\d+[a-z]?)\b", query_lower)
    print(f"numbers_found: {numbers_found}")
    for num in numbers_found:
        print(f"  checking '{num}' - in IPC_TO_BNS: {num in IPC_TO_BNS}")
        if num in IPC_TO_BNS:
            ipc_target_section = IPC_TO_BNS[num]
            print(f"  MATCH: setting ipc_target_section to {ipc_target_section}")
            break
else:
    print("'ipc' NOT found in query_lower")

print(f"\nFinal ipc_target_section: {ipc_target_section}")
