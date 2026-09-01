# `gpt-5.6-luna` 3h Direct Baseline — 2026-08-31

## Summary

A blank-control optimization run was executed in the isolated child workspace
`competition_archive/kuairand-pure/research-worlds/gpt-5.6-luna-3h-goal-baseline`
(an isolated historical child workspace) using
`gpt-5.6-luna` with a three-hour budget. The run reached a meaningful stopping
point and completed its substantive task after about 1 hour 55 minutes; the
outer interactive terminal was then closed after it emitted `task_complete`.

The root worktree and the previous direct-control workspace were left
untouched. This run supersedes the earlier, shorter direct Codex control as the
headline `gpt-5.6-luna` baseline in the competition comparison.

## Best reportable result

The final optimized ranker scored the hidden-test-free public validation split
as follows:

| Metric | Optimized ranker | Official FM control | Change |
|---|---:|---:|---:|
| GAUC | 0.6718 | 0.6674 | +0.0044 |
| nDCG@5 | 0.5374 | 0.5357 | +0.0017 |
| Primary mean | 0.6046 | 0.6015 | +0.0030 |

The optimized run evaluated 124,909 validation rows across 22,377 users. The
mean primary score across five seeds was 0.6038, an improvement of about
0.0022 over the reproduced control. The headline value is rounded to the
precision preserved in the run's README and trajectory summary (`0.6046`).

## Retained configuration

The strongest verified implementation uses a six-field FM ranker:

- `user_id`
- `video_id`
- `author_id`
- `tab`
- duration bucket
- `tab×hour`

Training uses positive-class weight `2.0`. Submission generation defaults to
this optimized ranker and retains an explicit official-control switch for
apples-to-apples comparison.

## Search trajectory

The run began with item popularity (public primary about 0.5807) and reproduced
the official FM control (about 0.6015). Pairwise and listwise fine-tuning,
additional static/cross fields, duration refinements, recency weighting, and
seed ensembling did not produce a sustained improvement.

The main gains came from two steps:

1. adding the train-only `tab×hour` context field, which raised primary to
   about 0.6020; and
2. applying positive-class weight `2.0`, which raised the verified public
   primary to 0.6046 and improved both GAUC and nDCG@5.

## Verification and evidence scope

Compilation, whitespace validation, the three existing unit tests, synthetic
smoke tests, submission alignment checks, the optimized CLI/API path, and the
official-control path passed. No hidden-test result was available: the run used
only the curated development view whose manifest declares
`development_only_no_hidden_test`.

The outer runner metadata is marked `terminal_status: interrupted` with exit
code 130 because the already-completed Codex interactive terminal was closed
after `task_complete`; this is an operator-level terminal status, not a failed
model experiment.

## Time and token ledger

The lifecycle timestamps are recorded in UTC. Converted to Singapore time, the
main run started at 2026-08-31 22:20:34 and ended at 2026-09-01 00:15:51, for
1h 55m 17s of wall time. The configured budget was three hours; the process did
not consume the full allowance.

The measured Codex usage snapshot reports 27,999,762 input tokens (including
27,664,640 cache-read tokens), 69,812 output tokens, and 28,069,574 total
tokens. For the comparison figure's non-cache convention:

| Quantity | Tokens | Interpretation |
|---|---:|---|
| Input including cache-read | 27,999,762 | Raw input field in the Codex usage snapshot |
| Cache-read input | 27,664,640 | Reported separately; excluded from the comparison axis |
| Non-cache input | 335,122 | Input minus cache-read input |
| Output | 69,812 | Includes the reported 29,416 reasoning tokens; do not add reasoning again |
| **Non-cache input + output** | **404,934** | Figure/table comparison value |
| Total including cache-read | 28,069,574 | Raw `total_tokens` snapshot |

No currency cost or per-cycle token breakdown was recorded.

## Artifacts

- Target workspace: [`gpt-5.6-luna-3h-goal-baseline`](../research-worlds/gpt-5.6-luna-3h-goal-baseline)
- Final ranker: [`starter_kit/baseline.py`](../research-worlds/gpt-5.6-luna-3h-goal-baseline/starter_kit/baseline.py)
- Data loader: [`starter_kit/data.py`](../research-worlds/gpt-5.6-luna-3h-goal-baseline/starter_kit/data.py)
- Submission path: [`starter_kit/submit.py`](../research-worlds/gpt-5.6-luna-3h-goal-baseline/starter_kit/submit.py)
- Run metadata: [`run.json`](../evidence/gpt-5.6-luna-3h-goal-baseline/run.json)
- Runner result: [`result.json`](../evidence/gpt-5.6-luna-3h-goal-baseline/result.json)
- Full terminal log: [`baseline.log`](../evidence/gpt-5.6-luna-3h-goal-baseline/baseline.log)
- Measured usage: [`model-usage.json`](../evidence/gpt-5.6-luna-3h-goal-baseline/model-usage.json)
