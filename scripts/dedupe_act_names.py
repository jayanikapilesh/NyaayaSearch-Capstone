import pandas as pd

df = pd.read_csv("../data/case_law/processed/case_citations.csv")

before = len(df[df["act_name_normalized"] == "Indian Penal Code"])
df.loc[df["act_name_normalized"] == "Indian Penal Code", "act_name_normalized"] = "Penal Code"

df.to_csv("../data/case_law/processed/case_citations.csv", index=False)

print(f"Merged {before} 'Indian Penal Code' entries into 'Penal Code'")

counts = df["act_name_normalized"].value_counts()
print("\nUpdated top acts:")
print(counts.head(15))
