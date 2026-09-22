content = open("search_core.py", encoding="utf-8").read()
old = '            combined = title + " " + legal_text + " " + act_name'
new = '''            combined = title + " " + legal_text + " " + act_name

            if ipc_target_section is not None:
                if "bharatiya nyaya sanhita" in act_name and section_number == ipc_target_section:
                    boost[i] *= 5.0'''
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("search_core.py", "w", encoding="utf-8").write(content)
    print("Added direct boost for resolved IPC target section")
