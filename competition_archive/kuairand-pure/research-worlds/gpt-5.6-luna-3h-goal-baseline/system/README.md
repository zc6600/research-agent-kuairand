# `gpt-5.6-luna` direct-control system interface

Python API:

```python
from system import run_optimized_ranker, run_popularity_baseline, smoke_result

print(smoke_result())
print(run_popularity_baseline("competition_data/data", split="valid"))
print(run_optimized_ranker("competition_data/data", split="valid"))
```

CLI:

```bash
python -m system.cli smoke
python -m system.cli evaluate-pop --data-dir competition_data/data --split valid
python -m system.cli evaluate-fm --data-dir competition_data/data --split valid
```

The smoke command uses a tiny synthetic dataset and does not require local
KuaiRand data. `evaluate-pop` and `evaluate-fm` expect the hidden-test-free local development
view under `competition_data/data` or an explicitly supplied equivalent.
