import pandas as pd
from bs4 import BeautifulSoup

df = pd.read_csv("../data/case_law/processed/Dataset2_Case_Law_Corpus_2015_2025.csv")
sample = df.sample(n=30, random_state=7)

for i, row in sample.iterrows():
    soup = BeautifulSoup(row["raw_html"], "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    print(f"\n=== case_id: {row['case_id']} ===")
    print(text[-500:])
