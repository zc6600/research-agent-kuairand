# Cycle 2 — train-only empirical-rate blend diagnostic

- Hypothesis: explicit train-only item, author, tab, and user-context rates
  might repair pointwise FM ranking errors.
- Command: an inline `.venv/bin/python` diagnostic trained the seed-0 FM,
  generated smoothed train-only rates, and evaluated each candidate through
  `starter_kit.evaluate.evaluate` on public validation.
- Metrics: item/author blends did not improve the FM; the best coarse tab-rate
  blend was GAUC `0.6675545637`, nDCG@5 `0.5360836719`, primary
  `0.6018191178` (`+0.0003503614` versus Cycle 1). A group-rank diagnostic was
  also at most `0.601705`.
- Decision: the observed lift is below `epsilon=0.002`; no rate blend was
  retained as the best checkpoint. The first probe was interrupted after a
  coding error rebuilt a large seen-pair set inside a row loop; its completed
  rate results are retained as diagnostics, not claimed as a full candidate.
- Next action: implement and validate sampled within-user pairwise FM training.
