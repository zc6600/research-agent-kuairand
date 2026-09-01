# Scientist report — cycle 3

## Question and hypothesis

The current validation-best implementation was a 5-seed logit ensemble of the 38-field rank-16 FM. I tested whether adding independent seeds 5, 6, and 7 would reduce non-convex SGD variance enough to improve the official public-validation ranking score, while keeping the representation, optimizer, learning rate, regularization, deterministic complete-user Medium checkpoint selection, and evaluator unchanged.

## Experiment

Command:

```bash
uv run --with numpy python system/ensemble_fm.py --seeds 0 1 2 3 4 5 6 7 --k 16 --lr 0.001 --l2 1e-5 --full --output system/evidence/cycle3-fm-rich38-ensemble8-full.json
```

The run used only the managed `competition_data/` files and the organizer evaluator. It trained 8 independently seeded models, selected each checkpoint on the deterministic 25% complete-user Medium slice, averaged logits, and then evaluated the ensemble on all 124,909 public-validation rows / 22,377 users. Runtime was 783.36 seconds, within the 15-minute experiment limit.

## Results

| model | GAUC | nDCG@5 | primary |
|---|---:|---:|---:|
| Existing 5-seed 38-field ensemble | 0.6704182 | 0.5377619 | 0.6040901 |
| 8-seed experiment | 0.6712176 | 0.5376403 | 0.6044289 |

The 8-seed Full primary is +0.0003389 versus the five-seed 38-field ensemble and +0.0028289 versus the published validation baseline (0.6016). GAUC improves by +0.0007994; nDCG@5 decreases by 0.0001216. The deterministic Medium ensemble primary was 0.6041272, but this Medium result was used only for per-seed checkpoint selection and is not a Full convergence decision.

## Interpretation and handoff

The result supports a modest benefit from adding seeds in this recipe, primarily through GAUC, but the effect is below the task epsilon of 0.002 and should not be treated as a large or universally reliable seed-count effect. The Full result is valid and exceeds the prior validation-best primary, so the 8-seed configuration is the strongest measured checkpoint from this session.

No executable implementation change was needed: `system/ensemble_fm.py` already accepts arbitrary seed lists. The exact evidence is `system/evidence/cycle3-fm-rich38-ensemble8-full.json`. I did not edit `research_record/STATE.yaml` or create a State tag; META should decide whether to crystallize the 8-seed configuration as the next State.

No hidden-test files or labels were accessed.
