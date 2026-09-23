content = open("search_core.py", encoding="utf-8").read()
old = '    "physically bring my vehicle": ["physically bring my vehicle", "production of vehicle"],'
new = '''    "physically bring my vehicle": ["physically bring my vehicle", "production of vehicle"],
    "bus route permit": ["bus route permit", "stage carriage permit"],
    "damage using fire": ["damage using fire", "mischief by fire"],
    "child not yet born": ["child not yet born", "unborn person", "vested interest"],
    "repay expenses": ["repay expenses", "bailor necessary expenses"],
    "taking care of their item": ["taking care of their item", "bailee"],
    "very minor harm": ["very minor harm", "slight harm"],'''
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("search_core.py", "w", encoding="utf-8").write(content)
    print("Added 6 new targeted entries")
