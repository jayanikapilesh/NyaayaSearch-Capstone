content = open("search_core.py", encoding="utf-8").read()
old = """            if ipc_target_section is not None:
                if "bharatiya nyaya sanhita" in act_name and section_number == ipc_target_section:
                    boost[i] *= 5.0"""
new = """            if ipc_target_section is not None:
                if "bharatiya nyaya sanhita" in act_name and section_number == ipc_target_section:
                    boost[i] *= 50.0"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("search_core.py", "w", encoding="utf-8").write(content)
    print("Increased boost multiplier to 50x")
