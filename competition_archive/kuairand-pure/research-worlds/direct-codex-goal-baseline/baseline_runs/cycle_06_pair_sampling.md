# Cycle 6 — two negatives per positive

- Hypothesis: more same-user negative comparisons could reduce sampling noise.
- Command: pairwise FM, `factors=16`, lr `0.0005`, seed `0`, one versus two
  sampled train-only negatives per positive; official public validation for
  checkpoint selection.
- Metrics: two negatives: GAUC `0.6702011069`, nDCG@5 `0.5371198262`, primary
  `0.6036604666`; it is below the one-negative primary `0.6038589810`.
- Decision: retain one negative per positive.
- Next action: check pairwise factor capacity.
