# PyTorch learning track

Этот трек даёт технические prerequisites для neural policies. Он не является отдельным
research study: сначала здесь осваивается инструмент, затем в Experiment 02 с его помощью
проверяется гипотеза про Two-Tower retrieval.

Не переходить к следующему модулю, пока текущий пример нельзя объяснить без подсказки.
Готовых training loops в репозитории намеренно нет.

## Module 0 — Setup and experiment discipline

Цель: создать изолированный playground, не затрагивая основной pipeline.

- [ ] Установить `uv sync --extra dev --extra neural`.
- [ ] Создать `playground/pytorch/`, когда начнётся работа над треком.
- [ ] Зафиксировать seed для Python, NumPy и PyTorch.
- [ ] Научиться выводить версию PyTorch, доступное device и dtype.
- [ ] Для каждого упражнения записывать shapes входов и выходов.

Gate: среда воспроизводится, а автор может объяснить различие CPU, CUDA и MPS без
обещания, что вычисления автоматически попадают на ускоритель.

## Module 1 — Tensors and shapes

Темы:

- создание tensor, `dtype`, `device`, `shape`;
- indexing и slicing;
- `reshape`, `view`, `squeeze`, `unsqueeze`;
- broadcasting;
- reductions;
- matrix multiplication.

Упражнения:

1. Повторить на tensor несколько операций NumPy и проверить формы.
2. Посчитать вручную и через PyTorch dot-product user/item embeddings.
3. Одновременно посчитать scores одного user для нескольких items.
4. Написать assertions, которые ловят перепутанные batch и embedding dimensions.
5. Специально создать ошибку broadcasting и объяснить её.

Gate: до запуска кода автор предсказывает shape результата каждого выражения.

## Module 2 — Autograd from first principles

Темы:

- `requires_grad`;
- computational graph;
- scalar loss;
- `backward()` и `.grad`;
- накопление gradients;
- `torch.no_grad()` и `detach()`.

Упражнения:

1. Взять скалярную функцию, вывести derivative руками и сравнить с autograd.
2. Реализовать линейную регрессию без `nn.Module` и без optimizer.
3. Написать вручную шаг gradient descent.
4. Показать баг от забытых zero gradients.
5. Сравнить analytical и numerical gradient на маленьком примере.

Gate: автор может объяснить, почему gradients накапливаются и почему update параметров не
должен строить новый computational graph.

## Module 3 — Modules, losses and optimizers

Темы:

- `nn.Module`, parameters и `forward`;
- `nn.Linear`;
- loss functions;
- `torch.optim.SGD` и Adam;
- `train()` / `eval()`;
- `state_dict`.

Упражнения:

1. Переписать линейную регрессию через `nn.Module`.
2. Самостоятельно написать полный training loop.
3. Переобучить модель на 20–30 примерах почти до нулевого loss.
4. Сохранить `state_dict`, загрузить его и проверить одинаковые predictions.
5. Добавить один намеренный train/eval bug и тест, который его ловит.

Gate: tiny-batch overfit работает, loss действительно уменьшается, save/load проверен
тестом.

## Module 4 — Dataset, DataLoader and validation

Темы:

- собственный `Dataset`;
- batching, shuffle и `DataLoader`;
- train/validation split;
- collate и variable-length inputs;
- отсутствие leakage между splits.

Упражнения:

1. Собрать Dataset из маленькой таблицы взаимодействий.
2. Проверить shapes и dtypes одного batch.
3. Написать train и evaluation loops с разными режимами модели.
4. Доказать тестом, что validation rows не используются для fit.
5. Проверить воспроизводимость порядка batches при фиксированном seed.

Gate: обучение и validation разделены, а код корректно обрабатывает последний неполный
batch.

## Module 5 — Embeddings and matrix factorization

Это первый RecSys-мост, но ещё не Experiment 02.

Темы:

- `nn.Embedding`;
- user/item ID mapping;
- dot-product scoring;
- positive и negative pairs;
- `BCEWithLogitsLoss`;
- recommendation evaluation.

Упражнения:

1. Создать маленькую synthetic user–item matrix с понятными предпочтениями.
2. Реализовать user и item embeddings.
3. Определить negative-sampling contract и проверить его тестами.
4. Обучить dot-product matrix factorization.
5. Сравнить Recall@K с popularity baseline.
6. Исключить train interactions из recommendation candidates.
7. Проверить cold user/item behavior.

Gate: модель переобучает tiny dataset, но оценивается на held-out interactions; автор
объясняет, почему случайный negative sampling может давать слишком лёгкую задачу.

## Module 6 — Retrieval-ready PyTorch

Темы:

- batch matrix multiplication;
- cosine versus dot-product similarity;
- normalized embeddings;
- in-batch negatives;
- contrastive loss;
- exact top-k retrieval.

Упражнения:

1. Векторизовать scoring без Python-loop по items.
2. Построить similarity matrix batch users × batch items.
3. Реализовать учебный contrastive objective по собственному псевдокоду.
4. Сравнить exact top-k с ручным ranking на маленьком наборе.
5. Исследовать, как normalization меняет ranking и scale logits.

Gate: автор объясняет каждый axis similarity matrix и может вывести target labels для
in-batch negatives.

## Module 7 — Two-Tower readiness gate

До начала Experiment 02 автор должен уметь:

- написать training/evaluation loop без копирования готового trainer;
- диагностировать shapes, NaN loss и отсутствие gradients;
- overfit one batch;
- сохранить и загрузить embeddings/model state;
- объяснить negative sampling и false negatives;
- посчитать exact Recall@K;
- отделить model training от ANN serving.

После прохождения gate открывается
[Experiment 02 — Neural retrieval](../../experiments/02_neural_retrieval/README.md).

## Чего нет в этом треке

Не «никогда», а «не сейчас» — каждый пункт приходит на своём месте
[плана разработки](../development-plan.md):

- SASRec и трансформеры — Could, после эксперимента 02;
- FAISS и ANN — эксперимент 03, но только после корректного exact top-k;
- Semantic IDs — эксперименты 05 и 06; генеративный retrieval — Could;
- ONNX, Triton и serving — в проекте нет намеренно;
- DDP — в проекте нет намеренно.

Не приходит никогда:

- Lightning и высокоуровневые trainers — они скрывают ровно то, что нужно уметь показать;
- AMP как способ «ускорить всё» до появления измеренного bottleneck.

## Teach-back questions

1. Чем parameter отличается от обычного tensor?
2. Почему loss обычно scalar перед `backward()`?
3. Когда нужен `model.eval()` и почему его недостаточно без `no_grad()`?
4. Почему tiny-batch overfit является проверкой корректности?
5. Чем `Embedding` отличается от one-hot vector followed by Linear?
6. Что является negative example в implicit-feedback RecSys?
7. Почему in-batch negative иногда на самом деле relevant item?
8. Чем exact retrieval отличается от ANN и почему сначала проверяется exact?
