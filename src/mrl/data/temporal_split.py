"""Exercise: implement the decision-time split fixed by this module.

The input is one row per recommendation example, not one row per raw purchase. For H&M the
example unit is a customer-day: history contains purchases strictly before the decision day,
and purchases on that day are outcomes. A customer's examples may therefore occur in several
splits without leaking future events into an earlier decision.

Write the tests first. At minimum they should cover examples exactly on each cutoff, unsorted
input, repeated customer IDs across splits, missing decision timestamps, timezone-aware input,
and cutoffs given in the wrong order. The fixed boundary contract is train
``<= train_end``, validation ``(train_end, valid_end]`` and test ``> valid_end``.
"""

from __future__ import annotations

import pandas as pd


def temporal_split(
    examples: pd.DataFrame,
    *,
    decision_timestamp_column: str,
    train_end: pd.Timestamp,
    valid_end: pd.Timestamp,
) -> pd.Series:
    """Return a ``train`` / ``valid`` / ``test`` label for every decision example.

    Args:
        examples: one row per customer-day recommendation decision.
        decision_timestamp_column: column holding the decision time.
        train_end: last timestamp belonging to train.
        valid_end: last timestamp belonging to validation.

    Returns:
        A Series aligned to ``examples.index`` holding the split label.
    """
    raise NotImplementedError("Exercise: implement the temporal split contract")
