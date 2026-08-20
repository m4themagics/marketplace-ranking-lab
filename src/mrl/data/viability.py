"""Measurements for the dataset viability test.

The question these answer: does the catalogue renew enough, at the level of genuine products
rather than colour variants, for a codebook fit at t0 to be strained by later cohorts?

Thresholds are preregistered in ``experiments/00_dataset_viability/README.md``. They live
here as constants so that changing one shows up in a diff rather than in a notebook.
"""

from __future__ import annotations

import math
from datetime import timedelta
from typing import TypedDict

import polars as pl

#: Share of the final six months' catalogue that must be newly arrived in that window.
PASS_A_MIN_RENEWAL = 0.20

#: Share of final-quarter transactions that must go to items arrived in the prior 90 days.
PASS_B_MIN_TRANSACTION_SHARE = 0.10

#: Jensen-Shannon divergence between the earliest and latest arrival cohort's attribute mix.
PASS_C_MIN_DIVERGENCE = 0.05


class PermutationNullBand(TypedDict):
    """Stable report contract for criterion C.

    The implementation is a learning exercise, but its output is fixed up front so the
    experiment runner and reports cannot quietly change meaning after seeing the data.
    """

    observed_first_to_last: float
    first_to_last_lower: float
    first_to_last_upper: float
    observed_trend_slope: float
    trend_slope_lower: float
    trend_slope_upper: float
    n_permutations: int
    seed: int
    min_cohort_size: int


def flagship_gates(
    *,
    product_renewal: float,
    new_item_transaction_share: float,
) -> dict[str, bool]:
    """Return the only two gates that decide whether experiments 05–06 are viable.

    Content shift is deliberately absent: criterion C is a measurement whose low and high
    outcomes are both informative, not a reason to reject the earlier ranking experiments.
    """
    return {
        "A_product_renewal": product_renewal >= PASS_A_MIN_RENEWAL,
        "B_transaction_weight": (
            new_item_transaction_share >= PASS_B_MIN_TRANSACTION_SHARE
        ),
    }


def arrival_cohorts(events: pl.LazyFrame, *, level: str) -> pl.DataFrame:
    """First observed transaction date per item, bucketed into monthly cohorts.

    ``min(t_dat)`` is a proxy for catalogue arrival, not the arrival itself. It biases
    slow-selling items late: an item stocked in January but first bought in March is
    recorded as a March arrival.
    """
    return (
        events.group_by(level)
        .agg(pl.col("t_dat").min().alias("first_seen"))
        .with_columns(pl.col("first_seen").dt.truncate("1mo").alias("cohort"))
        .collect()
    )


def renewal_in_final_window(
    events: pl.LazyFrame,
    cohorts: pl.DataFrame,
    *,
    level: str,
    months: int,
) -> float:
    """Among items *transacted* in the final window, the share that arrived inside it.

    Deliberately not "share of the whole catalogue that is new": a catalogue can accumulate
    dead stock forever and look renewed. What matters is how much of current trading happens
    on items the codebook would never have seen.

    A value near zero means the catalogue was essentially complete at the start, and there is
    no arrival process to study.
    """
    sold = events.select("t_dat", level).collect()
    last = sold["t_dat"].max()
    if last is None or sold.height == 0:
        return 0.0

    cutoff = last - timedelta(days=30 * months)
    active = sold.filter(pl.col("t_dat") >= cutoff).select(level).unique()
    if active.height == 0:
        return 0.0

    joined = active.join(cohorts.select(level, "first_seen"), on=level, how="left")
    is_new = joined["first_seen"] >= cutoff
    return float(is_new.sum() / joined.height)


def new_item_transaction_share(
    events: pl.LazyFrame,
    cohorts: pl.DataFrame,
    *,
    level: str,
    window_days: int,
) -> float:
    """Share of final-quarter transactions going to recently arrived items.

    Renewal alone is not enough: a catalogue can churn in the long tail while all the volume
    stays on items that have been there for years. In that case degradation on new items is
    real but economically irrelevant, and the experiment measures nothing that matters.
    """
    collected = events.select("t_dat", level).collect()
    last = collected["t_dat"].max()
    if last is None or collected.height == 0:
        return 0.0

    quarter_start = last - timedelta(days=90)
    recent = collected.filter(pl.col("t_dat") >= quarter_start)
    if recent.height == 0:
        return 0.0

    joined = recent.join(cohorts.select(level, "first_seen"), on=level, how="left")
    arrival_cutoff = quarter_start - timedelta(days=window_days)
    is_new = joined["first_seen"] >= arrival_cutoff
    return float(is_new.sum() / joined.height)


