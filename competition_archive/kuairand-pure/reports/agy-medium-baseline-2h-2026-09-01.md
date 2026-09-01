# AGY `medium` 2h direct baseline

This corrected AGY Goal run replaces the older one-hour direct
`gemini-3.7-flash` baseline in the final comparison. The detailed trajectory
report is [`docs/trajectories/agy-medium-baseline-2h-2026-09-01.md`](../../../docs/trajectories/agy-medium-baseline-2h-2026-09-01.md),
and the compact score/token snapshot is
[`evidence/agy-medium-baseline-2h-2026-09-01.md`](../evidence/agy-medium-baseline-2h-2026-09-01.md).

| Metric | AGY 2h baseline | Official FM reference | Delta |
|---|---:|---:|---:|
| GAUC | 0.6714473005 | 0.6674 | +0.0040473005 |
| nDCG@5 | 0.5377133445 | 0.5357 | +0.0020133445 |
| **Primary** | **0.6045803225** | **0.6016** | **+0.0029803225** |

The run used `gemini-3.7-flash` through AGY 1.1.22, with `medium` effort, and
completed in 4,059.946 seconds. Its measured non-cache input + output was
1,117,370 tokens; cache-read input was 7,447,606 tokens, giving **8,564,976
total input + output tokens including cache-read**. The earlier `89fdbbf6...` attempt is not included because it was
bound to AGY's global scratch workspace rather than the requested target.
