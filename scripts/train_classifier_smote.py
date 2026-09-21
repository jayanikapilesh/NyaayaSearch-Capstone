import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from imblearn.over_sampling import SMOTE
import joblib

df = pd.read_csv("../data/eval/classifier_training_data_v2.csv")

features = ["hybrid_score", "semantic_score", "bm25_score", "matched_term_count", "rank", "reciprocal_rank", "query_length", "matched_term_ratio", "semantic_minus_bm25"]
X = df[features]
y = df["is_relevant"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

print(f"Original training set: {len(X_train)} examples ({y_train.sum()} relevant)")

smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

print(f"After SMOTE: {len(X_train_smote)} examples ({y_train_smote.sum()} relevant)")
print(f"Test set (untouched, original distribution): {len(X_test)} examples ({y_test.sum()} relevant)")


def evaluate(name, model):
    model.fit(X_train_smote, y_train_smote)
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

lr = LogisticRegression(max_iter=1000)
f1, m = evaluate("Logistic Regression (SMOTE)", lr)
results["logistic_regression"] = (f1, m)

rf = RandomForestClassifier(n_estimators=100, random_state=42)
f1, m = evaluate("Random Forest (SMOTE)", rf)
results["random_forest"] = (f1, m)

gb = GradientBoostingClassifier(random_state=42)
f1, m = evaluate("Gradient Boosting (SMOTE)", gb)
results["gradient_boosting"] = (f1, m)

svm = SVC(probability=True, random_state=42)
f1, m = evaluate("SVM (SMOTE)", svm)
results["svm"] = (f1, m)

voting = VotingClassifier(estimators=[("lr", lr), ("rf", rf)], voting="soft")
f1, m = evaluate("Voting Ensemble (SMOTE)", voting)
results["voting_ensemble"] = (f1, m)

print("\n" + "=" * 50)
print("SUMMARY (SMOTE-resampled training data)")
print("=" * 50)
for name, (f1, m) in results.items():
    print(f"{name}: F1 = {f1:.3f}")

best_name = max(results, key=lambda k: results[k][0])
best_f1, best_model = results[best_name]
print(f"\nBest model by F1: {best_name}")
joblib.dump(best_model, "../relevance_classifier_smote_experiment.pkl")
print(f"Saved experimental SMOTE model (NOT overwriting production classifier) to ../relevance_classifier_smote_experiment.pkl")
