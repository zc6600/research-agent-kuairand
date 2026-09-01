# Blank-control baseline

`research-agent baseline` is the control condition for measuring whether the
Research Agent architecture adds value beyond the underlying coding model.

The baseline launches exactly one runner process. It does **not** create META or
Scientist roles and its fixed prompt explicitly tells the runner not to use
`research_record/**`, the Research Method, current META briefs, Research
Intuition, DO_BETTER, or Research Agent State machinery as guidance. The model
works directly from `task.md`, `PERSONAL.md` when present, the implementation,
data, and the evaluator and tries to leave the strongest verified implementation
it can find.

When `--cli codex`, `--cli agy`, or `--cli claude` is selected, the baseline launches
the runner in Goal mode (`/goal`). For Codex, the launcher submits the fixed baseline
prompt as `/goal` over a pseudo-terminal; for AGY and Claude, it submits `/goal` with
autonomous permissions and waits for the Goal session to finish. This control represents the
long-running single-agent condition rather than a single short turn. The run still
has one agent process, no META/Scientist machinery, and the same workspace and
approval boundary. Other runner choices retain their native single-invocation
transport.


This follows the official long-running agent guidance:
start `/goal` in an interactive CLI session and include clear outcome,
constraints, and verification criteria in the goal text.

The baseline target does not need `research-agent init` and should preferably be
a clean checkout of the original task. This avoids injecting Research Agent
`AGENTS.md` or project-local research instructions into the control condition.
Use a separate checkout from the Research Agent condition, both created from the
same starting implementation. Do not run the two conditions sequentially on the
same mutated checkout.

Example with Codex:

```bash
research-agent baseline \
  --target /absolute/control-project \
  --cli codex \
  --model <model> \
  --effort max \
  --allow-edits
```

Example with AGY:

```bash
research-agent baseline \
  --target /absolute/control-project \
  --cli agy \
  --model <model> \
  --allow-edits
```

Example with Claude:

```bash
research-agent baseline \
  --target /absolute/control-project \
  --cli claude \
  --model <model> \
  --allow-edits
```

Control-run metadata, raw runner output, and model-level token accounting are
kept under `.git/research-agent-baseline/<run-id>/`. The run metadata records
`mode: goal` for runners with Goal mode (such as Codex, AGY, and Claude) and
`mode: single-turn` for other runners. Keeping this operational

measurement state under `.git/` avoids adding Research Agent files to the
working tree seen by the control model.

For a meaningful comparison, keep the starting code/data, evaluator, runner
model, external tool access, and evaluation procedure fixed. Compare final task
performance together with token usage and wall-clock cost. The independent
variable should be the research architecture: direct single-agent optimization
for the blank control versus persistent META + fresh Scientist iterations for
the Research Agent condition.

## Recorded Baseline Reports

Detailed baseline execution reports and complete trajectory ledgers:

- [Headline Luna Max 3h Codex Goal Baseline (`gpt-5.6-luna`, max)](../competition_archive/kuairand-pure/reports/gpt-5.6-luna-3h-goal-baseline.md)
- [Earlier Codex Goal control (historical)](../competition_archive/kuairand-pure/reports/direct-codex-goal-baseline.md)
- [Gemini 3.7 Flash Goal Baseline (`gemini-3.7-flash`)](../competition_archive/kuairand-pure/reports/direct-gemini-3.7-flash-goal-baseline.md)
- [Codex / AGY process and implementation audit](../competition_archive/kuairand-pure/reports/baseline-protocol-audit.md)
