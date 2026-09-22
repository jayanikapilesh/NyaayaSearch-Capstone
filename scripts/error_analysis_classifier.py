import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("../data/eval/classifier_training_data_production826.csv")

features = ["hybrid_score", "semantic_score", "bm25_score", "matched_term_count", "rank", "reciprocal_rank", "query_length", "matched_term_ratio", "semantic_minus_bm25"]
X = df[features]
y = df["is_relevant"]
groups = df["query"]

splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

test_df = df.iloc[test_idx].copy()
test_df["predicted"] = y_pred
test_df["actual"] = y_test.values

false_positives = test_df[(test_df["actual"] == 0) & (test_df["predicted"] == 1)]
false_negatives = test_df[(test_df["actual"] == 1) & (test_df["predicted"] == 0)]

print(f"Total test examples: {len(test_df)}")
print(f"False positives (predicted relevant, actually not): {len(false_positives)}")
print(f"False negatives (predicted not relevant, actually relevant): {len(false_negatives)}")

print("\n" + "=" * 70)
print("SAMPLE FALSE POSITIVES (model said relevant, but wrong)")
print("=" * 70)
for _, row in false_positives.head(10).iterrows():
    print(f"Query: {row['query']}")
    print(f"  Wrongly matched: {row['act_name']} S{row['section_number']} (rank={row['rank']}, hybrid_score={row['hybrid_score']:.3f})")
    print()

print("=" * 70)
print("SAMPLE FALSE NEGATIVES (model said not relevant, but was actually correct)")
print("=" * 70)
for _, row in false_negatives.head(10).iterrows():
    print(f"Query: {row['query']}")
    print(f"  Missed correct match: {row['act_name']} S{row['section_number']} (rank={row['rank']}, hybrid_score={row['hybrid_score']:.3f})")
    print()
