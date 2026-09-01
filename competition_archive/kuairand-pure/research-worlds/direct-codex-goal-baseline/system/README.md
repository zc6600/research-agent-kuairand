# Direct Codex Agent system interface

Python API:

```python
from system import (
    run_fm_baseline,
    run_fm_pairwise_baseline,
    run_popularity_baseline,
    smoke_result,
)

print(smoke_result())
print(run_popularity_baseline("competition_data/data", split="valid"))
print(run_fm_baseline("competition_data/data", split="valid"))
print(run_fm_pairwise_baseline("competition_data/data", split="valid"))
```

The current candidate also exposes `run_fm_pairwise_baseline` and
`fm_pairwise_scores`, which train the same five fields with sampled
within-user positive/negative pairs. Their defaults are the current best
public-validation setting (`factors=8`, `learning_rate=0.00025`).
The pairwise command accepts train-only explicit crosses such as
`--extra-field user_tab` for experiments.

CLI:

```bash
python -m system.cli smoke
python -m system.cli evaluate-pop --data-dir competition_data/data --split valid
python -m system.cli evaluate-fm --data-dir competition_data/data --split valid
python -m system.cli evaluate-fm-pairwise --data-dir competition_data/data --split valid
```

The smoke command uses a tiny synthetic dataset and does not require local
KuaiRand data. `evaluate-pop` is the item-popularity control. `evaluate-fm`
is the stronger official five-field Factorization Machine and selects its
checkpoint using public validation only. Both data commands expect the
hidden-test-free local development view under `competition_data/data` or an
explicitly supplied equivalent.
