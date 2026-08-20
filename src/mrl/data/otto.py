"""Loading and conversion for the OTTO dataset.

Raw OTTO ships as gzipped JSONL, one session per line::

    {"session": 12899779, "events": [{"aid": 59625, "ts": 1661724000278, "type": "clicks"}]}

That shape is convenient to distribute and useless to compute on: every question worth
asking is columnar. So the first thing this module does is flatten sessions into one row
per event and write Parquet partitioned by day.

This is plumbing, not an exercise. The exercises are :func:`mrl.data.temporal_split` and
the metrics — those stay unimplemented on purpose.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

import polars as pl

OttoEventType = Literal["click", "cart", "order"]

#: OTTO writes plural event names; the rest of the codebase uses the singular form
#: while this fallback loader remains self-contained.
EVENT_TYPE_MAP: dict[str, OttoEventType] = {
    "clicks": "click",
    "carts": "cart",
    "orders": "order",
}

EVENT_SCHEMA = {
    "session": pl.Int32,
    "aid": pl.Int32,
    "ts": pl.Int64,
    "type": pl.Enum(["click", "cart", "order"]),
}


def iter_raw_events(path: Path) -> Iterator[dict]:
    """Yield one flat event dict per interaction from a raw OTTO JSONL file.

    Handles both ``.jsonl`` and ``.jsonl.gz``. Streams line by line: the full file does
    not fit in memory comfortably, and materialising it defeats the point.
    """
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            session = record["session"]
            for event in record["events"]:
                raw_type = event["type"]
                if raw_type not in EVENT_TYPE_MAP:
                    raise ValueError(f"unknown OTTO event type: {raw_type!r}")
                yield {
                    "session": session,
                    "aid": event["aid"],
                    "ts": event["ts"],
                    "type": EVENT_TYPE_MAP[raw_type],
                }


def raw_to_frame(path: Path) -> pl.DataFrame:
    """Read one raw OTTO file into a flat, typed event frame."""
    rows = list(iter_raw_events(path))
    if not rows:
        return pl.DataFrame(schema=EVENT_SCHEMA)
    return pl.DataFrame(rows, schema=EVENT_SCHEMA)


def raw_to_parquet(
    source: Path,
    destination: Path,
    *,
    chunk_sessions: int = 250_000,
) -> Path:
    """Convert a raw OTTO JSONL file into Parquet, streaming in session chunks.

    Args:
        source: raw ``.jsonl`` or ``.jsonl.gz`` file.
        destination: output ``.parquet`` file.
        chunk_sessions: how many sessions to buffer before writing a row group.

    Returns:
        The destination path.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)

    frames: list[pl.DataFrame] = []
    buffer: list[dict] = []
    seen_sessions = 0
    current_session: int | None = None

    for event in iter_raw_events(source):
        if event["session"] != current_session:
            current_session = event["session"]
            seen_sessions += 1
            if seen_sessions % chunk_sessions == 0:
                frames.append(pl.DataFrame(buffer, schema=EVENT_SCHEMA))
                buffer = []
        buffer.append(event)

    if buffer:
        frames.append(pl.DataFrame(buffer, schema=EVENT_SCHEMA))

    table = pl.concat(frames) if frames else pl.DataFrame(schema=EVENT_SCHEMA)
    table.write_parquet(destination)
    return destination


def scan_events(path: Path) -> pl.LazyFrame:
    """Open converted events lazily, so aggregates never materialise the whole table."""
    return pl.scan_parquet(path)


def profile(events: pl.LazyFrame) -> dict[str, int | float]:
    """Basic shape of the dataset. Run this before choosing split cutoffs.

    Deliberately small: the numbers here are the ones needed to argue that a cutoff is
    reasonable, not a full EDA.
    """
    stats = events.select(
        n_events=pl.len(),
        n_sessions=pl.col("session").n_unique(),
        n_items=pl.col("aid").n_unique(),
        ts_min=pl.col("ts").min(),
        ts_max=pl.col("ts").max(),
    ).collect()

    by_type = (
        events.group_by("type").agg(pl.len().alias("n")).collect().to_dicts()
    )

    result: dict[str, int | float] = stats.to_dicts()[0]
    for row in by_type:
        result[f"n_{row['type']}"] = row["n"]
    result["events_per_session"] = result["n_events"] / max(result["n_sessions"], 1)
    return result


def fingerprint(path: Path, *, chunk_bytes: int = 1 << 20) -> str:
    """SHA-256 of a data file, recorded next to every result.

    A number without the fingerprint of the data it came from is not reproducible, only
    plausible.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()
