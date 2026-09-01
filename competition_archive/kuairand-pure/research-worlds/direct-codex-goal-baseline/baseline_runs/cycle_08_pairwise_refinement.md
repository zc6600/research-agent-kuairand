# Cycle 8 — k=8 refinement and explicit crosses

- Hypothesis: a smaller lr or explicit user/item crosses may complement the
  pairwise latent representation.
- Command: pairwise FM, seed `0`, k=8, one negative per positive, 40 epochs,
  with lr `0.00025`/`0.00075` and train-only `user_tab`/`video_tab` extra
  fields.
- Metrics: lr `0.00025`: GAUC `0.6712470735`, nDCG@5 `0.5376594671`, primary
  `0.6044532703` (best). lr `0.00075`: primary `0.6041803564`.
  `user_tab`: GAUC `0.6704557381`, nDCG@5 `0.5373354569`, primary
  `0.6038955975`; `video_tab`: GAUC `0.6705311633`, nDCG@5 `0.5369507543`,
  primary `0.6037409588`.
- Decision: retain k=8, lr `0.00025`, no extra field. The improvement over
  Cycle 7 is `0.0002205446`, below epsilon but it is the valid frontier.
- Next action: test auxiliary feedback as a training-only signal.
