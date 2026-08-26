# 04 — Where does offline evaluation diverge, and how is the online path defended?

**Status:** writing scaffolded, not started. This experiment intentionally has no simulation
or fake A/B/serving implementation. Its 12-hour scope closes the operational-defence part of
the 96-hour core.

## Question

Where do exposure and position bias enter the H&M learning and evaluation pipeline, which
claims remain identifiable from purchases alone, and what would have to be logged online to
evaluate a replacement policy? How would retrieval, ranking and response delivery be operated
under a declared latency budget without claiming that this repository serves traffic?

## Required analysis

The final note must trace one event through:

1. eligibility and candidate generation;
2. exposure and position;
3. customer action and delayed outcomes;
4. training-example construction;
5. offline evaluation;
6. deployment, feedback and retraining.

For every stage it names the observed variables, missing variables, selection mechanism and
the direction in which the resulting bias could move a reported metric.

## Required decisions

- Why H&M purchase logs cannot estimate a new policy's causal revenue uplift.
- What propensities IPS requires, when positivity fails and why clipping trades variance for
  bias.
- Which online metrics are primary and which guard relevance, diversity, latency, complaints
  and long-horizon customer value.
- How shadow, canary, A/B and rollback serve different purposes.
- Which logging contract would make the next offline dataset more useful: request ID,
  eligible pool, candidates, scores, positions, policy/version, propensity, actions and
  delayed outcomes.

## Required operational defence

- Trace the request path from eligibility and retrieval through ranking, optional constrained
  reranking and response assembly. Name the contract and failure boundary at every step.
- Allocate an end-to-end latency budget across retrieval, feature access, ranking and response;
  state timeouts, fallbacks and graceful-degradation order.
- Define RED signals plus model/data signals for candidate-pool size, feature freshness,
  score drift, fallback share and online guardrails. A dashboard sketch is a design, not a
  monitoring result.
- Explain how shadow, canary, A/B and rollback consume the same policy/version and logging
  identity, and which signal stops each stage.
- Separate evidence from this offline repository, personal production experience and proposed
  architecture in every answer.

## Definition of done

One end-to-end note is linked from the final report, explicitly limits every claim made by
Experiments 02–03, and can be defended aloud without notes under a timer. It contains the
request path, latency/fallback table, logging contract, observability set and rollout/A/B
decision path. No synthetic click simulator, serving diagram or dashboard sketch is presented
as evidence of online impact or implemented infrastructure.
