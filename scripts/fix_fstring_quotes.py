content = open("search_core.py", encoding="utf-8").read()
old = 'print(f"DEBUG: winning record = {self.records[top_idx].get(\\"act_name\\")} S{self.records[top_idx].get(\\"section_number\\")}")'
new = "print(f\"DEBUG: winning record = {self.records[top_idx].get('act_name')} S{self.records[top_idx].get('section_number')}\")"
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("search_core.py", "w", encoding="utf-8").write(content)
    print("Fixed f-string quoting")
