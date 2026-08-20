"""Smoke test: the package is importable and the H&M contracts hold their shape.

Real tests for the temporal split and the ranking metrics are written by the author
before those functions are implemented — see LEARNING.md.
"""

from mrl import PROJECT_STATUS
from datetime import date

import pytest

from mrl.contracts import PurchaseEvent, RecommendationContext, ScoredItem


def test_package_imports() -> None:
    assert PROJECT_STATUS == "00-dataset-viability"


def test_recommendation_context_only_holds_past_purchases() -> None:
    history = (
        PurchaseEvent(
            customer_id="customer-1", item_id=100, timestamp=date(2020, 1, 1), price=0.1
        ),
        PurchaseEvent(
            customer_id="customer-1", item_id=101, timestamp=date(2020, 1, 2), price=0.2
        ),
    )
    context = RecommendationContext(
        customer_id="customer-1", decision_timestamp=date(2020, 1, 3), history=history
    )

    assert all(event.timestamp < context.decision_timestamp for event in context.history)
    assert context.history[-1].item_id == 101


def test_recommendation_context_rejects_same_day_outcomes_as_history() -> None:
    leaked = PurchaseEvent(
        customer_id="customer-1", item_id=100, timestamp=date(2020, 1, 3), price=0.1
    )

    with pytest.raises(ValueError, match="strictly earlier"):
        RecommendationContext(
            customer_id="customer-1",
            decision_timestamp=date(2020, 1, 3),
            history=(leaked,),
        )


def test_scored_item_is_comparable_by_score() -> None:
    ranked = sorted(
        [ScoredItem(item_id=7, score=0.1), ScoredItem(item_id=9, score=0.9)],
        key=lambda item: item.score,
        reverse=True,
    )

    assert [item.item_id for item in ranked] == [9, 7]
