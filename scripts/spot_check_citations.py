import pandas as pd

df = pd.read_csv("../data/case_law/processed/case_citations.csv")

sample = df.sample(n=20, random_state=42)

for i, row in sample.iterrows():
    print(f"Case: {row['title'][:80]}")
    print(f"  -> {row['act_name']}, Section {row['section_number']}")
    print()
