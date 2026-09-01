# Cycle 1 Scientist report

I established the first managed-data implementation and evaluated it without accessing hidden-test data. The retained score-bearing recipe is the `rich` FM in `system/fm_ranker.py`: the organizer's five categorical fields plus hour, weekday, basic-video type/music/tag, and five stable user-profile categories. It trains only on `log_standard_4_08_to_4_21_pure.csv`, selects its epoch on a deterministic complete-user Medium slice, and calls `starter_kit/evaluate.py` unchanged.

My first hypothesis was that leakage-safe historical target rates at item, author, duration, context, and user-content levels could cheaply capture much of the ranking signal. I prespecified four shrinkage/blend variants and ran:

`python3 system/train_evaluate.py --mode medium --variant all --output system/evidence/cycle1-medium.json`

On 5,590 complete users / 31,536 rows, content-only was best at GAUC 0.6472900, nDCG@5 0.5256474, primary 0.5864687. Interaction, crosses, and personal variants were worse (primary 0.5813902, 0.5836003, and 0.5800704). This weakened the hypothesis, especially the idea that sparse direct user-history target encodings would help.

I pivoted to the organizer FM and compared representations on the same Medium slice. The first combined command trained successfully but failed only while serializing the final evidence because organizer outputs backed by NumPy predictions were `numpy.float32`; its printed measurements were preserved in the session output, and I fixed the runner to convert them before JSON serialization. The base five-field FM peaked at epoch 7 with GAUC 0.6669250, nDCG@5 0.5358402, primary 0.6013826. The rich FM peaked at epoch 3 with 0.6694859 / 0.5354874 / 0.6024866.

To localize that small difference, I ran the following independent Medium ablations (both seed 0):

- `... fm_ranker.py --representation video ...` produced best primary 0.6014388 at epoch 7 (`system/evidence/cycle1-fm-video-medium.json`).
- `... fm_ranker.py --representation profile ...` produced best primary 0.5991135 at epoch 5 (`system/evidence/cycle1-fm-profile-medium.json`).

Neither group alone explains the rich model's Medium peak. The combined result could reflect interaction synergy, ordinary training variation, or selection noise; one seed and one Medium partition do not distinguish these explanations.

The selected rich model's first Full evaluation was:

- GAUC **0.6671069860**
- nDCG@5 **0.5361550450**
- primary **0.6016310453**
- 22,377 users / 124,909 rows

Evidence is `system/evidence/cycle1-fm-rich-full.json`. Relative to the official published validation baseline 0.6674 / 0.5357 / 0.6016, deltas computed against those rounded published values are GAUC **-0.0002930140**, nDCG@5 **+0.0004550450**, primary **+0.0000310453**. This is a metric tradeoff and effective tie, not a supported improvement; the official values have only four-decimal precision.

I then tested whether the structurally different content target encoder complemented the FM. `system/ensemble_ranker.py` standardized both scores using only Medium and compared prespecified target-encoder weights 0, 0.05, 0.10, 0.20, 0.30. Medium selected weight 0: primary was 0.6024866 at zero, 0.6024814 at 0.05, and declined further thereafter. The consequent second Full evaluation was therefore exactly the same FM and exactly reproduced 0.6016310453 (`system/evidence/cycle1-ensemble-full.json`). The blend hypothesis was rejected and target encoding is not part of the final scoring recipe.

There were two completed Full evaluations, both the identical selected FM score; neither improved the published primary by the task epsilon 0.002. Thus the Full no-improvement count is two, not semantic convergence (which requires three). The delegated Scientist iteration budget ends here while plausible research directions remain, so this session is budget-exhausted rather than converged.

All experiments finished far inside the 15-minute per-experiment limit (roughly 7–36 seconds). I left the executable runners and raw JSON evidence under `system/**`, updated `EXPLORE.md` and `ENGINEERING.md`, and did not create or edit `STATE.yaml` or any META-owned cumulative record.
