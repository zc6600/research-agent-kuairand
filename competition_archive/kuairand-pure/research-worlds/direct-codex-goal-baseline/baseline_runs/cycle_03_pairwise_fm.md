# Cycle 3 — sampled within-user pairwise FM

- Hypothesis: the evaluator ranks impressions within each user, so sampling
  train-only positive/negative pairs from the same user and optimizing BPR-style
  logistic ordering should improve GAUC and nDCG over pointwise logloss.
- Command: `.venv/bin/python` calling `fm_pairwise_scores(..., validation_rows=valid, factors=16, learning_rate=0.001, epochs=40, batch_size=8192, patience=4, seed=0)`; metrics came from `evaluate_scores`, which delegates to `starter_kit/evaluate.py`.
- Metrics: GAUC `0.6702483708`, nDCG@5 `0.5372679854`, primary `0.6037581781`.
- Deltas: versus published valid baseline `+0.0028483708` GAUC,
  `+0.0015679854` nDCG@5, `+0.0021581781` primary; versus Cycle 1
  `+0.0031157387`, `+0.0014631048`, `+0.0022894218` respectively.
- Decision: retain as current best valid checkpoint and expose it through the
  Python API/CLI. Repeat with another fixed seed before further changes.
- Next action: seed stability and pair-sampling/learning-rate sensitivity.
