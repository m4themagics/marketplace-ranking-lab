# Задание 02 — ranking metrics как ручные контракты

**Бюджет:** два вечера, 4–5 ч. **Фаза:** недели 2–3.
**Код:** функции в `src/mrl/evaluation/metrics.py` — stubs.

## До реализации

На одном списке из пяти items руками посчитать DCG, NDCG@3, Recall@3, MRR@3 и вклад в catalog
coverage. До первой строки implementation отдельно зафиксировать:

- `k <= 0` и `k` больше длины списка;
- duplicate predictions;
- запрос без relevant items;
- отрицательные gains;
- tie rule до формирования `ranked_item_ids`.

Эти решения становятся частью evaluation contract и после первого модельного результата не
меняются молча.

## Falsifying tests

1. Graded relevance меняет NDCG, но не binary Recall.
2. Relevant item на первой и на последней доступной позиции даёт разные MRR.
3. Перестановка двух items с разными gains меняет DCG в правильную сторону.
4. Duplicate policy ловит tempting implementation через `set`.
5. Empty-relevance policy не позволяет агрегатору незаметно изменить population.
6. Catalog coverage считает уникальные items по всем top-K, а не среднее per-list coverage.

## Gate

Каждая функция проходит ручной пример, boundary tests и failure-mode test. Автор объясняет,
почему candidate Recall@K и final-list Recall@K отвечают на разные вопросы.
