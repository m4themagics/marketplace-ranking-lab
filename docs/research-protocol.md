# Research protocol

Правила, которым должен удовлетворять результат, чтобы попасть в README или в `reports/`.
Один эксперимент из `experiments/` — одно заполнение этого checklist. Пустые поля
заполняются **до** итогового прогона, а не после того, как число уже увидено.

## Preregistration

```text
Research question:
Expected mechanism:
Population and unit of observation:
Baseline:
Treatment:
Primary metric:
Correctness gates:
Expected failure modes:
Stopping rule:
```

## Data contract

- У каждого решения есть timestamp.
- Behavioral feature использует только события строго раньше timestamp решения.
- Train/validation/test разделяются до подбора модели.
- Dataset revision, sampling rule, seed и fingerprint сохраняются.
- Исключения и пропуски считаются и публикуются.

## Evaluation contract

- Candidate generation и ranking оцениваются отдельно.
- Policies получают одинаковую population и совместимые candidate pools.
- Видимый output явно определён.
- Infeasibility не маскируется fallback-строками.
- Per-example outcomes сохраняются для paired analysis.
- Вместе с conditional metric публикуется coverage.

## Uncertainty

До прогона выбрать независимую или кластерную единицу bootstrap, число repetitions и seed.
Публиковать effect size и interval. Если interval включает ноль, результат не называется
улучшением или ухудшением.

## Reproducibility

Каждый run сохраняет commit, environment/lock revision, config snapshot, exact command,
seed, input fingerprint и output paths. Clean-checkout smoke run — обязательный gate.

## Publication gate

Finding появляется в README только когда:

- correctness tests проходят;
- protocol не был молча изменён после просмотра числа;
- uncertainty рассчитана;
- ручные примеры разобраны;
- автор может провести teach-back без чтения кода.
