# Cycle 9 — auxiliary feedback pair losses

- Hypothesis: correlated training-only feedback may regularize long-view
  ranking without using feedback from public target rows.
- Command: inline pairwise FM diagnostic on the same five fields, k=8, lr
  `0.00025`, seed `0`; mixed train-only same-user pairs for `is_click`,
  `is_profile_enter`, and `is_like` at weights `0.1`, `0.25`, `0.5`; every
  result evaluated with `starter_kit/evaluate.py` on public validation.
- Metrics: best auxiliary result was `is_click`, weight `0.1`: GAUC
  `0.6706593093`, nDCG@5 `0.5374222306`, primary `0.6040407700`. Larger
  weights and the other feedback labels were lower.
- Decision: auxiliary mixing does not beat the current `0.6044532703`; do not
  retain it.
- Next action: test hard-negative selection, then stop on convergence if no
  material improvement remains.
