import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

df = pd.read_csv("../data/eval/classifier_training_data_newfeature.csv")

features = ["hybrid_score", "semantic_score", "bm25_score", "matched_term_count", "rank", "reciprocal_rank", "query_length", "matched_term_ratio", "semantic_minus_bm25", "gap_to_next"]
X = df[features]
y = df["is_relevant"]
groups = df["query"]

splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

train_queries = set(df.iloc[train_idx]["query"])
test_queries = set(df.iloc[test_idx]["query"])
overlap = train_queries.intersection(test_queries)
print(f"Query overlap (should be 0): {len(overlap)}")


def evaluate(name, model):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{name}: F1={f1:.3f} Precision={precision:.3f} Recall={recall:.3f} Accuracy={accuracy:.3f}")
    return f1


lr = LogisticRegression(max_iter=1000, class_weight="balanced")
rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
gb = GradientBoostingClassifier(random_state=42)
svm = SVC(probability=True, random_state=42, class_weight="balanced")
voting = VotingClassifier(estimators=[("lr", lr), ("rf", rf)], voting="soft")

print("\nWith NEW gap_to_next feature added (10 features total):")
evaluate("Logistic Regression", lr)
evaluate("Random Forest", rf)
evaluate("Gradient Boosting", gb)
evaluate("SVM", svm)
evaluate("Voting Ensemble", voting)

print("\nFor comparison, current production (9 features, no gap_to_next): F1=0.772")
