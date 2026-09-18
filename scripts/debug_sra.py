with open("data/processed/specific_relief_act_1963.txt", encoding="utf-8") as f:
    text = f.read()

positions = [j for j in range(len(text)) if text.startswith("Recovery of specific immovable property", j)]
print("Occurrences:", len(positions))
if len(positions) >= 1:
    last = positions[-1]
    print(repr(text[last-100:last+700]))
