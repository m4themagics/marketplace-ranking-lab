# Marketplace Ranking Lab

[![ci](https://github.com/m4themagics/marketplace-ranking-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/m4themagics/marketplace-ranking-lab/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.12-blue)](pyproject.toml)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Retrieval and ranking experiments on a real fashion catalogue, each one answering a question
that has a number for an answer.

The classical two-stage recommender — ALS candidates, gradient-boosted ranker on top — is the
baseline, not the achievement: it is what the author already runs in production. What gets
built here is what production does not have: a neural retriever measured against that
baseline, an ANN index measured against exact search, an explicit relevance/value proxy
trade-off curve, and finally the question the lab is named for.

> **Flagship question.** How well does a fixed content codebook generalise to future item
> cohorts under temporal distribution shift — and when does rebuilding it start to pay for
> itself?

That one is last, not first. Everything before it closes a gap that comes up in interviews;
it is the one that would be worth writing up.

## Status

**Nothing is trained yet.** H&M is downloaded locally and fixed for experiments 01–04; its
viability for the post-week-12 flagship remains unmeasured. Raw data is never committed.
The honest state, updated as it changes:

| | What | State |
|---|---|---|
| 00 | Does the catalogue turn over enough to support the flagship? | data fetched; central permutation exercise pending |
| — | Temporal split, metrics, ALS + LambdaRank baseline | not started |
| 01 | What logged basket value is captured as relevance changes? | design fixed, not started |
| 02 | What does a two-tower add over ALS retrieval? | not started |
| 03 | What does exact → ANN cost in recall, latency, memory? | not started |
| 04 | Where do exposure and position bias enter the system? | not started |

Order and reasoning: [development plan](docs/development-plan.md). Experiment 00 is a
kill-test for the post-week-12 codebook work. If catalogue renewal is too weak, experiments
01–04 still run on H&M, while 05–06 remain closed rather than having their premise softened.

## What exists today

- [`data/viability.py`](src/mrl/data/viability.py) — catalogue turnover measured at both
  `article_id` and `product_code` level, because H&M has roughly twice as many articles as
  products and a new colour of an old product is not an arrival;
- [`contracts.py`](src/mrl/contracts.py) — H&M customer-day types every later model has to
  respect: a decision happens on a date, and only strictly earlier purchases may produce it;
- [`experiments/00_dataset_viability/`](experiments/00_dataset_viability/) — the kill-test,
  one command, preregistered criteria;
- tests on synthetic frames with known turnover, including the trap the experiment exists to
  catch: variant churn must not show up as catalogue renewal.

Ranking metrics and the temporal split are stubs with the exercise written into their
docstrings — see [LEARNING.md](LEARNING.md) for why they are stubs and not generated code.

## Data

[H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations)
— the working dataset for experiments 01–04: real purchase transactions over roughly two
years, with product images, text attributes, and a price on every transaction. Experiment 00
decides only whether it also supports the later codebook-drift question.

Fashion is the promising domain on the argument that its catalogues renew quickly. That is a
hypothesis about the data, not a property of it, which is what experiment 00 is for.

The limitation, stated here and in every report: no public dataset publishes the date an item
entered the catalogue. First-transaction time is a proxy, and it biases arrival late for
slow-selling items.

Raw data is never committed; `data/` holds loading scripts and fingerprints only.

## Run

```bash
make install                        # dev + data + neural environments
make check                          # ruff + pytest
uv run python experiments/00_dataset_viability/run.py --data data/raw
```

Every result carries the command that produced it, its seed, and the fingerprint of its input.

## How this repository is meant to be read

- **One split, one evaluation core.** Every model is scored the same way, so the deltas
  between rows mean something.
- **Candidate recall and ranking quality are measured separately.** A retrieval failure and a
  ranking failure are different bugs with different fixes.
- **Leakage tests are adversarial.** The split test is written to fail against a deliberately
  broken implementation first; a test that only ever passes proves nothing.
- **Baselines are not straw.** The neural retriever is compared against a tuned ALS +
  LambdaRank stack, not against popularity.
- **Negative results are kept.** Where the neural model loses, that is reported.
- **Collision accounting is not optional.** Semantic-ID metrics are computed at item level,
  never at SID level: matching a predicted SID against the target counts a hit for any
  colliding item, and recent work finds Hit@10 inflated by as much as 103% that way.

## Documents

- [Development plan](docs/development-plan.md) — which gap each experiment closes, and why in
  that order.
- [Research protocol](docs/research-protocol.md) — what a number has to satisfy to be reported.
- [PyTorch learning track](docs/learning-tracks/pytorch.md) — the ladder the neural work rests on.
- [Learning contract](LEARNING.md) — how this codebase is authored, and where AI assistance
  stops.
