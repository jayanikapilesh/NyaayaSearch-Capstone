# NyaayaSearch-Final-Evaluation-v1 (FROZEN)

This file documents the final, frozen 148-query category-based evaluation.
Do not modify the query set or retrieval system based on these results -
this is the final reported number for the paper.

## Evaluation Set Design: Relationship to the multilingual evaluation

The English and multilingual evaluations were designed as separate
experiments with different objectives. The 148-query English evaluation
measures retrieval robustness across diverse query formulations,
including simple, vague, and synonym-rich queries. A separate 40-query
multilingual evaluation (21 Hindi, 19 Kannada - see
scripts/test_multilingual_expanded.py) assesses whether retrieval
performance is maintained across Hindi and Kannada queries. Therefore,
the evaluation-set sizes differ intentionally and should not be
interpreted as missing or inconsistent data. Report the two sets side
by side, not as one combined sample.

## Methodology
- 149 queries constructed across 8 categories (Simple/Direct, Synonym-heavy,
  BNS/BNSS Terminology, Broad/Ambiguous, Specific Legal Concepts,
  Natural-language, Case-law style, Multilingual Hindi/Kannada), 20 per
  category (9 for multilingual: 5 Hindi + 4 Kannada), each with a manually
  identified correct Act + Section.
- A retrieval was scored as a hit when at least one of the top-5 results
  matched the manually annotated relevant Act and Section (exact match on
  both fields). This is a strict, unambiguous hit criterion, not a semantic
  or partial-relevance judgment - referred to here as Recall@5 under the
  Act-Section exact-match relevance criterion.
- Post-evaluation contamination check: all 149 queries were checked against
  every training/tuning data source (eval_queries.json, training_pairs.jsonl,
  training_pairs_batch2.jsonl) for exact text overlap. One duplicate was
  found ("What is a contingent contract?", present in the fine-tuning pairs)
  and excluded from the final count.

## Final frozen metrics (n=148, independent, decontaminated)
- Recall@5: 115/148 = 77.70%

## Recall@5 by category
- Simple/Direct: 100% (20/20)
- Specific Legal Concepts: 100% (20/20)
- BNS/BNSS Terminology: 95% (19/20)
- Multilingual (Hindi/Kannada combined): 77.8% (7/9) [small n, interpret cautiously]
- Natural-language: 75% (15/20)
- Case-law style: 70% (14/20)
- Broad/Ambiguous: 55% (11/20)
- Synonym-heavy: 50% (10/20)

## Failure analysis
33 total failures (34 before decontamination). Of these, 19 (57.6%) occurred
in the Synonym-heavy and Broad/Ambiguous categories combined, identifying
vocabulary mismatch and query underspecification as the two dominant
failure modes - consistent with the earlier qualitative failure analysis
(failure_analysis.md) but now with a controlled, quantified measurement.

## Reproducibility
- Query set and per-query hit/miss: data/eval/category_evaluation_full_results.csv
- Generation scripts: scripts/sample_category_batch.py through batch4.py
- Test scripts: scripts/test_categories_batch1.py through batch4.py
- Diagnostic/contamination check: scripts/diagnostic_category_eval.py
- Final clean metric computation: scripts/compute_final_clean_metrics.py
- Retrieval system version: commit 3be6b70 and earlier (search_core.py with
  synonym dictionary as expanded through this session)

## Status: FROZEN
No further tuning against this evaluation set. This is the final reported
number for the paper's retrieval evaluation section, alongside the earlier
42-query tuned set (Recall@5=0.881) and 55-query held-out set
(Recall@5=0.71-0.80), reported together with clear disclosure of which set
is which.


