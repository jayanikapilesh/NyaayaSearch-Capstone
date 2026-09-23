import re
import pandas as pd
from bs4 import BeautifulSoup
import sys
sys.path.insert(0, ".")
from extract_citations import extract_citations

INPUT_FILE = "../data/case_law/processed/Dataset2_Case_Law_Corpus_2015_2025.csv"
df = pd.read_csv(INPUT_FILE)

sample = df.sample(n=400, random_state=222333)

unmatched_examples = []

for i, row in sample.iterrows():
    html = row["raw_html"]
    if not isinstance(html, str):
        continue
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    citations = extract_citations(text)
    if not citations:
        matches = re.findall(r".{50}(?:Act|Code)[,.]?\s*\d{0,4}.{50}", text)
        if matches and len(unmatched_examples) < 25:
            unmatched_examples.append(matches[0])

print(f"Sample size: 400")
print(f"Found {len(unmatched_examples)} example snippets from unmatched cases:\n")
for ex in unmatched_examples:
    print(f"  ...{ex}...\n")
