# `gemini-3.7-flash` Medium Baseline — 2026-08-31

## Summary

A separate blank-control baseline was launched in an isolated medium-baseline
workspace with runner CLI 1.1.22, model `gemini-3.7-flash`, and reasoning effort
`medium`. The run was given a three-hour budget and used only the curated
KuaiRand-Pure development view and the official starter-kit evaluator.

The outer runner was safely stopped at the hard limit after 3:01:44. The agent
did not return a final summary or verified optimization result before the limit.
The target was left with the official FM baseline unchanged; no generated
implementation change or verified optimization result was observed. The
exploration script found in the clean starter snapshot is not evidence of work
performed by this run.

## Verified public result

After interruption, the final target implementation was evaluated once with
the official FM command (`seed=0`, public validation only):

| Metric | Final target / FM seed 0 | Official FM control | Change |
|---|---:|---:|---:|
| GAUC | 0.6671 | 0.6674 | -0.0003 |
| nDCG@5 | 0.5358 | 0.5357 | +0.0001 |
| Primary mean | 0.6015 | 0.6016 | -0.0001 |

The evaluation covered 124,909 public validation rows. The target manifest
declares `development_only_no_hidden_test`; no hidden-test score is available.
The official control values are the published five-seed reference values, while
the final-target values above are a single reproducibility check after the
interrupted run.

## Operator-designed goal

Optimize the KuaiRand-Pure long-view ranker for public-validation primary score
through repeated inspect/measure/change/verify cycles for up to three hours,
preserving the strongest verified checkpoint. Explore model, feature, objective,
sampling, and representation changes when justified by evidence; use no
hidden/test rows, research-agent roles, subagents, parent/sibling workspaces, or
`research_record`; report GAUC, nDCG@5, primary, deltas, elapsed time, and the
final configuration.

## Run status and evidence

- Runner status: `closed`, `terminal_status: interrupted`, exit code `130`.
- Started: `2026-08-31T18:01:09.775762+00:00`.
- Ended: `2026-08-31T21:02:53.794216+00:00`.
- Wall-clock duration: `3:01:44`.
- Model usage: unavailable; the runner exposes no verified local token telemetry
  backend.
- Post-run checks: 3 unit tests passed; the system smoke test passed with
  `GAUC=1.0`, `nDCG@5=1.0`, and `primary=1.0`.
- The baseline log is empty and its runner result records the interruption;
  therefore no `gemini-3.7-flash` experiment-level improvement is claimed.

## Evidence boundary

The medium run is retained as a negative control in the trajectory index. Its
structured result is sufficient to document the interruption and the one
post-run reproducibility check, but no token total or agent-generated model
change is available for the comparison.
