# Cycle 10 — train-only hard-negative mining

- Hypothesis: selecting high-scoring train negatives could make pairwise
  learning more ranking-effective than uniform negatives.
- Command: inline k=8, lr `0.00025` pairwise FM with one negative per positive,
  selecting from the current top negative pool sizes `1`, `5`, `20`, plus a
  random-control pool; only train rows were used for mining.
- Metrics: pool 1 primary `0.5133061084`, pool 5 `0.5334015939`, pool 20
  `0.5935823444`, random-control `0.6038737377`.
- Decision: hard mining is rejected; it destabilizes this model and is below
  the saved checkpoint.
- Next action: one listwise diagnostic was started; convergence is already
  supported by the preceding completed Full evaluations if it remains below
  the best.
