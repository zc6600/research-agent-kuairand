# KuaiRand-Pure Competition Evidence Archive

This archive contains only the historical research worlds and analyses used by
[`docs/FINAL_REPORT.md`](../../docs/FINAL_REPORT.md). The public, self-contained
submission remains [`submission/research-agent-kuairand/`](../../submission/research-agent-kuairand/).

## Research worlds

| Archive name | Previous project name | Final Report use | Relevant checkpoint |
|---|---|---|---|
| `research-agent-source` | `final Research Agent submission` | Source research world for the verified submission | Primary 0.6059363 |
| `gemini-3.7-flash-only-cycle2-e008` | `gemini-3.7-flash-only cycle-2 research world` | `gemini-3.7-flash`-only comparison through Cycle 2 | E008 Primary 0.6052 |
| `gpt-5.6-luna-3h-goal-baseline` | `gpt-5.6-luna` direct control | Headline direct `gpt-5.6-luna` 3h baseline | Best public-validation Primary approximately 0.6046 |
| `direct-codex-goal-baseline` | `direct Codex control` | Earlier direct Codex control; superseded by the `gpt-5.6-luna` 3h run | Best Primary 0.6044533 |
| `agy-medium-baseline-2h-2026-09-01` | `p0_baseline_antigravity_2h` | Headline corrected AGY `gemini-3.7-flash` 2h direct control | Primary 0.6045803 |
| `gemini-3.7-flash-heterogeneous-subagents-baseline` | `heterogeneous gemini-3.7-flash control` | Delegated heterogeneous `gemini-3.7-flash` control | Best artifact-backed Primary approximately 0.6047 |

The `gemini-3.7-flash`-only research-world snapshot also contains later cycles. The Final Report
comparison stops at the Cycle-2 result; later exploratory results are outside
that plotted comparison.

## Submission form

The six directories under `research-worlds/` are submitted as ordinary source
snapshots rather than Git submodules. They contain the code and records needed
by the linked reports. Local Git metadata, virtual environments, caches, and
`competition_data/` are excluded from the parent submission.

## Reports used by the final narrative

- [`reports/gpt-5.6-luna-3h-goal-baseline.md`](reports/gpt-5.6-luna-3h-goal-baseline.md)
- [`reports/direct-codex-goal-baseline.md`](reports/direct-codex-goal-baseline.md)
- [`reports/agy-medium-baseline-2h-2026-09-01.md`](reports/agy-medium-baseline-2h-2026-09-01.md)
- [`reports/gemini-3.7-flash-heterogeneous-subagents-baseline.md`](reports/gemini-3.7-flash-heterogeneous-subagents-baseline.md)
- [`reports/baseline-protocol-audit.md`](reports/baseline-protocol-audit.md)
- [`reports/baseline-and-token-synthesis.md`](reports/baseline-and-token-synthesis.md)
- [`analysis/scientific-validity-failure.md`](analysis/scientific-validity-failure.md)
- [`analysis/late-stage-anchoring.md`](analysis/late-stage-anchoring.md)
- [`analysis/model-search-behavior.md`](analysis/model-search-behavior.md)

The `gpt-5.6-luna-3h-goal-baseline` report remains the headline direct
`gpt-5.6-luna` control. The corrected AGY 2h run is now the direct
`gemini-3.7-flash` control used in the Final Report; the older one-hour direct
`gemini-3.7-flash` report remains in the archive only as superseded history.
The earlier `direct-codex-goal-baseline` also remains for audit history only.

The exact Cycle-2 E008 score and token boundary are captured in the tracked
[`E008 evidence snapshot`](evidence/gemini-3.7-flash-only-cycle2-e008.md). Raw
child-run logs remain in the local research world for provenance but are not
required for the public claim.

## Accounting convention

Token comparisons use non-cache input + output. For the `gemini-3.7-flash`-only trajectory through Cycle 2, the
directly attributable cumulative minimum is 2,070,960 tokens. The persistent
META session spans Cycles 2–4 and has no per-cycle split, so assigning its entire
827,670-token total gives a conservative upper bound of 2,898,630.

The headline `gpt-5.6-luna` 3h baseline reports 335,122 non-cache input tokens plus
69,812 output tokens, or **404,934** comparison tokens. Its raw input-plus-output
snapshot is 28,069,574 because 27,664,640 cache-read tokens are reported inside
the input field and excluded from the comparison axis.
