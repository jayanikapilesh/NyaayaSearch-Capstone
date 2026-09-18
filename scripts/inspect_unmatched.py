import re
import pandas as pd
from bs4 import BeautifulSoup

df = pd.read_csv("../data/case_law/processed/Dataset2_Case_Law_Corpus_2015_2025.csv", nrows=500)

WORD = r"(?:[A-Z][a-z]+|of|the|and)"
PATTERN_ACT_SECTION = re.compile(rf"((?:{WORD}\s+){{1,6}}Act,?\s*\d{{4}})\s*-?\s*[:\-]?\s*s\.?\s*(\d+[A-Za-z]?(?:\(\w+\))?)")
PATTERN_US_OF = re.compile(rf"u[/l1]s\.?\s*(\d+[A-Za-z]?(?:\(\w+\))?)\s*of\s*(?:the\s*)?((?:{WORD}\s+){{1,6}}Act)")

unmatched_samples = []

for i in range(len(df)):
    html = df["raw_html"].iloc[i]
    if not isinstance(html, str):
        continue
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    if not PATTERN_ACT_SECTION.findall(text) and not PATTERN_US_OF.findall(text):
        unmatched_samples.append(text[-600:])

    if len(unmatched_samples) >= 8:
        break

for i, s in enumerate(unmatched_samples):
    print(f"--- UNMATCHED {i} ---")
    print(s)
    print()
