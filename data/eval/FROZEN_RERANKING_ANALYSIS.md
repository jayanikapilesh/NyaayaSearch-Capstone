# Reranking Analysis - FROZEN (CORRECTED)

## IMPORTANT CORRECTION

An earlier version of this analysis reported a +18.2 percentage point
Top-1 improvement from classifier reranking on the 55-query held-out
set. This result was found to be INVALID due to train/test leakage:
the 55 held-out queries (and the 42 tuned eval queries) were
inadvertently included in the classifier's own training data. The
classifier had partially "seen" these queries during training, so
testing reranking on them was not a genuine generalization test.

## The fix

1. Rebuilt classifier training data using ONLY the 826 purpose-built
   query-section pairs (training_pairs.jsonl + training_pairs_batch2.jsonl),
   explicitly excluding the 42 tuned and 55 held-out evaluation queries.
2. Switched from a row-level train/test split to a GroupShuffleSplit by
   query, ensuring zero query overlap between train and test even within
   the remaining data (verified: 0 overlapping queries).
3. Retrained: the clean classifier achieves F1=0.772 (Voting Ensemble),
   HIGHER than the contaminated version's F1=0.719 - the leakage was not
   inflating the classifier's own quality metric, only the reranking
   Top-1 claim.
4. This clean classifier is now the production model
   (relevance_classifier.pkl).

## Corrected, trustworthy results

### 55-query held-out set (classifier now genuinely never trained on these)
- Search-only Top-1 accuracy: 49.1% (27/55)
- Classifier-reranked Top-1 accuracy: 49.1% (27/55)
- Delta: 0.0 percentage points (CORRECTED from the invalid +18.2pp claim)
- Script: scripts/test_clean_reranking_55.py

### 148-query frozen category set (was already clean, unaffected)
- Search-only Top-1 accuracy: 50.68% (75/148)
- Classifier-reranked Top-1 accuracy: 50.68% (75/148)
- Delta: 0.0 percentage points
- Search-only Recall@5: 77.70%, Reranked Recall@5: 75.68% (-2.03pp)
- Search-only MRR: 0.6088, Reranked MRR: 0.6081 (-0.0007)

## Honest interpretation

Both evaluation sets, tested cleanly and independently, now agree: the
classifier reranker provides no measurable Top-1 accuracy improvement.
This is a genuine, consistent finding across two separate test sets,
not an artifact. The classifier itself (F1=0.772 on unseen data) shows
real discriminative ability at the relevance-classification task in
isolation, but this does not translate into improved end-to-end top-1
retrieval ranking on either evaluation set tested.

## Lesson learned (worth stating explicitly in the paper)

This correction is itself a legitimate methodological finding worth
reporting: an initial evaluation suggested a substantial reranking
benefit, but a subsequent data-leakage audit revealed the training and
evaluation sets were not properly isolated. After fixing the leakage
(purpose-built training data only, grouped train/test split), the
apparent benefit disappeared, and both independent evaluation sets
consistently showed no Top-1 improvement. This underscores the
importance of verifying query-level (not just row-level) independence
between training and evaluation data in retrieval-adjacent ML tasks.

## Status: FROZEN (corrected)

This is the final, corrected, trustworthy finding on the classifier's
real-world reranking value for the paper.
