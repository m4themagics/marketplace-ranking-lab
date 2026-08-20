# Fixtures

`otto_sample.jsonl` — six sessions in the raw OTTO wire format, retained only to test the
fallback loader. It is not the fixture for H&M customer-day split or ranking metrics.

It survives until the OTTO loader is removed after the first reproducible H&M run. H&M
customer-day fixtures are authored with the split and metric exercises.

It is built so that the awkward cases are already present:

| Session | Why it is here |
|---|---|
| 1 | full click → cart → order funnel on one item |
| 2 | single event, no next item to predict |
| 3 | click and cart on the same item at the **same timestamp** — forces a tie rule |
| 4 | **straddles ts=2400**: starts before, ends after; the split decision shows up here |
| 5 | the **same item twice at the same timestamp**, then an order — forces a duplicate rule |
| 6 | starts after every plausible cutoff — a session that is pure test data |

Item 100 appears in sessions 1, 3 and 5, so co-visitation counts are non-trivial but
still countable on paper.

These cases document the old wire format only; no new model test should depend on it.
