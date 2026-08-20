# 04 — Where does offline evaluation diverge from online behaviour?

**Status:** writing scaffolded, not started. This experiment intentionally has no simulation
or fake A/B implementation.

## Question

Where do exposure and position bias enter the H&M learning and evaluation pipeline, which
claims remain identifiable from purchases alone, and what would have to be logged online to
evaluate a replacement policy?

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

## Definition of done

The note is linked from the final report, explicitly limits every claim made by Experiments
01–03, and can be defended aloud without notes. No synthetic click simulator is presented as
evidence of online impact.
