# Cycle 4 — pairwise seed stability

- Hypothesis: Cycle 3's lift should survive fixed-seed reruns.
- Command: pairwise FM with `factors=16`, `learning_rate=0.001`, one
  train-only negative per positive, seeds `1` and `2`, public validation
  checkpoint selection.
- Metrics: seed 1 GAUC `0.6696339610`, nDCG@5 `0.5372469512`, primary
  `0.6034404561`; seed 2 GAUC `0.6695923645`, nDCG@5 `0.5370549740`, primary
  `0.6033236693`.
- Decision: the pairwise direction is stable and remains above the pointwise
  FM; retain Cycle 3's higher validation checkpoint while tuning.
- Next action: tune pairwise learning rate and sampling/capacity.
