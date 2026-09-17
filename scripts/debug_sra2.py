with open("data/processed/specific_relief_act_1963.txt", encoding="utf-8") as f:
    text = f.read()

positions = [j for j in range(len(text)) if text.startswith("Short title, extent and commencement", j)]
print("Occurrences of real Section 1 title:", len(positions))
for p in positions:
    print("---")
    print(repr(text[p-30:p+150]))
