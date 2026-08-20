RAW ?= data/raw/train.jsonl.gz
PROCESSED ?= data/processed/events.parquet

.PHONY: install test lint data profile check fetch-hm viability

install:
	uv sync --extra dev --extra data --extra neural

test:
	uv run pytest

lint:
	uv run ruff check .

check: lint test

## Convert raw OTTO JSONL into columnar Parquet.
## Override the source with: make data RAW=data/raw/test.jsonl.gz
data:
	uv run python -c "from pathlib import Path; from mrl.data.otto import raw_to_parquet; \
	print(raw_to_parquet(Path('$(RAW)'), Path('$(PROCESSED)')))"

## Print dataset shape and its fingerprint. Run before choosing split cutoffs.
profile:
	uv run python -c "from pathlib import Path; from mrl.data.otto import scan_events, profile, fingerprint; \
	p = Path('$(PROCESSED)'); \
	[print(f'{k}: {v}') for k, v in profile(scan_events(p)).items()]; \
	print('fingerprint:', fingerprint(p))"

HM_COMP ?= h-and-m-personalized-fashion-recommendations

## Fetch the two H&M files the viability test needs (~3.5 GB).
## Requires a Kaggle token in ~/.kaggle/access_token and the competition rules accepted:
## https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/rules
fetch-hm:
	mkdir -p data/raw
	uv run --extra data kaggle competitions download -c $(HM_COMP) -f articles.csv -p data/raw
	uv run --extra data kaggle competitions download -c $(HM_COMP) -f transactions_train.csv -p data/raw
	unzip -o data/raw/articles.csv.zip -d data/raw
	unzip -o data/raw/transactions_train.csv.zip -d data/raw
	rm -f data/raw/articles.csv.zip data/raw/transactions_train.csv.zip
	ls -la data/raw

## Run the preregistered dataset kill-test.
viability:
	uv run python experiments/00_dataset_viability/run.py --data data/raw
