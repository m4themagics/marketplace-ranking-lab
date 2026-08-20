"""Exercise: implement ranking metrics from their definitions.

No library wrappers. Every function here must be checkable by hand on a five-item example,
because the whole project rests on these numbers being right.

Before implementing, decide and write down: how ties are broken, how duplicate predictions
are treated, and what a metric returns when a session has no relevant items at all. Those
three choices move reported numbers more than most modelling decisions.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def dcg(gains: Sequence[float]) -> float:
    """Discounted cumulative gain of an ordered list of gains."""
    raise NotImplementedError("Exercise: implement DCG")


def ndcg_at_k(
    ranked_item_ids: Sequence[int],
    relevance: Mapping[int, float],
    k: int,
) -> float:
    """NDCG@k for graded relevance (click / cart / order weigh differently)."""
    raise NotImplementedError("Exercise: implement NDCG@k")


def recall_at_k(
    ranked_item_ids: Sequence[int],
    relevant_item_ids: Sequence[int],
    k: int,
) -> float:
    """Recall@k: share of relevant items retrieved in the top k."""
    raise NotImplementedError("Exercise: implement Recall@k")


def mrr_at_k(
    ranked_item_ids: Sequence[int],
    relevant_item_ids: Sequence[int],
    k: int,
) -> float:
    """Mean reciprocal rank of the first relevant item within the top k."""
    raise NotImplementedError("Exercise: implement MRR@k")


def catalog_coverage(
    ranked_lists: Sequence[Sequence[int]],
    catalog_size: int,
    k: int,
) -> float:
    """Share of the catalog that appears in any top-k list.

    A diversity metric, not a quality metric: it is the cheapest way to notice that a
    model has quietly collapsed onto the head of the catalog.
    """
    raise NotImplementedError("Exercise: implement catalog coverage")
