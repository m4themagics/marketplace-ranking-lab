# 02 — What does Two-Tower add over ALS retrieval?

**Status:** design scaffolded, not started. Opens only after the PyTorch Module 7 gate and
depends on the shared temporal split, evaluation core and classical baseline.

## Question

At the same candidate budget, where does a Two-Tower retriever improve or lose candidate
recall relative to tuned ALS, and do those differences survive a common reranking protocol?

## Comparisons

The experiment publishes two comparisons and never collapses them into one delta:

1. **Retrieval-only, primary.** ALS and Two-Tower each return 500 candidates per customer-day.
   Report candidate Recall@100/500, coverage and cold/new-item slices. Exact dot-product top-K
   is the neural correctness oracle.
2. **End-to-end, secondary.** Train one LambdaRank model on the union of train-time candidates
   from both retrievers, using a shared feature schema without retriever-specific raw scores.
   Apply that same fitted ranker separately to each candidate pool and report NDCG@12,
   Recall@12 and captured-value coverage.

This does not make the end-to-end comparison perfectly causal: changing a retriever changes
the candidate distribution. It does stop a separately tuned ranker from being mistaken for a
retrieval improvement.

## Model contract

- user and item towers produce embeddings of the same declared dimension;
- training starts with in-batch negatives and records false-negative handling;
- sampled-softmax runs record the sampling distribution and apply logQ correction;
- hard-negative runs draw only from train-time candidate pools;
- one-batch overfit, gradient presence, save/load equality and exact top-K on a hand-computed
  example are correctness gates, not optional diagnostics.

## Evaluation contract

- Same absolute-time split, population and exclusion rules as ALS.
- Same candidate budget; ties and duplicate candidates follow the evaluation-core contract.
- Candidate metrics and final-list metrics are stored separately per customer for paired
  bootstrap by customer.
- Primary slices: history length, item popularity, new versus previously observed items, and
  customer activity. A slice is reported with its coverage.
- Training cost, exact retrieval latency and embedding memory are reported next to quality.

## Definition of done

- ALS and Two-Tower have exact, reproducible candidate files for the same evaluation rows.
- Primary and secondary comparisons have paired intervals and no split leakage.
- A negative result is retained and explained by slices rather than hidden by retuning K.
- The author can distinguish model training, exact retrieval and ANN serving without notes.

## Run

Not yet runnable — the PyTorch readiness gate and shared baseline are incomplete.
