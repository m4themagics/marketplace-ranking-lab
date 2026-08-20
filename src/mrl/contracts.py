"""Shared H&M types for candidate generators and rankers.

Two ideas are fixed from the start and every later model must respect them:

1. Every decision happens at a point in time, and only events strictly before that time
   may be used to produce it.
2. H&M exposes purchases but not impressions, so a purchase is an observed outcome rather
   than evidence that every unpurchased candidate was shown and rejected.

Nothing here implements a ranking algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, Sequence


@dataclass(frozen=True)
class PurchaseEvent:
    """One observed H&M purchase used as history or a logged outcome."""

    customer_id: str
    item_id: int
    timestamp: date
    price: float


@dataclass(frozen=True)
class RecommendationContext:
    """Everything a policy is allowed to see when it makes one decision.

    ``history`` must contain only events with ``timestamp < decision_timestamp``.
    Purchases on ``decision_timestamp`` are outcomes, never input features.
    """

    customer_id: str
    decision_timestamp: date
    history: tuple[PurchaseEvent, ...]

    def __post_init__(self) -> None:
        if any(event.customer_id != self.customer_id for event in self.history):
            raise ValueError("history contains a purchase from another customer")
        if any(event.timestamp >= self.decision_timestamp for event in self.history):
            raise ValueError("history must be strictly earlier than the decision")


@dataclass(frozen=True)
class ScoredItem:
    item_id: int
    score: float


class RecommendationPolicy(Protocol):
    """Minimal interface shared by every baseline and model in this repository.

    Candidate generation and ranking are deliberately separate: a policy receives the
    candidate pool it must order, so that candidate recall and ranking quality can be
    measured independently of each other.
    """

    def rank(
        self,
        context: RecommendationContext,
        candidate_item_ids: Sequence[int],
        k: int,
    ) -> Sequence[ScoredItem]: ...
