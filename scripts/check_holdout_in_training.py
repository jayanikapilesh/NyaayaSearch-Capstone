import pandas as pd

df = pd.read_csv("../data/eval/classifier_training_data_v2.csv")
training_queries = set(df["query"])

holdout_sample_check = [
    "Can I leave property to my grandchild who hasn't been born yet?",
    "Someone took my car without asking me, is that a crime?",
    "Who appoints the Chief Information Commissioner?",
    "Can I appeal a decision made under the Motor Vehicles Act?",
]

for q in holdout_sample_check:
    print(f"{'FOUND in training data' if q in training_queries else 'not found'}: {q}")
