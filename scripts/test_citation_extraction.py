import re
import pandas as pd
from bs4 import BeautifulSoup

df = pd.read_csv("../data/case_law/processed/Dataset2_Case_Law_Corpus_2015_2025.csv", nrows=200)

# Title-case words (not ALL CAPS, which are judge names) plus connector words like "of", "the", "and"
WORD = r"(?:[A-Z][a-z]+|of|the|and)"
PATTERN_ACT_SECTION = re.compile(
    rf"((?:{WORD}\s+){{1,6}}Act,?\s*\d{{4}})\s*-?\s*[:\-]?\s*s\.?\s*(\d+[A-Za-z]?(?:\(\w+\))?)",
)

PATTERN_US_OF = re.compile(
    rf"u[/l1]s\.?\s*(\d+[A-Za-z]?(?:\(\w+\))?)\s*of\s*(?:the\s*)?((?:{WORD}\s+){{1,6}}Act)",
)

matches_found = 0
examples = []

for i in range(len(df)):
    html = df["raw_html"].iloc[i]
    if not isinstance(html, str):
        continue
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    found_1 = PATTERN_ACT_SECTION.findall(text)
    found_2 = PATTERN_US_OF.findall(text)

    if found_1 or found_2:
        matches_found += 1
        examples.append({
            "case_id": df["case_id"].iloc[i],
            "pattern1": found_1,
            "pattern2": found_2,
        })

print(f"Matched {matches_found} out of {len(df)} cases")
print()
for ex in examples[:15]:
    print(ex)
