# Cycle 11 — listwise softmax diagnostic

- Hypothesis: user-exposure listwise cross-entropy may align more directly with
  within-user ranking than BPR.
- Command: inline listwise FM over contiguous train-user groups, excluding
  all-negative groups, with k=8 and official public-validation checkpoint
  selection; the first tested learning rate was `0.001`, followed by `0.005`.
- Metrics: lr `0.001`: GAUC `0.6471060952`, nDCG@5 `0.5262492248`, primary
  `0.5866776600`; lr `0.005`: GAUC `0.6569370681`, nDCG@5 `0.5299757502`,
  primary `0.5934564092`.
- Decision: listwise training is rejected. The remaining sweep was stopped
  after these completed Full evaluations because the convergence rule had
  already been met and neither approached the best `0.6044532703`.
- Next action: run final default-candidate CLI/API and focused test audit; no
  hidden-test evaluation.
