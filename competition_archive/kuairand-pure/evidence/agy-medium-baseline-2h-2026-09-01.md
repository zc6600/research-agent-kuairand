# AGY 2h baseline evidence snapshot

This is the compact evidence snapshot for the corrected `p0_baseline_antigravity_2h`
direct Goal run. It supersedes the older one-hour direct `gemini-3.7-flash`
control in the comparison table.

| Field | Recorded value |
|---|---|
| Run ID | `a2723fa527c948eca931b9ac4dc9f784` |
| Runner / model | AGY 1.1.22 / `gemini-3.7-flash` |
| Effort | `medium` |
| Budget | 2h maximum |
| Actual wall-clock | 4,059.946s (67m39.9s) |
| Measured non-cache tokens | 1,117,370 (1,051,695 input + 65,675 output) |
| Cache-read tokens | 7,447,606 (reported separately) |
| **Total input + output including cache-read** | **8,564,976** |
| GPU-hours | 0 (Apple Silicon MPS was available; the run used the local target pipeline) |
| Public-validation rows | 124,909 |
| GAUC | 0.6714473005 |
| nDCG@5 | 0.5377133445 |
| Primary | **0.6045803225** |
| Delta vs official validation primary 0.6016 | **+0.0029803225** |

The final result is the independently re-scored five-model blend from the
target's `outputs/summary_metrics.json`, evaluated with the unchanged Starter
Kit evaluator. The earlier `89fdbbf6...` attempt is excluded because AGY used a
global scratch workspace rather than the requested target. Workspace binding,
the corrected run metadata, and the full experiment narrative are documented
in [`agy-medium-baseline-2h-2026-09-01.md`](../../../docs/trajectories/agy-medium-baseline-2h-2026-09-01.md).
