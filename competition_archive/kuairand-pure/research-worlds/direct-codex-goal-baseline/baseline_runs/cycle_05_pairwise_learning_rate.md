# Cycle 5 — pairwise learning-rate sweep

- Hypothesis: the pairwise optimizer may prefer a smaller step than the
  official pointwise FM.
- Command: pairwise FM, `factors=16`, one negative per positive, seed `0`,
  `epochs=40`, `batch_size=8192`, `patience=4`, with learning rates `0.0005`
  and `0.002`.
- Metrics: lr `0.0005`: GAUC `0.6704166044`, nDCG@5 `0.5373013575`, primary
  `0.6038589810`; lr `0.002`: GAUC `0.6688596654`, nDCG@5 `0.5364221826`,
  primary `0.6026409240`.
- Decision: lr `0.0005` improves the Cycle 3 checkpoint by `0.0001008029`
  primary, but remains a sub-epsilon refinement; continue checking sampling
  and capacity.
- Next action: test additional negatives per positive.
