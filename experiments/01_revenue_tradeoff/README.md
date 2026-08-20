# 01 — What logged basket value is captured as relevance changes?

**Status:** design fixed, not yet run. Depends on the split, the metrics, and the
ALS + LambdaRank baseline being in place.

## Question

When item value is given more weight, how does the share of observed basket value captured in
top 12 change relative to NDCG@12, and which policies lie on the Pareto frontier?

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
multi-task heads and constrained optimisation are different policy families; the experiment
implements only scalarisation and explains the other two.

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
- **Score:** `p_proxy ^ α · price ^ β`, with `α = 1` and a preregistered non-negative grid for
  `β`. Multiplication keeps both factors positive; it does not make the proxy causal.
- **Relevance metrics:** NDCG@12 and Recall@12.
- **Value metric:** captured logged basket value@12 — the summed price of observed purchased
  items in top 12 divided by the observed basket value for that customer-day. Queries with no
  logged purchase are outside this conditional metric and their coverage is reported.
- **Uncertainty:** paired bootstrap by customer, never by event or customer-day.

## Preregistered reading

- Mark `β = 0` as the relevance-only baseline and publish every swept point plus the
  non-dominated Pareto frontier.
- Report effect sizes and paired intervals relative to baseline; do not call an offline value
  delta “revenue uplift”.
- Price correlates with product group, so publish top-12 garment-group composition at the
  baseline, a middle Pareto point and the value-heavy endpoint.
- If the apparent trade-off is entirely a category-composition change, that mechanism is the
  finding.
- The conclusion must name missing impressions, exposure bias and the fact that an online
  policy changes its own future training distribution.

## Outcomes

| Result | Permitted interpretation |
|---|---|
| Stable Pareto frontier | The offline relevance/value exchange rate is measurable on this logged population. |
| Flat region before a knee | Some logged basket value is recovered without a detectable relevance loss; online impact remains unknown. |
| Entirely a category shift | The mechanism is composition, not evidence of general value optimisation. |
| Poor calibration | The scalarised proxy is invalid; fix calibration before interpreting the sweep. |
| Irregular raw curve | Keep every point and report the Pareto frontier; irregularity alone is not a calibration diagnosis. |

## Run

Not yet runnable — no split, metrics, calibration or baseline.
