# Frozen Goal prompt

This is the exact prompt submitted to the interactive Codex session for the
benchmark documented in `CODEX_GOAL_BENCHMARK.md`.

```text
/goal Run the correct agent-system baseline for project direct-codex-goal-baseline.

You are the single direct Codex agent being measured. This is NOT the KuaiRand recommendation-model baseline: popularity and FM are only task models/evaluation controls. The baseline is the behavior of one Codex agent operating autonomously over a long horizon, corresponding to an agent system with no META layer, no Scientist layer, no delegation, and no other agents.

Work directly in the current project only: /Users/frank/github_project/Good4AI/research_agent/projects/direct-codex-goal-baseline. Read task.md, PERSONAL.md, AGENTS.md, the official starter_kit, and the current system implementation. Do not invoke research-agent, do not launch META/Scientist or any subagent, do not access sibling projects or the parent workspace, and do not use hidden-test data. Use only the curated local data in competition_data/data and the official organizer evaluator. Preserve a usable Python API and CLI in system/.

This is a long-horizon autonomous run, not a one-shot implementation. Use a hard budget of up to 60 minutes or 12 substantial experiment cycles, whichever comes first. Do not return after the first inspection, first implementation, or first passing smoke test. Do not stop merely because the current API is already reasonable. Stay active and iterate until the hard budget, or until there have been at least 3 consecutive meaningful Full public-validation evaluations without a primary improvement, or a genuine external blocker.

For every cycle, do as much of this loop as is justified while keeping each individual experiment under 15 minutes: reconstruct the task contract and current best; inspect the relevant official evaluator and data path; identify one concrete hypothesis or bottleneck; make a bounded code change or a faithful diagnostic; run focused tests plus a valid public-validation evaluation; compare GAUC, nDCG@5, and primary against the current best and official baseline; keep the best valid checkpoint; and record what was learned and what the next cycle should test. Prefer cheap faithful evidence before expensive runs. If an experiment fails, diagnose it and continue with the next useful cycle. Use fixed seeds and public validation only. Never claim a gain without the official evaluator.

Create or update concise run evidence under baseline_runs/ (not research_record state history) so the single-agent trajectory is auditable: cycle number, hypothesis, command, metrics, decision, and next action. Do not create immutable research State tags or promote unsupported results. At the end, leave the best code and evidence in the project and provide a final summary with the number of completed cycles, elapsed time, experiments, best public-validation metrics and deltas, tests run, and any blocker. Do not just describe possible work: perform the work now, and only finish when the stated stopping condition is met.
```

For a rerun, preserve the prompt text and change only the absolute project path
if the checkout has moved. The prompt intentionally measures a single direct
agent; adding delegation, other agents, or the research-agent control plane
would define a different benchmark.
