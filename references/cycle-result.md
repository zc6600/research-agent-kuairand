# META Result Handoff

After META finishes supervising its delegated research trajectory, it writes one
small final JSON object for the external launcher:

```json
{
  "status": "converged",
  "summary": "What changed and what META concluded from current project evidence.",
  "next_action": "The process-level follow-up, such as stop, continue, or request human input."
}
```

For `step`, META may have supervised at most one Scientist. For `run` and
`resume`, the same META process may have supervised multiple fresh Scientist
iterations before writing this final handoff.

`status` is one of:

- `continue`: more research would be useful;
- `converged`: the task-defined convergence rule is satisfied;
- `budget_exhausted`: a compute, token, or delegated cycle budget is exhausted;
- `needs_human`: a decision or authorization requires human input;
- `failed`: the run could not complete normally.

`next_action` describes process control, not the next scientific direction. If
research continues, the next fresh Scientist reconstructs the current research
environment and independently chooses what question, hypothesis, exploratory
work, experiment, or implementation change is worth pursuing.

This file is ordinary process coordination. It is not scientific evidence, a
research record, or a tamper-proof receipt. The launcher does not bind it to a
brief digest, archive exact bytes, validate evidence references, or commit it
to Git.

Scientific claims and experiment history belong in the persistent research
environment: each Scientist leaves a free-form persisted session report, while
META maintains `RESEARCH_RECORD.yaml`, `RESEARCH_BRIEF.md`,
`RESEARCH_INTUITION.md`, and `DO_BETTER.md` after checking the report against
raw logs/results, explicit evidence artifacts, source, evaluator behavior, and
observed State behavior. State tags and their Git snapshots identify which
implementation belongs to a State; Git commit history is not the research
chronology.

Research progress is broader than benchmark gain: reduced uncertainty,
falsified or supported hypotheses, reusable knowledge, scientific intuition,
research-process learning, and improved or otherwise useful States may all be
valuable progress.

META owns cycle sequencing and the delegated `max_cycles` policy. The external
launcher records META's final status as written; it does not reinterpret
`continue` from the final brief or inferred cycle count. If META means that its
cycle budget is exhausted, META should return `budget_exhausted` itself.

If the handoff is missing or unreadable, the launcher cannot infer a terminal
state and returns control for inspection. A non-zero META or Scientist runner
exit also stops the run.
