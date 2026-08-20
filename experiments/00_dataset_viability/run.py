"""Dataset viability test: does the catalogue turn over enough to strain a fixed codebook?

Preregistered criteria live in this directory's README and are not to be edited after the
numbers are seen. See :mod:`mrl.data.viability` for the measurements themselves.

Usage::

    uv run python experiments/00_dataset_viability/run.py --data data/raw
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

import polars as pl

from mrl.data.viability import (
    PASS_C_MIN_DIVERGENCE,
    arrival_cohorts,
    attribute_divergence,
    flagship_gates,
    new_item_transaction_share,
    permutation_null_band,
    renewal_in_final_window,
)


def _fingerprint(path: Path, *, chunk_bytes: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def _commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/raw"))
    parser.add_argument("--out", type=Path, default=Path("reports/00_dataset_viability.json"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--n-permutations", type=int, default=200)
    parser.add_argument("--min-cohort-size", type=int, default=50)
    args = parser.parse_args()

    transactions_path = args.data / "transactions_train.csv"
    articles_path = args.data / "articles.csv"

    transactions = pl.scan_csv(
        transactions_path, try_parse_dates=True
    ).select("t_dat", "article_id")
    articles = pl.scan_csv(articles_path).select(
        "article_id", "product_code", "product_type_name", "garment_group_name"
    )

    events = transactions.join(articles, on="article_id", how="left")

    report: dict[str, object] = {
        "run": {
            "command": shlex.join([sys.executable, *sys.argv]),
            "commit": _commit(),
            "seed": args.seed,
            "config": {
                "n_permutations": args.n_permutations,
                "min_cohort_size": args.min_cohort_size,
            },
            "input_fingerprints": {
                transactions_path.name: _fingerprint(transactions_path),
                articles_path.name: _fingerprint(articles_path),
            },
        }
    }

    for level in ("article_id", "product_code"):
        cohorts = arrival_cohorts(events, level=level)
        renewal = renewal_in_final_window(events, cohorts, level=level, months=6)
        share = new_item_transaction_share(events, cohorts, level=level, window_days=90)
        report[level] = {
            "n_items": cohorts.height,
            "arrivals_per_month": cohorts.group_by("cohort")
            .agg(pl.len().alias("n"))
            .sort("cohort")
            .to_dicts(),
            "renewal_final_6m": renewal,
            "new_item_transaction_share_final_quarter": share,
        }

    product_cohorts = arrival_cohorts(events, level="product_code")
    divergence = attribute_divergence(
        events,
        product_cohorts,
        level="product_code",
        min_cohort_size=args.min_cohort_size,
    )
    null_band = permutation_null_band(
        events,
        product_cohorts,
        level="product_code",
        n_permutations=args.n_permutations,
        seed=args.seed,
        min_cohort_size=args.min_cohort_size,
    )
    report["measurements"] = {
        "C_content_shift": {
            "orientation_mark": PASS_C_MIN_DIVERGENCE,
            "observed": divergence,
            "null_band": null_band,
        }
    }

    product = report["product_code"]
    if not isinstance(product, dict):
        raise TypeError("product-level report must be a mapping")
    gates = flagship_gates(
        product_renewal=float(product["renewal_final_6m"]),
        new_item_transaction_share=float(
            product["new_item_transaction_share_final_quarter"]
        ),
    )
    report["gates"] = gates
    report["flagship_viable"] = all(gates.values())

    # The diagnostic that separates real arrivals from colour-variant churn.
    article = report["article_id"]
    if not isinstance(article, dict):
        raise TypeError("article-level report must be a mapping")
    article_renewal = float(article["renewal_final_6m"])
    product_renewal = float(product["renewal_final_6m"])
    report["variant_inflation_ratio"] = (
        article_renewal / product_renewal if product_renewal else None
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, default=str))

    print(f"flagship viable: {report['flagship_viable']}")
    for name, passed in gates.items():
        print(f"  {'pass' if passed else 'FAIL'}  {name}")
    print("  measured  C_content_shift (not a gate)")
    print(f"  variant inflation (article renewal / product renewal): "
          f"{report['variant_inflation_ratio']}")
    print(f"\nfull report: {args.out}")

    return 0 if report["flagship_viable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
