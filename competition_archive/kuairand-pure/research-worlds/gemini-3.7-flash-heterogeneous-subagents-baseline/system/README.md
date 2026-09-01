# `gemini-3.7-flash` heterogeneous-subagent system interface

Python API:

```python
from system import run_popularity_baseline, smoke_result

print(smoke_result())
print(run_popularity_baseline("competition_data/data", split="valid"))
```

CLI:

```bash
python -m system.cli smoke
python -m system.cli evaluate-pop --data-dir competition_data/data --split valid
```

The smoke command uses a tiny synthetic dataset and does not require local
KuaiRand data. `evaluate-pop` expects the hidden-test-free local development
view under `competition_data/data` or an explicitly supplied equivalent.