def _jensen_shannon(p: dict[str, float], q: dict[str, float]) -> float:
    """Jensen-Shannon divergence between two categorical distributions, base 2."""
    keys = set(p) | set(q)

    def kl(a: dict[str, float], b: dict[str, float]) -> float:
        total = 0.0
        for key in keys:
            pa = a.get(key, 0.0)
            pb = b.get(key, 0.0)
            if pa > 0 and pb > 0:
                total += pa * math.log2(pa / pb)
        return total

    m = {key: 0.5 * (p.get(key, 0.0) + q.get(key, 0.0)) for key in keys}
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def attribute_divergence(
    events: pl.LazyFrame,
    cohorts: pl.DataFrame,
    *,
    level: str,
    min_cohort_size: int = 50,
) -> dict[str, float]:
    """How much the attribute mix of arriving items moves across cohorts.

    If arrivals look like what came before, a codebook fit on the earlier catalogue has no
    reason to strain — renewal without content shift predicts a null result, which is worth
    knowing before three months are spent on it.
    """
    attributes = (
        events.select(level, "product_type_name", "garment_group_name")
        .unique(subset=[level])
        .collect()
    )
    labelled = cohorts.join(attributes, on=level, how="left").with_columns(
        (pl.col("garment_group_name").fill_null("?") + " | " + pl.col("product_type_name").fill_null("?")).alias("attr")
    )

    per_cohort: list[tuple[object, dict[str, float]]] = []
    for cohort, part in labelled.group_by("cohort", maintain_order=True):
        counts = part["attr"].value_counts()
        total = counts["count"].sum()
        if total < min_cohort_size:  # too few arrivals to compare distributions
            continue
        per_cohort.append(
            (
                cohort[0] if isinstance(cohort, tuple) else cohort,
                {row["attr"]: row["count"] / total for row in counts.to_dicts()},
            )
        )

    per_cohort.sort(key=lambda item: item[0])
    if len(per_cohort) < 3:
        return {"first_to_last": 0.0, "trend_slope": 0.0, "n_cohorts": len(per_cohort)}

    baseline = per_cohort[0][1]
    divergences = [_jensen_shannon(baseline, dist) for _, dist in per_cohort]

    n = len(divergences)
    mean_x = (n - 1) / 2
    mean_y = sum(divergences) / n
    denominator = sum((i - mean_x) ** 2 for i in range(n))
    slope = (
        sum((i - mean_x) * (divergences[i] - mean_y) for i in range(n)) / denominator
        if denominator
        else 0.0
    )

    return {
        "first_to_last": divergences[-1],
        "trend_slope": slope,
        "n_cohorts": n,
        "divergence_curve": divergences,
    }


def permutation_null_band(
    events: pl.LazyFrame,
    cohorts: pl.DataFrame,
    *,
    level: str,
    n_permutations: int = 200,
    seed: int = 0,
    min_cohort_size: int = 50,
    quantiles: tuple[float, float] = (0.025, 0.975),
) -> PermutationNullBand:
    """Exercise: the null band criterion C is read against.

    ``attribute_divergence`` returns a number. A number alone cannot say whether arrivals
    genuinely changed, because JS divergence between two finite samples is above zero even
    when both are drawn from the same distribution — the sparser the attribute mix and the
    smaller the cohorts, the further above zero. Without a null band, criterion C measures
    cohort size as much as it measures content shift.

    Decide and write down before implementing:

    1. what is exchangeable under the null — which labels get shuffled, and which structure
       of the real data must survive the shuffle untouched;
    2. which statistic the band is built for: first-to-last divergence, the trend slope, or
       both, and whether one band can serve both;
    3. ``n_permutations``, ``seed``, and whether the interval is one- or two-sided, given
       that C only ever asks whether the divergence is *higher* than chance;
    4. what the band means at H&M's scale. With ~47k products the test is significant for
       any nonzero difference, so this is a ruler for effect size, not a gate. The plan is
       explicit that a low C does not reject the dataset.

    Failure modes worth a test each:

    - shuffling the attributes instead of the cohort labels: cohort sizes stop being fixed,
      the band comes out too narrow, and every observed value looks significant;
    - a band computed with a different ``min_cohort_size`` than the observed value it is
      compared against — the two are then not the same statistic;
    - reusing one RNG stream across calls, so two runs of the same command disagree.

    Args:
        events: transactions joined to article attributes.
        cohorts: output of :func:`arrival_cohorts` for the same ``level``.
        level: ``product_code`` for the decision, ``article_id`` for the diagnostic.
        n_permutations: draws from the null.
        seed: fixed, and recorded in the run manifest.
        min_cohort_size: must match the value used for the observed divergence.
        quantiles: lower and upper edge of the band.

    Returns:
        ``observed_first_to_last``, ``first_to_last_lower``,
        ``first_to_last_upper``, ``observed_trend_slope``, ``trend_slope_lower``,
        ``trend_slope_upper``, ``n_permutations``, ``seed`` and ``min_cohort_size``.
    """
    raise NotImplementedError("Exercise: implement the permutation null band for criterion C")
