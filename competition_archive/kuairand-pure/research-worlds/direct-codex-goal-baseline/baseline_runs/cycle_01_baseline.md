# Cycle 1 — official FM checkpoint

- Hypothesis: establish a faithful single-agent starting point before changing
  the task model.
- Command: `.venv/bin/python -m system.cli evaluate-fm --data-dir competition_data/data --split valid --factors 16 --learning-rate 0.001 --epochs 40 --batch-size 8192 --patience 4 --seed 0`
- Metrics: GAUC `0.6671326322`, nDCG@5 `0.5358048805`, primary `0.6014687564`.
- Decision: valid baseline established; it matches the published validation
  reference within rounding and is the current checkpoint.
- Next action: test a ranking-aligned within-user pairwise loss.

# Controls

- `evaluate-pop --prior 20`: GAUC `0.6387257649`, nDCG@5 `0.5227180938`,
  primary `0.5807219293`.
- `smoke`: official evaluator shape passed on the deterministic synthetic
  fixture.
