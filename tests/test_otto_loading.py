"""Tests for the loading plumbing.

These cover conversion only — that the wire format is read correctly and nothing is
silently dropped. Tests for the temporal split and the metrics are written by the author
as part of Phase 1, against `tests/fixtures/otto_sample.jsonl`.
"""

from pathlib import Path

import polars as pl
import pytest

from mrl.data.otto import fingerprint, iter_raw_events, profile, raw_to_frame, raw_to_parquet

FIXTURE = Path(__file__).parent / "fixtures" / "otto_sample.jsonl"


def test_every_event_survives_flattening() -> None:
    events = list(iter_raw_events(FIXTURE))

    # 4 + 1 + 3 + 2 + 3 + 2, counted by hand from the fixture.
    assert len(events) == 15
    assert {event["session"] for event in events} == {1, 2, 3, 4, 5, 6}


def test_plural_wire_types_are_normalised() -> None:
    types = {event["type"] for event in iter_raw_events(FIXTURE)}

    assert types == {"click", "cart", "order"}


def test_unknown_event_type_is_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    bad.write_text('{"session": 1, "events": [{"aid": 1, "ts": 1, "type": "wishlist"}]}\n')

    with pytest.raises(ValueError, match="unknown OTTO event type"):
        list(iter_raw_events(bad))


def test_frame_keeps_event_order_within_session() -> None:
    frame = raw_to_frame(FIXTURE)
    session_one = frame.filter(pl.col("session") == 1)

    assert session_one["ts"].to_list() == [1000, 1500, 1800, 2400]
    assert session_one["type"].to_list() == ["click", "click", "cart", "order"]


def test_parquet_roundtrip_preserves_every_row(tmp_path: Path) -> None:
    destination = raw_to_parquet(FIXTURE, tmp_path / "events.parquet")
    reloaded = pl.read_parquet(destination)

    assert reloaded.height == raw_to_frame(FIXTURE).height
    assert reloaded.sort(["session", "ts"]).equals(raw_to_frame(FIXTURE).sort(["session", "ts"]))


def test_profile_reports_the_shape_used_to_pick_cutoffs(tmp_path: Path) -> None:
    destination = raw_to_parquet(FIXTURE, tmp_path / "events.parquet")
    stats = profile(pl.scan_parquet(destination))

    assert stats["n_events"] == 15
    assert stats["n_sessions"] == 6
    assert stats["ts_min"] == 1000
    assert stats["ts_max"] == 3300
    # Two orders: session 1 (aid 101) and session 5 (aid 500).
    assert stats["n_order"] == 2


def test_fingerprint_changes_when_data_changes(tmp_path: Path) -> None:
    first = tmp_path / "a.jsonl"
    second = tmp_path / "b.jsonl"
    first.write_text('{"session": 1, "events": [{"aid": 1, "ts": 1, "type": "clicks"}]}\n')
    second.write_text('{"session": 1, "events": [{"aid": 2, "ts": 1, "type": "clicks"}]}\n')

    assert fingerprint(first) != fingerprint(second)
    assert fingerprint(first) == fingerprint(first)
