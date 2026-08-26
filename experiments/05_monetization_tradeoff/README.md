# 05 — Can a calibrated value objective improve the list without violating UX guardrails?

**Status:** design revised before any run on 2026-08-26; blocked until the 96-hour core closes.
This is an optional additional six-hour experiment.

## Question

When a calibrated expected-basket-value proxy is introduced as a second objective, how does
captured logged basket value@12 change relative to relevance and UX guardrails? Which
scalarised or constrained policies remain non-dominated?

This is deliberately narrower than “how much revenue will the policy make?”. H&M has purchases,
but no impression log, propensities or online randomisation. The experiment measures an offline
proxy on logged outcomes; it cannot identify causal revenue uplift or replace an A/B test.

## Why it is worth a directory

“Balance relevance against business value” is usually answered with a heuristic boost applied
after ranking. That answer has no explicit objective: it cannot say what was traded for what,
and it cannot be moved deliberately. This experiment exposes the choice as a curve while also
making the limit of that curve explicit.

The distinction the design rests on:

- objectives defined **on the list** — diversity, slot quotas, per-category caps — can be
  enforced during constrained list construction;
- objectives defined **on the item** — a conversion proxy or item value — must be represented
  before top-N truncation if they are expected to recover candidates the relevance-only policy
  would otherwise discard.

This does not imply that every item objective should be folded into one score. Scalarisation,
multi-task heads and constrained optimisation are different policy families. This bounded
experiment compares scalarisation with one constrained list-construction policy; it does not
open a new modelling or auctions track.

## Calibration contract

A LambdaRank score is an ordering, not a probability. `lgbm_score × price` is therefore not an
expected monetary value: the score has no stable unit and its scale can drift between queries.

The experiment uses isotonic calibration on a slice carved from validation, never test. The
target is the sampled offline candidate distribution, so the result is called a calibrated
purchase **proxy**, not a population purchase probability. The report includes:

- a reliability diagram;
- Brier score and expected calibration error (ECE);
- the positive rate and negative-sampling rule of the calibration population.

Poor calibration invalidates interpretation of the scalarised policy, but non-monotonic NDCG
along the raw sweep does not: top-K lists change discretely and price can correlate with
relevance.

## Design

- **Unit of observation:** one customer-day. Purchases on that day are the logged positives.
- **Candidates:** the baseline ALS pool, unchanged across the sweep, so the experiment varies
  ordering rather than retrieval.
- **Baseline:** relevance-only LambdaRank ordering.
- **Scalarised policy:** `p_proxy ^ α · price ^ β`, with `α = 1` and a preregistered
  non-negative grid for `β`. Multiplication keeps both factors positive; it does not make the
  proxy causal.
- **Constrained policy:** construct top 12 from the same scored pool under a garment-group cap.
  The cap grid and all guardrail thresholds remain `UNSET` until the protocol is frozen before
  the first run; no test result may be used to choose them.
- **UX guardrails:** NDCG@12, Recall@12, catalogue coverage@12 and top-12 garment-group
  concentration. Report local reranking runtime separately; it is not an online latency claim.
- **Value metric:** captured logged basket value@12 — the summed price of observed purchased
  items in top 12 divided by the observed basket value for that customer-day. Queries with no
  logged purchase are outside this conditional metric and their coverage is reported.
- **Uncertainty:** paired bootstrap by customer, never by event or customer-day.

## Preregistered reading

- Mark `β = 0` as the relevance-only baseline and publish every swept point plus the
  non-dominated Pareto frontier.
- Report effect sizes and paired intervals relative to baseline; do not call an offline value
  delta “revenue uplift”.
- Publish scalarised and constrained points on the same relevance/value plane. Infeasible
  constrained lists remain explicit; they are not silently filled from an unconstrained list.
- Price correlates with product group, so publish coverage and top-12 garment-group composition
  at the baseline, a middle Pareto point and the value-heavy endpoint.
- If the apparent trade-off is entirely a category-composition change, that mechanism is the
  finding.
- The conclusion must name missing impressions, exposure bias and the fact that an online
  policy changes its own future training distribution.

## A/B design — written, not simulated

The final note defines a future online test without pretending to run one:

- customer-level randomisation, eligibility and exposure logging;
- revenue per eligible user as the primary metric;
- conversion, average order value, engagement, diversity, complaints and p95 latency as
  secondary/guardrail metrics;
- power and duration assumptions, sample-ratio-mismatch checks, novelty and carry-over risks;
- segment analysis and an explicit decision rule for value gain with a failed UX guardrail;
- shadow, canary, A/B and rollback responsibilities kept distinct.

## Outcomes

| Result | Permitted interpretation |
|---|---|
| Stable Pareto frontier | The offline relevance/value exchange rate is measurable on this logged population. |
| Flat region before a knee | Some logged basket value is recovered without a detectable relevance loss; online impact remains unknown. |
| Entirely a category shift | The mechanism is composition, not evidence of general value optimisation. |
| Poor calibration | The scalarised proxy is invalid; fix calibration before interpreting the sweep. |
| Constrained policy protects UX but loses value | The constraint has a measurable cost; do not weaken it post hoc. |
| Value rises while a UX guardrail fails | Reject that policy; conflicting metrics are the result, not noise to hide. |
| Irregular raw curve | Keep every point and report the Pareto frontier; irregularity alone is not a calibration diagnosis. |

## Stop rule

Stop after six hours with one comparison table, a calibration/guardrail audit and the written
A/B design, even if the result is negative or thresholds remain infeasible. Pacing, bidding,
auctions and budget allocation stay deferred.

## Run gate

Not runnable before the 96-hour core closes. At activation, fill every `UNSET` value in a
separate protocol before looking at a test result; the split, metrics, calibration population
and ALS + LambdaRank baseline must already exist.
