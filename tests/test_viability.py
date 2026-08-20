"""Tests for the dataset viability measurements.

These run on synthetic frames with known turnover, so the measurements are verified before
they are pointed at real data and a project decision is made on their output.
"""

from datetime import date, timedelta

import polars as pl

from mrl.data.viability import (
    arrival_cohorts,
    attribute_divergence,
    flagship_gates,
    new_item_transaction_share,
    renewal_in_final_window,
)

START = date(2020, 1, 1)


def build(rows: list[tuple[int, int, int, str, str]]) -> pl.LazyFrame:
    """rows: (day_offset, article_id, product_code, product_type, garment_group)."""
    return pl.LazyFrame(
        {
            "t_dat": [START + timedelta(days=r[0]) for r in rows],
            "article_id": [r[1] for r in rows],
            "product_code": [r[2] for r in rows],
            "product_type_name": [r[3] for r in rows],
            "garment_group_name": [r[4] for r in rows],
        }
    )


def test_arrival_cohort_is_first_transaction_not_last() -> None:
    events = build([(0, 1, 100, "tee", "jersey"), (200, 1, 100, "tee", "jersey")])

    cohorts = arrival_cohorts(events, level="article_id")

    assert cohorts.height == 1
    assert cohorts["first_seen"][0] == START


def test_static_catalogue_shows_no_renewal() -> None:
    # Same two products traded across the whole period, nothing new ever arrives.
    rows = [(day, 1, 100, "tee", "jersey") for day in range(0, 700, 7)]
    rows += [(day, 2, 200, "sock", "socks") for day in range(0, 700, 7)]
    events = build(rows)

    cohorts = arrival_cohorts(events, level="product_code")
    renewal = renewal_in_final_window(events, cohorts, level="product_code", months=6)

    assert renewal == 0.0


def test_fully_renewed_catalogue_shows_complete_renewal() -> None:
    # Every product traded in the last 6 months arrived in the last 6 months.
    old = [(day, day, day, "tee", "jersey") for day in range(0, 300, 10)]
    new = [(day, day, day, "tee", "jersey") for day in range(560, 700, 10)]
    events = build(old + new)

    cohorts = arrival_cohorts(events, level="product_code")
    renewal = renewal_in_final_window(events, cohorts, level="product_code", months=6)

    assert renewal == 1.0


def test_variant_churn_does_not_inflate_product_level_renewal() -> None:
    """The trap this whole experiment exists to catch.

    One product, sold all period, gains a fresh colour variant every month. Article-level
    renewal looks vigorous; product-level renewal must stay at zero.
    """
    rows = [(day, 1000 + day, 100, "tee", "jersey") for day in range(0, 700, 30)]
    events = build(rows)

    article_cohorts = arrival_cohorts(events, level="article_id")
    product_cohorts = arrival_cohorts(events, level="product_code")

    article_renewal = renewal_in_final_window(
        events, article_cohorts, level="article_id", months=6
    )
    product_renewal = renewal_in_final_window(
        events, product_cohorts, level="product_code", months=6
    )

    assert article_renewal == 1.0
    assert product_renewal == 0.0


def test_transaction_share_weighs_volume_not_item_count() -> None:
    """A long tail of new items with no sales must not count as economic renewal."""
    # One genuinely old product: on sale from day zero, carrying the volume throughout.
    old = [(day, 1, 100, "tee", "jersey") for day in range(0, 700)]
    # Ten new products arrive late but sell once each.
    new = [(650 + i, 200 + i, 200 + i, "tee", "jersey") for i in range(10)]
    events = build(old + new)

    cohorts = arrival_cohorts(events, level="product_code")
    share = new_item_transaction_share(events, cohorts, level="product_code", window_days=90)

    assert 0.0 < share < 0.15


def test_divergence_is_zero_when_arrivals_look_the_same() -> None:
    rows = [(day, day, day, "tee", "jersey") for day in range(0, 700, 5)]
    events = build(rows)

    cohorts = arrival_cohorts(events, level="product_code")
    result = attribute_divergence(events, cohorts, level="product_code", min_cohort_size=5)

    assert result["first_to_last"] == 0.0


def test_divergence_rises_when_the_mix_shifts() -> None:
    # Early arrivals are all jersey tees; later arrivals are all knitwear.
    early = [(day, day, day, "tee", "jersey") for day in range(0, 200, 2)]
    late = [(day, day, day, "jumper", "knitwear") for day in range(400, 600, 2)]
    events = build(early + late)

    cohorts = arrival_cohorts(events, level="product_code")
    result = attribute_divergence(events, cohorts, level="product_code", min_cohort_size=5)

    assert result["first_to_last"] > 0.9
    assert result["trend_slope"] > 0


def test_flagship_viability_depends_only_on_renewal_and_transaction_weight() -> None:
    gates = flagship_gates(product_renewal=0.20, new_item_transaction_share=0.10)

    assert gates == {"A_product_renewal": True, "B_transaction_weight": True}
    assert all(gates.values())


def test_either_failed_gate_makes_the_flagship_infeasible() -> None:
    low_renewal = flagship_gates(product_renewal=0.19, new_item_transaction_share=0.10)
    low_weight = flagship_gates(product_renewal=0.20, new_item_transaction_share=0.09)

    assert not all(low_renewal.values())
    assert not all(low_weight.values())
