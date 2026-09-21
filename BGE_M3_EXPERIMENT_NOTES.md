# BGE-M3 Multilingual Embedding Experiment - NOT FEASIBLE (documented for honesty)

## What was attempted
Tested BAAI/bge-m3, a multilingual embedding model, as a potential replacement
for the current translate-then-search pipeline. The idea: search Hindi/Kannada
queries directly against section embeddings, without first translating to
English via the Groq API - removing a point of failure (translation errors,
API rate limits) and potentially improving accuracy since BGE-M3 handles
Hindi/Kannada natively.

## Why it was not pursued
Embedding all 1,887 legal sections with BGE-M3 on available hardware (CPU only,
no GPU acceleration) was projected to take approximately 8 hours based on
observed batch processing speed (240 seconds per batch of 16, 118 batches
total). This is computationally impractical for this project's timeline and
hardware.

## Honest conclusion
BGE-M3 (or similar large multilingual embedding models) may be a viable
future improvement IF GPU acceleration is available. On CPU-only consumer
hardware, the current lightweight fine-tuned embedding model remains the
practical choice, even though it requires translation as a preprocessing
step. This is a legitimate hardware/resource constraint, not a finding about
BGE-M3s quality - its actual retrieval performance was never measured, since
the embedding step alone was not completable in reasonable time.

## For the paper
Worth mentioning briefly in Future Work: "A multilingual embedding model
(e.g. BGE-M3) was considered as an alternative to the current translate-then-
search approach, which could reduce both latency and translation-error risk.
This was not evaluated due to hardware constraints (CPU-only embedding of the
1,887-section corpus was computationally impractical); GPU-accelerated
evaluation is left for future work."
