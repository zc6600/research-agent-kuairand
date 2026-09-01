# Final single-agent baseline checkpoint

- Completed trajectory: 11 substantial cycles, approximately 29 minutes of
  active tool time; the 12-cycle/60-minute hard budget was not reached.
- Stopping condition: after the validation-best checkpoint was found, at least
  three subsequent completed Full public-validation evaluations (auxiliary
  feedback, hard-negative mining, and listwise softmax; with the preceding
  two-negative/cross controls also below the frontier) failed to improve
  primary by more than `epsilon=0.002`. No hidden-test evaluation was run.
- Best command: `.venv/bin/python -m system.cli evaluate-fm-pairwise --data-dir competition_data/data --split valid`.
- Best model: five official FM fields, sampled one same-user train negative per
  positive, factors `8`, learning rate `0.00025`, 40 epochs, batch size
  `8192`, patience `4`, seed `0`.
- Best public-validation metrics: GAUC `0.6712470735`, nDCG@5 `0.5376594671`,
  primary `0.6044532703`.
- Deltas versus the official validation baseline (`0.6674`, `0.5357`,
  `0.6016`): GAUC `+0.0038470735`, nDCG@5 `+0.0019594671`, primary
  `+0.0028532703`.
- Deltas versus the seed-0 pointwise FM checkpoint: GAUC `+0.0041144414`,
  nDCG@5 `+0.0018545866`, primary `+0.0029845140`.
- Controls/tests: popularity public primary `0.5807219293`; synthetic smoke
  passed; 5 API unit tests passed; Python compilation, CLI help, curated-data
  row-count/keys, curated-only path guard, and `git diff --check` passed.
- Blocker: none.
