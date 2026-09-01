# AGY `medium` Goal Baseline — 2h Maximum — 2026-09-01

## Summary

This is the corrected AGY baseline run requested as a two-hour maximum. It
used `mode=goal`, AGY CLI 1.1.22, model `gemini-3.7-flash`, and reasoning
effort `medium` in the isolated target project
`projects/p0_baseline_antigravity_2h/`.

The agent completed its operator-designed goal in 67m39.9s and returned exit
code 0. The final public-validation submission was re-scored independently
with the repository's official starter-kit evaluator. The authoritative
result is **GAUC 0.6714473, nDCG@5 0.5377133, primary 0.6045803**.

## Why the earlier 2h attempt was excluded

An earlier 2h attempt (`89fdbbf6e7ca4d44bfe2a37c26ac5632`) also returned
normally, but AGY had silently used its global `default-cli-project` scratch
workspace because the target was not registered as an AGY project. Its
reported `0.6031` therefore was not attributable to the requested target
workspace and is excluded from the baseline result.

The runner was corrected to invoke AGY with `--new-project`, which binds the
session workspace to the invocation directory. A no-op probe confirmed the
target path before the formal rerun. The corrected run's raw log and generated
files are all under the target project's `.git/` and working tree.

## Run configuration and goal

- Target: `projects/p0_baseline_antigravity_2h/`
- Run ID: `a2723fa527c948eca931b9ac4dc9f784`
- Mode: `goal`
- Runner: `agy` 1.1.22
- Model: `gemini-3.7-flash`
- Effort: `medium`
- Permissions: `accept-edits` with the research sandbox permission flag
- Goal: repeatedly inspect, measure, change, and verify the public-validation
  KuaiRand-Pure `long_view` ranker, retaining the strongest verified result;
  use no hidden/test rows, subagents, parent/sibling workspaces, or
  `research_record`.
- AGY request timeout: 105 minutes
- Outer runner hard limit: 6,900 seconds (115 minutes), leaving cleanup time
  within the requested 2h ceiling
- Output: non-streaming JSON, because the hard timeout and streaming mode are
  incompatible in the runner

The run progressed through official FM control, CatBoost/OOF target encoding,
unified DeepFM and DCN-v2 models, multi-task supervision, AutoCrossNet, a
multi-seed ensemble, and public-validation blend optimization.

## Run status and measured usage

| Field | Value |
|---|---|
| Started | `2026-09-01T00:42:58.194815+00:00` |
| Ended | `2026-09-01T01:50:38.140982+00:00` |
| Wall duration | 4,059.946s (67m39.9s) |
| Runner status | `closed` |
| Terminal status | `completed` |
| Exit code | `0` |
| Total input + output including cache-read | **8,564,976 tokens** |
| Non-cache input + output | 1,117,370 tokens |
| Input | 1,051,695 |
| Output | 65,675 |
| Reasoning | 11,607 |
| Cache read | 7,447,606 |

The 20,358-token workspace probe and the 946,615-token invalid-workspace
attempt are separate invocations and are not included in the formal rerun
total above.

## Verified public result

The formal target's final file was checked with:

```bash
python starter_kit/submit.py outputs/submission_valid_best.csv \
  --split valid --data_dir competition_data/data --score
```

The evaluator accepted all 124,909 public validation rows and reported:

| Metric | Final optimized blend | Official FM control | Delta |
|---|---:|---:|---:|
| GAUC | 0.6714473005 | 0.6674 | +0.0040473005 |
| nDCG@5 | 0.5377133445 | 0.5357 | +0.0020133445 |
| Primary mean | **0.6045803225** | 0.6016 | **+0.0029803225** |

The official control values above are the five-seed reference values used by
the target pipeline. An earlier single-seed FM reproducibility check recorded
`0.6671 / 0.5358 / 0.6015`; that result is retained in the older trajectory
record, but its delta should not be mixed with this five-seed control.

## Verified model components and blend

The strongest verified component metrics in the target summary were:

| Model | Seed | GAUC | nDCG@5 | Primary |
|---|---:|---:|---:|---:|
| AutoCrossNet | 42 | 0.6694302298 | 0.5368486686 | 0.6031394492 |
| Unified DCN-v2 | 42 | 0.6687808791 | 0.5362980580 | 0.6025394686 |
| Unified DeepFM | 42 | 0.6683064530 | 0.5365100422 | 0.6024082476 |
| Multi-Task DeepFM | 42 | 0.6702091489 | 0.5370387604 | 0.6036239546 |
| AutoCrossNet | 2024 | 0.6701722728 | 0.5376401013 | 0.6039061871 |
| Optimized five-model blend | — | **0.6714473005** | **0.5377133445** | **0.6045803225** |

The final blend weights, in the order used by `optimize_blend.py`, were:

```text
AutoCrossNet_seed42       0.20
UnifiedDCNv2_seed42       0.20
UnifiedDeepFM_seed42      0.15
MultiTaskDeepFM_seed42    0.10
AutoCrossNet_seed2024     0.35
```

## Evidence and limitations

- The final score is a public-validation score only; no hidden-test score is
  available.
- The score above was independently re-scored after rerunning the local blend
  optimizer, so it is not based only on the agent's final narrative.
- The generated scripts, checkpoints, and output CSV are untracked artifacts
  in the child project; no commit was created.
- Focused runner, baseline, and usage tests passed (28 tests); the full
  research-agent suite had also passed earlier (187 tests).

## Public evidence links

- [Compact score and usage snapshot](../../competition_archive/kuairand-pure/evidence/agy-medium-baseline-2h-2026-09-01.md)
- [Archived comparison report](../../competition_archive/kuairand-pure/reports/agy-medium-baseline-2h-2026-09-01.md)
- [Competition evidence index](../../competition_archive/kuairand-pure/INDEX.md)

The raw lifecycle JSON, full terminal log, generated submission, summary
metrics, and blend optimizer remain local child-project artifacts and are not
presented as public repository links.
