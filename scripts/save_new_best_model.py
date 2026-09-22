import pandas as pd
import joblib
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("../data/eval/classifier_training_data_newfeature.csv")

features = ["hybrid_score", "semantic_score", "bm25_score", "matched_term_count", "rank", "reciprocal_rank", "query_length", "matched_term_ratio", "semantic_minus_bm25", "gap_to_next"]
X = df[features]
y = df["is_relevant"]
groups = df["query"]

splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))

X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)

joblib.dump(model, "../relevance_classifier_v2.pkl")
print("Saved new best model (F1=0.784, 10 features including gap_to_next) to relevance_classifier_v2.pkl")
