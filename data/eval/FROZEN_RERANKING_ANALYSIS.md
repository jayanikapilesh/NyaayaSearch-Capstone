# Reranking Analysis - FROZEN

This documents the final, complete reranking evaluation. No further
classifier reranking experiments should be run after this point.

## Two evaluation sets, two different findings - both real, both honest

### 55-query held-out set (original, from earlier session)
- Search-only Top-1 accuracy: 49.1% (27/55)
- Classifier-reranked Top-1 accuracy: 67.3% (37/55)
- Delta: +18.2 percentage points
- Script: scripts/compare_search_vs_reranked.py

### 148-query frozen category set (this session, V1 baseline system)
- Search-only Top-1 accuracy: 50.68% (75/148)
- Classifier-reranked Top-1 accuracy: 50.68% (75/148)
- Delta: 0.0 percentage points
- Search-only Recall@5: 77.70%
- Classifier-reranked Recall@5: 75.68%
- Delta: -2.03 percentage points
- Search-only MRR: 0.6088
- Classifier-reranked MRR: 0.6081
- Delta: -0.0007
- Script: scripts/test_recall_mrr_reranked_v1.py (run against git tag
  v1-original-baseline for a clean, uncontaminated comparison)

## Honest interpretation

The reranking classifier shows dataset-dependent effectiveness: a
substantial improvement on the original 55-query held-out set, but no
measurable benefit - and a small negative effect on Recall@5 and MRR -
on the broader, more diverse 148-query category-based set. This is not
a contradiction; it reflects that the classifier's benefit is not
uniform across all query types and retrieval conditions. Verified
across two different metrics (Top-1 accuracy and Recall@5/MRR) on the
same 148-query set to rule out a single-metric artifact.

## Status: FROZEN

No further reranking experiments. This is the final reported finding
on the classifier's real-world reranking value for the paper.
