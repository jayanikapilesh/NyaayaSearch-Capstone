import re
import pandas as pd
from bs4 import BeautifulSoup
import sys
sys.path.insert(0, ".")
from extract_citations import extract_citations

INPUT_FILE = "../data/case_law/processed/Dataset2_Case_Law_Corpus_2015_2025.csv"
df = pd.read_csv(INPUT_FILE)

sample = df.sample(n=300, random_state=42)

unmatched_with_section_word = 0
unmatched_total = 0
example_texts = []

for i, row in sample.iterrows():
    html = row["raw_html"]
    if not isinstance(html, str):
        continue
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    citations = extract_citations(text)
    if not citations:
        unmatched_total += 1
        if re.search(r"\bSection\s+\d+", text):
            unmatched_with_section_word += 1
            if len(example_texts) < 3:
                match = re.search(r".{40}Section\s+\d+[A-Za-z]?.{60}", text)
                if match:
                    example_texts.append(match.group())

print(f"Sample size: 300 cases")
print(f"Currently unmatched: {unmatched_total}")
print(f"Of those, contain spelled-out 'Section N': {unmatched_with_section_word}")
print(f"\nExample missed text snippets:")
for ex in example_texts:
    print(f"  ...{ex}...")
