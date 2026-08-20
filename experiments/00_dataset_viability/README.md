# 00 — Dataset viability: does the catalogue actually turn over?

**Status:** preregistered, runner scaffolded, data fingerprinted, central permutation exercise pending.
Criteria last amended 2026-08-20, before any data existed locally.

This experiment exists to kill the **flagship codebook-drift question** cheaply if its premise
is false. It runs before H&M is committed to experiments 05–06. Experiments 01–04 do not
depend on catalogue renewal and continue on H&M under either verdict.

## Question

Does the H&M dataset contain enough observable catalogue renewal, at the level of genuine
products rather than colour variants, for a fixed content codebook to be measurably strained
by later item cohorts?

## Why it must run first

The central question assumes new items keep arriving and that they differ from the items the
codebook was fit on. That assumption is about the data, not about the method — and it is
cheap to check and expensive to be wrong about. If it fails, the twelve-week ranking lab
continues, but the post-week-12 codebook work does not start on H&M.

Two known traps:

**Variants masquerading as arrivals.** H&M has roughly 105.5k `article_id` values but only
about 47.2k `product_code` values: one product appears as many articles, one per colour or
size grouping. A new `article_id` may simply be a new colour of a product that has existed
for a year. Every turnover statistic here is therefore computed at **both** levels, and the
`product_code` level is the one that decides.

**First transaction is not catalogue entry.** No public dataset publishes the date an item
became available. `min(t_dat)` per item is a proxy and is treated as one. It is a better
proxy for transactions than for reviews — there is no unknown delay between buying and the
event being recorded — but it still biases arrival times late for slow-selling items.

## Preregistered criteria

**A and B decide.** C is measured, not enforced. Thresholds are judgement calls; the point of
writing them down now is that they cannot be adjusted after the numbers are seen.

*Amended 2026-08-20, before any data was downloaded and before any number was seen: C was
originally a third blocking criterion. It is not one. A catalogue that renews while staying
self-similar is a perfectly good setting for the flagship question — it predicts that a frozen
quantiser generalises, which the experiment then confirms or refutes. A/B now gate only
experiments 05–06; the earlier ranking experiments remain valid without catalogue renewal.*

**A — Product-level renewal.** Among `product_code`s transacted in the final six months, at
least **20%** were first seen in that final six-month window.
*If nearly the whole catalogue was present from the start, there is no arrival process.*

**B — Economic weight of arrivals.** In the final quarter, at least **10%** of transactions
go to `product_code`s first seen within the preceding 90 days.
*If new products carry negligible volume, degradation on them does not matter.*

**C — Content shift (measurement).** How far the attribute mix (garment group × product
type) of new-product cohorts moves over time: Jensen–Shannon divergence from the earliest
cohort, read against a permutation null band rather than against a bare threshold. At ~47k
products a permutation test is significant for any nonzero difference, so this is an effect
size, not a gate. **0.05** is kept as an orientation mark, not a pass condition.
*A low C does not reject the dataset. It predicts that a codebook fit on the earlier catalogue
generalises well — a smaller but publishable result.*

## Diagnostic that decides between two stories

The ratio of article-level to product-level renewal. If article-level turnover looks vigorous
and product-level turnover does not, the apparent churn is variant proliferation, and H&M is
substantially weaker for this hypothesis than it appears.

## Outcomes

| Result | Action |
|---|---|
| A and B pass, C high | Open experiments 05–06 on H&M and record the high-shift hypothesis. |
| A and B pass, C inside the null band | Open experiments 05–06 on H&M and record the prediction that a frozen quantiser should generalise well. |
| A or B fails | Continue experiments 01–04 on H&M; keep 05–06 closed and choose any replacement dataset only after the twelve-week market phase. |

## Run

```bash
uv run python experiments/00_dataset_viability/run.py --data data/raw
```

Expects `transactions_train.csv` and `articles.csv` from the Kaggle competition.
The JSON report has stable top-level `run`, `gates`, `measurements` and
`flagship_viable` fields. `gates` contains only A and B; C and its null band live under
`measurements`.
