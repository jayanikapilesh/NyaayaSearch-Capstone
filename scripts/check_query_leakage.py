import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("../data/eval/classifier_training_data_v2.csv")

features = ["hybrid_score", "semantic_score", "bm25_score", "matched_term_count", "rank", "reciprocal_rank", "query_length", "matched_term_ratio", "semantic_minus_bm25"]
X = df[features]
y = df["is_relevant"]

X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X, y, df.index, test_size=0.25, random_state=42, stratify=y
)

train_queries = set(df.loc[idx_train, "query"])
test_queries = set(df.loc[idx_test, "query"])

overlap = train_queries.intersection(test_queries)

print(f"Unique queries in training set: {len(train_queries)}")
print(f"Unique queries in test set: {len(test_queries)}")
print(f"Queries appearing in BOTH train and test (leakage): {len(overlap)}")
print(f"Percentage of test queries also seen in training: {len(overlap)/len(test_queries)*100:.1f}%")
