import re

files = {
    "Motor Vehicles Act, 1988": "data/processed/motor_vehicles_act_1988.txt",
    "Transfer of Property Act, 1882": "data/processed/transfer_of_property_act_1882.txt",
    "Bharatiya Nyaya Sanhita, 2023": "data/processed/bharatiya_nyaya_sanhita_2023.txt",
    "Bharatiya Nagarik Suraksha Sanhita, 2023": "data/processed/bharatiya_nagarik_suraksha_sanhita_2023.txt",
    "Protection of Women from Domestic Violence Act, 2005": "data/processed/domestic_violence_act_2005.txt",
}

for name, path in files.items():
    with open(path, encoding="utf-8") as f:
        text = f.read()
    print("=====", name, "=====")
    print("File length:", len(text))
    # find first 3 occurrences of "1. " followed by capital letter, to see numbering pattern
    matches = [m.start() for m in re.finditer(r"\n1\.\s+[A-Z]", text)][:3]
    for m in matches:
        print(repr(text[m:m+120]))
    print()
