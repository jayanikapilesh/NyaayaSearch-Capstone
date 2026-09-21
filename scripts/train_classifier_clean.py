import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

df = pd.read_csv("../data/eval/classifier_training_data_clean.csv")

features = ["hybrid_score", "semantic_score", "bm25_score", "matched_term_count", "rank", "reciprocal_rank", "query_length", "matched_term_ratio", "semantic_minus_bm25"]
X = df[features]
y = df["is_relevant"]
groups = df["query"]

# GROUPED split: all rows for a given query go entirely into train OR test, never both
splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

train_queries = set(df.iloc[train_idx]["query"])
test_queries = set(df.iloc[test_idx]["query"])
overlap = train_queries.intersection(test_queries)

print(f"Training set: {len(X_train)} examples ({y_train.sum()} relevant), {len(train_queries)} unique queries")
print(f"Test set: {len(X_test)} examples ({y_test.sum()} relevant), {len(test_queries)} unique queries")
print(f"Query overlap between train and test (should be 0): {len(overlap)}")


def evaluate(name, model):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\n--- {name} ---")
    print(f"Accuracy:  {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1 Score:  {f1:.3f}")

    cm = confusion_matrix(y_test, y_pred)
    print(f"Confusion matrix: TN={cm[0][0]} FP={cm[0][1]} FN={cm[1][0]} TP={cm[1][1]}")
    return f1, model


results = {}
lr = LogisticRegression(max_iter=1000, class_weight="balanced")
f1, m = evaluate("Logistic Regression (class_weight=balanced)", lr)
results["logistic_regression"] = (f1, m)

rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
f1, m = evaluate("Random Forest (class_weight=balanced)", rf)
results["random_forest"] = (f1, m)

gb = GradientBoostingClassifier(random_state=42)
f1, m = evaluate("Gradient Boosting", gb)
results["gradient_boosting"] = (f1, m)

svm = SVC(probability=True, random_state=42, class_weight="balanced")
f1, m = evaluate("Support Vector Machine (class_weight=balanced)", svm)
results["svm"] = (f1, m)

voting = VotingClassifier(estimators=[("lr", lr), ("rf", rf)], voting="soft")
f1, m = evaluate("Voting Ensemble (LR + RF)", voting)
results["voting_ensemble"] = (f1, m)

print("\n" + "=" * 50)
print("SUMMARY (grouped split, no train/test query leakage)")
print("=" * 50)
for name, (f1, m) in results.items():
    print(f"{name}: F1 = {f1:.3f}")

best_name = max(results, key=lambda k: results[k][0])
best_f1, best_model = results[best_name]
print(f"\nBest model by F1: {best_name}")
joblib.dump(best_model, "../relevance_classifier_clean.pkl")
print(f"Saved clean, leakage-free model to ../relevance_classifier_clean.pkl (NOT overwriting production yet)")
