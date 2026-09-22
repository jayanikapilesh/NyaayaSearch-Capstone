import os
import datetime
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import precision_recall_curve, average_precision_score

print("Loading real classifier training data and the actual saved production model...")
df = pd.read_csv("../data/eval/classifier_training_data_production826.csv")
model = joblib.load("../relevance_classifier.pkl")

features = ["hybrid_score", "semantic_score", "bm25_score", "matched_term_count", "rank", "reciprocal_rank", "query_length", "matched_term_ratio", "semantic_minus_bm25", "gap_to_next"]

# Use only the features the loaded model actually expects (handles older/newer model versions)
if hasattr(model, "feature_names_in_"):
    features = [f for f in features if f in list(model.feature_names_in_)]

X = df[features]
y = df["is_relevant"]
groups = df["query"]

# Same grouped split used when this model was originally trained - ensures
# the test set here is genuinely unseen by the model, not leaked.
splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))
X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]

print(f"Test set: {len(X_test)} examples, {y_test.sum()} relevant")

y_scores = model.predict_proba(X_test)[:, 1]
precision, recall, thresholds = precision_recall_curve(y_test, y_scores)
avg_precision = average_precision_score(y_test, y_scores)

print(f"Average Precision (real, computed): {avg_precision:.4f}")

fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(recall, precision, color="#4C72B0", linewidth=2)
ax.set_xlabel("Recall")
ax.set_ylabel("Precision")
ax.set_title(f"Classifier Precision-Recall Curve (AP={avg_precision:.3f}, real computed)")
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 1.05)
ax.grid(alpha=0.3)
plt.tight_layout()

os.makedirs("../results/figures", exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filepath = f"../results/figures/classifier_pr_curve_{timestamp}.png"
plt.savefig(filepath, dpi=150)
plt.close()
print(f"PR curve saved to: {filepath}")
