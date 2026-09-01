# Usage Accounting

Token accounting is runner telemetry, not a capability of the researched
model. Reports preserve what was observed, when it was observed, and which
runner scope was measured.

## Normalized reports

Runner snapshots use:

- `accounting_status`: `measured` or `unavailable`;
- `scope: runner_sessions`;
- `sessions` and token counters only when the backend actually measured them;
- `reason` when measurement is unavailable.

A finalized external `step`, `run`, or `resume` may additionally produce a
run-level delta:

```json
{
  "runner": "codex",
  "accounting_status": "measured",
  "final": true,
  "scope": "run_delta",
  "input": 12000,
  "output": 1800,
  "reasoning": 600,
  "cache_read": 4000,
  "cache_write": 0,
  "total": 13800,
  "baseline_status": "measured",
  "observed_at": "2026-08-29T00:00:00Z"
}
```

Counter meanings follow the selected runner's native telemetry. A backend may
provide only a measured total; in that case `breakdown_status` is
`total_only`. Never infer a missing breakdown from text length.

Zero is valid only inside a measured report. No matching session, missing
backend, unreadable database, unsupported runner, missing baseline, or
incomparable snapshots remain explicitly unavailable. They must not be
converted to a measured zero.

## Per-role and per-model run accounting

`model-usage.json` is the richer experiment-facing observation. Scientist
invocations are captured separately and the dashboard groups measured usage by
role, runner, and configured or runner-reported model.

Gemini and AGY expose structured headless session metrics, so their META,
Scientist, and baseline invocations are measured directly from the output of
each CLI process. AGY maps its official `usage` object as follows:

- `input_tokens` -> `input`;
- `output_tokens` -> `output`;
- `thinking_tokens` -> `reasoning`;
- `cache_read_tokens` -> `cache_read`;
- `total_tokens` -> `total`.

AGY does not currently report cache-write tokens in that envelope, so the field
is omitted rather than invented as zero. When an explicit `--model` is used,
the session usage is attributed to that configured model. If AGY internally
uses other models but does not expose a per-model split, the report remains a
session-level measurement for the configured AGY model rather than guessing an
internal breakdown.

For runners without direct per-process structured metrics, the launcher may
use runner-native cumulative telemetry and isolate META from separately
measured Scientist activity when the counters are comparable.

## Automatic run accounting

The outer launcher takes one best-effort runner snapshot immediately before
starting META and another after META exits. Those two snapshots are transient
calculation inputs; they are not runtime artifacts and are not exposed to the
agent through a special environment variable.

A run delta is published only when both snapshots are measured by the same
runner and the cumulative counters move monotonically forward. If those
conditions are not met, the finalized legacy run usage observation is
`unavailable` rather than an invented delta.

The persisted legacy usage observation is:

```text
target/research_record/runtime/tmp/<run-id>/meta/usage.json
```

The richer role/model report is:

```text
target/research_record/runtime/tmp/<run-id>/meta/model-usage.json
```

Scientist invocation measurements used to build that report are stored under
the same run's `scientist/` runtime directory. Blank-control measurements live
with the baseline run metadata under `.git/research-agent-baseline/`.

There is no `latest-usage.json`. Consumers locate the latest run through its
`run.json` and then read that run's own usage artifacts. If the latest run is
still active and final usage does not exist yet, consumers must show usage as
unknown rather than reuse an older run's value.

An active META cannot know the final tokens of its own unfinished model
session. META may inspect runner-native context information or invoke the
manual collector when useful for a budget decision, but that is distinct from
the launcher's finalized run accounting.

## Scope

Automatic accounting uses the target project root. META and Scientist runner
processes both execute with the target as their working directory, so the
launcher does not maintain a second control-root accounting scope.

The legacy run delta covers the selected runner's observable activity under
that target during the entire external run. A `run` or `resume` may contain
multiple Scientist iterations, so this value must not be relabeled as a
Scientist-only or single-cycle token count.

The delta intentionally omits `sessions`: subtracting two cumulative session
counts would measure only newly appearing sessions, not the sessions that
actually consumed tokens during the run.

## Backend coverage

| Runner | Source | Current behavior |
|---|---|---|
| Codex | newest `state_*.sqlite` plus rollout JSONL when available | full breakdown when rollout usage exists; measured total fallback otherwise |
| Claude | assistant usage entries in `~/.claude/projects/**/*.jsonl` | sums matching target sessions |
| OpenCode | cumulative token columns in the local `session` table | sums matching target sessions |
| Gemini | headless JSON session stats | direct per-invocation model metrics |
| agy | headless JSON `usage` envelope | direct per-invocation input/output/thinking/cache-read/total metrics; cumulative manual collector remains unavailable |

Telemetry formats are version-sensitive. A schema mismatch must degrade to an
unavailable result, not silently switch to an unrelated runner or estimate.

## Manual query

Select the runner explicitly with the canonical CLI:

```bash
research-agent usage \
  --target /absolute/project \
  --cli codex \
  --final
```

Use `--session ID` to request one exact runner session. Use `--include-path`
only when a human explicitly wants to include another runner working-directory
scope in a manual query. The command prints JSON and exits 1 for unavailable
telemetry so automation can distinguish it from a measured report.

The manual `research-agent usage --cli agy` command still has no cumulative
AGY backend. AGY measurement is instead captured automatically around the
actual Research Agent or blank-control invocation, where the CLI's own JSON
usage envelope is authoritative.
