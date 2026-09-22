import pandas as pd
df = pd.read_csv("../data/eval/classifier_training_data_clean.csv")
print(f"Unique queries in current file: {df['query'].nunique()}")
