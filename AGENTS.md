# Working context for agents

Read this before touching anything. `CLAUDE.md` is a symlink to this file, so every tool
lands here regardless of which convention it follows.

Retrieval and ranking experiments on a real fashion catalogue. Read [README.md](README.md)
for what the lab is and [docs/development-plan.md](docs/development-plan.md) for the order of
work and the reasoning behind it.

## The one rule that overrides default behaviour

This repository exists to build a skill, not to accumulate code. **Do not implement the core
exercises.** Modules that raise `NotImplementedError` with an "exercise" message are the
author's to write — `evaluation/metrics.py`, `data/temporal_split.py`,
`permutation_null_band` in `data/viability.py`, and any later stub in the same idiom.

Default mode for those: ask leading questions, give one hint at a time, review an attempt,
check a test without fixing the implementation under it. A finished implementation is written
only when the author asks for it in a separate, explicit decision after their own attempt.
Full contract in [LEARNING.md](LEARNING.md).

Mechanical work is fair game without ceremony: plumbing, config, CI, refactors, docs, fetch
scripts, test scaffolding the author asked for.

If you are unsure whether something is a core exercise, it is: ask before implementing it.

## How work is done here

- **Falsifying test first.** For every core TODO: hand-computed example → failing test → run
  it and record the failure → minimum implementation → boundary and failure-mode tests.
- **Preregistration is binding.** Thresholds and criteria in an experiment's README are fixed
  before the numbers are seen. If a criterion needs to change, change it before the run and
  say so in the commit — never after.
- **Every result carries** the command, the seed, the commit, and the input fingerprint.
- **Uncertainty before conclusions.** Bootstrap by user, not by event. An interval that
  includes zero is not an improvement.

## Conventions

- Docs and commit bodies in Russian; code, docstrings and commit subjects in English.
- Docstrings explain the decision and the failure mode, not the syntax.
- Commit subjects: `feat:`, `docs:`, `chore:`, lowercase, no trailing period.
- `uv` for everything. `make check` = ruff + pytest, and it must be green before a push.
- Raw data is never committed; `*.local.md` is never committed. A `*.local.md` file present
  on disk is private working context — read it, never quote it into a tracked file.

## State

The dataset kill-test ([experiment 00](experiments/00_dataset_viability/README.md)) is written
and waiting on data — nothing downstream starts until it passes. `make fetch-hm` pulls the two
H&M files; it needs a Kaggle token in `~/.kaggle/access_token` and the competition rules
accepted on the site.

`src/mrl/data/otto.py` and `configs/otto.yaml` are held for the fallback dataset and get
deleted once H&M is committed to.
