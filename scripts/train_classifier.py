import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

df = pd.read_csv("../data/eval/classifier_training_data_v2.csv")

features = ["hybrid_score", "semantic_score", "bm25_score", "matched_term_count", "rank", "reciprocal_rank", "query_length", "matched_term_ratio", "semantic_minus_bm25"]
X = df[features]
y = df["is_relevant"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(f"Training set: {len(X_train)} examples ({y_train.sum()} relevant)")
print(f"Test set: {len(X_test)} examples ({y_test.sum()} relevant)")


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

    return model, f1


results = {}

results["logistic_regression"] = evaluate(
    "Logistic Regression (class_weight=balanced)",
    LogisticRegression(class_weight="balanced", random_state=42)
)

results["random_forest"] = evaluate(
    "Random Forest (class_weight=balanced)",
    RandomForestClassifier(class_weight="balanced", random_state=42, n_estimators=100)
)

results["gradient_boosting"] = evaluate(
    "Gradient Boosting",
    GradientBoostingClassifier(random_state=42, n_estimators=100)
)

results["svm"] = evaluate(
    "Support Vector Machine (class_weight=balanced)",
    SVC(class_weight="balanced", random_state=42, probability=True)
)

voting_model = VotingClassifier(
    estimators=[
        ("lr", LogisticRegression(class_weight="balanced", random_state=42)),
        ("rf", RandomForestClassifier(class_weight="balanced", random_state=42, n_estimators=100)),
    ],
    voting="soft"
)
results["voting_ensemble"] = evaluate("Voting Ensemble (LR + RF)", voting_model)

print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
for name, (model, f1) in results.items():
    print(f"{name}: F1 = {f1:.3f}")

best_name = max(results, key=lambda k: results[k][1])
best_model = results[best_name][0]
print(f"\nBest model by F1: {best_name}")

joblib.dump(best_model, "../relevance_classifier.pkl")
print(f"Saved best model ({best_name}) to ../relevance_classifier.pkl")



