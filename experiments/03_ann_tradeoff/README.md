# 03 — What does exact → HNSW cost?

**Status:** design scaffolded, not started. Depends on a verified exact Two-Tower index from
Experiment 02.

## Question

How much exact-neighbour recall is lost when serving the trained item embeddings through
HNSW, and what latency and memory does that buy?

## Oracle and population

- Exact dot-product top-500 over the frozen Experiment 02 item matrix is the oracle.
- ANN and exact use identical query embeddings, item eligibility filters and query sample.
- ANN recall is agreement with exact neighbours; recommendation relevance remains a separate
  downstream metric.

## Measurements

- Recall@100 and Recall@500 against exact retrieval.
- Warmed-up p50 and p95 query latency, plus build time.
- Resident index size and peak build memory.
- A fixed HNSW grid over `M`, `efConstruction` and `efSearch`, written into the protocol before
  the final sweep.
- Hardware, thread count, library version, seed and the exact/ANN input fingerprint.

## Correctness and timing gates

- A hand-computed embedding example produces the same exact neighbours as brute force.
- Warm-up queries are excluded from timing and the timed query order is fixed.
- Index construction and query timing are measured separately.
- No HNSW point is called better without reporting all three axes: recall, latency and memory.

## Definition of done

One reproducible table and trade-off plot identify the non-dominated HNSW configurations and
the selected operating point. If no configuration preserves enough exact recall, exact search
remains the result rather than being replaced for the sake of using ANN.

## Run

Not yet runnable — Experiment 02 has no trained item embeddings.
