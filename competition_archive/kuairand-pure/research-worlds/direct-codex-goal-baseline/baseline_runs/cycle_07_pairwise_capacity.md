# Cycle 7 — pairwise factor capacity

- Hypothesis: the best latent rank under pointwise training may not be the
  best rank under pairwise training.
- Command: pairwise FM, lr `0.0005`, one negative per positive, seed `0`,
  factors `8` and `32`, official public evaluator.
- Metrics: k=8 GAUC `0.6710279481`, nDCG@5 `0.5374375032`, primary
  `0.6042327257`; k=32 GAUC `0.6696778442`, nDCG@5 `0.5371252408`, primary
  `0.6034015425`.
- Decision: k=8 is the new best; k=32 is rejected.
- Next action: refine lr around k=8 and test explicit train-only crosses.
