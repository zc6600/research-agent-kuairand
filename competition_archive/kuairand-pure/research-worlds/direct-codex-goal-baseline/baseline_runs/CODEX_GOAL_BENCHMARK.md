# Codex Goal benchmark: `direct-codex-goal-baseline`

## 1. What this benchmark measures

This is the agent-system baseline, not a recommendation-model baseline. It
measures one direct Codex agent running autonomously for a long horizon in the
`direct-codex-goal-baseline` child project. The run had no META layer, Scientist layer,
delegation, subagent, or research-agent control plane.

The KuaiRand model and its metrics are the task used to observe the agent's
work. Popularity and FM are task-model controls; they are not the definition of
the agent-system baseline. A future system with multiple roles or agents must
be compared as a separate system-level benchmark.

This file is a frozen record of the run on 2026-08-30. New runs should append a
new benchmark ID and must not overwrite this record.

## 2. Result at a glance

| Metric | Codex Goal best validation | Published validation reference | Delta |
| --- | ---: | ---: | ---: |
| GAUC | `0.6712470735` | `0.6674` | `+0.0038470735` |
| nDCG@5 | `0.5376594671` | `0.5357` | `+0.0019594671` |
| Primary = mean(GAUC, nDCG@5) | `0.6044532703` | `0.6016` | `+0.0028532703` |

The selected checkpoint was the highest completed public-validation primary.
No hidden-test score was used for model selection or claimed as a result.

## 3. Run identity and boundary

| Field | Recorded value |
| --- | --- |
| Benchmark ID | `codex-goal-2026-08-30-v1` |
| Target project | `/Users/frank/github_project/Good4AI/research_agent/projects/direct-codex-goal-baseline` |
| Run mode | Interactive Codex CLI with a `/goal` prompt |
| Measured runner | One direct Codex agent |
| Model | `gpt-5.6-luna` |
| Reasoning effort | High-capacity setting |
| Codex CLI | `0.151.0` |
| Codex session | `01a05144-81a9-79e1-a4ab-29ecd23e287d` |
| Starting state | Clean public-validation baseline, commit `c5a33f2`, with the API/CLI baseline worktree present |
| Sandbox | `workspace-write` |
| Approval policy | `never` |
| Hidden-test data | Not used |
| Subagents/delegation | Not used |
| Research-agent invocation | Not used |
| Data root | `competition_data/data` |
| Official evaluator | `starter_kit/evaluate.py` |
| Fixed label | `long_view` |

The normalized launch record used the `gpt-5.6-luna` agent with a
high-capacity reasoning setting in the `direct-codex-goal-baseline` child
project, with a workspace-write sandbox and never-ask approval policy.

The exact Goal prompt is frozen in
[CODEX_GOAL_PROMPT.md](CODEX_GOAL_PROMPT.md). The prompt explicitly required
the agent to remain in the child project, use curated public data, iterate
over experiments, retain the best valid checkpoint, and stop only at the
specified budget/convergence condition. This matches the `/goal` contract in
the official OpenAI long-running Codex guidance: the Goal is the completion
criterion for the same interactive session, rather than a one-shot request.

## 4. Time and stopping rule

The timestamps below are UTC, as recorded by the parent runner and session
transcript. The local timezone for the workspace is Asia/Singapore (UTC+8).

| Event | UTC timestamp |
| --- | --- |
| Codex process started | `2026-08-30T06:03:58.834Z` |
| Goal submitted | `2026-08-30T06:04:33.214Z` |
| Final agent message | `2026-08-30T06:55:18.708Z` |
| PTY/process closed | `2026-08-30T07:01:53.407Z` |

Recorded durations:

- Process wall time: `3,474.573` seconds, or `57m 54.573s`. This includes the
  terminal lifetime after the final agent message while the PTY was drained.
- Goal submission to final agent message: `3,045.494` seconds, or
  `50m 45.494s`.
- The Goal controller's structured completion record reports
  `timeUsedSeconds=2,920`, or `48m 40s` of Goal usage.
- The run evidence recorded approximately `29m` of active tool time. This is a
  tool-execution measure, not wall time; model reasoning, file inspection, and
  terminal idle/drain time are not interchangeable with it.

The hard budget was 60 minutes or 12 substantial cycles, with each individual
experiment intended to stay below 15 minutes. The run completed 11 substantial
cycles. It stopped after the validation frontier had been reached and at least
three consecutive meaningful full public-validations failed to improve the
primary by more than `epsilon = 0.002`. The 60-minute and 12-cycle limits were
not reached, and there was no external blocker.

## 5. Evaluation protocol

The agent trained only on the curated train rows under `competition_data/data`
and evaluated with the organizer's official evaluator on the curated public
validation split. Each claimed score is therefore an official public score,
not a smoke-test proxy.

The reported metrics were:

- `GAUC`
- `nDCG@5`
- `primary = mean(GAUC, nDCG@5)`

The published references used for context were:

| Reference | GAUC | nDCG@5 | Primary | Use |
| --- | ---: | ---: | ---: | --- |
| Published public validation | `0.6674` | `0.5357` | `0.6016` | Main comparison reference |
| Published hidden test | `0.6610` | `0.5282` | `0.5946` | Context only; not accessed |
| Popularity control | `0.6387257649` | `0.5227180938` | `0.5807219293` | Local sanity/control model |
| Synthetic smoke | `1.0` | `1.0` | `1.0` | 4 rows, 2 users; not a task score |

The hidden-test reference is recorded so later reports do not accidentally
compare a public result against the wrong number. It was not available to the
agent and did not affect checkpoint selection.

## 6. Best checkpoint

The best public-validation checkpoint used the following task model:

| Parameter | Value |
| --- | --- |
| Features | Five official FM fields |
| Pair construction | One same-user train negative per positive |
| Factors | `8` |
| Learning rate | `0.00025` |
| Epochs | `40` |
| Batch size | `8192` |
| Early-stopping patience | `4` |
| Seed | `0` |

The exact reproducing command was:

```bash
.venv/bin/python -m system.cli evaluate-fm-pairwise \
  --data-dir competition_data/data --split valid
```

The resulting official metrics were `GAUC=0.6712470735`,
`nDCG@5=0.5376594671`, and `primary=0.6044532703`.

## 7. Complete recorded experiment trajectory

The table includes every recorded public-validation outcome from the 11-cycle
trajectory. A dash means the cycle evidence did not preserve that component
metric; it is intentionally not reconstructed from rounded or missing data.
Primary deltas are measured against the published validation primary `0.6016`.

| Cycle | Hypothesis / variant | GAUC | nDCG@5 | Primary | Delta vs `0.6016` | Decision |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Official FM baseline checkpoint | `0.6671326322` | `0.5358048805` | `0.6014687564` | `-0.0001312436` | Establish baseline; continue |
| 2 | Tab-rate blend diagnostic | `0.6675545637` | `0.5360836719` | `0.6018191178` | `+0.0002191178` | Diagnostic only; not retained |
| 2 | Group-rank diagnostic (best recorded) | — | — | `0.601705` | `+0.000105` | Not better than frontier |
| 3 | Pairwise FM, factors `16`, lr `0.001` | `0.6702483708` | `0.5372679854` | `0.6037581781` | `+0.0021581781` | Retain pairwise direction |
| 4 | Pairwise, seed `1` | `0.6696339610` | `0.5372469512` | `0.6034404561` | `+0.0018404561` | Seed stability check |
| 4 | Pairwise, seed `2` | `0.6695923645` | `0.5370549740` | `0.6033236693` | `+0.0017236693` | Seed stability check |
| 5 | Pairwise, lr `0.0005` | `0.6704166044` | `0.5373013575` | `0.6038589810` | `+0.0022589810` | Small gain; continue tuning |
| 5 | Pairwise, lr `0.002` | `0.6688596654` | `0.5364221826` | `0.6026409240` | `+0.0010409240` | Reject higher lr |
| 6 | Two same-user negatives per positive | `0.6702011069` | `0.5371198262` | `0.6036604666` | `+0.0020604666` | Reject; below frontier |
| 7 | Pairwise, factors `8` | `0.6710279481` | `0.5374375032` | `0.6042327257` | `+0.0026327257` | Retain; new frontier |
| 7 | Pairwise, factors `32` | `0.6696778442` | `0.5371252408` | `0.6034015425` | `+0.0018015425` | Reject |
| 8 | Pairwise, factors `8`, lr `0.00025` | `0.6712470735` | `0.5376594671` | `0.6044532703` | `+0.0028532703` | Final best checkpoint |
| 8 | Pairwise, factors `8`, lr `0.00075` | — | — | `0.6041803564` | `+0.0025803564` | Below best |
| 8 | User-tab auxiliary blend | `0.6704557381` | `0.5373354569` | `0.6038955975` | `+0.0022955975` | Reject |
| 8 | Video-tab auxiliary blend | `0.6705311633` | `0.5369507543` | `0.6037409588` | `+0.0021409588` | Reject |
| 9 | Auxiliary `is_click`, weight `0.1` | `0.6706593093` | `0.5374222306` | `0.6040407700` | `+0.0024407700` | Below best |
| 10 | Hard-negative pool `1` | — | — | `0.5133061084` | `-0.0882938916` | Reject; diagnose |
| 10 | Hard-negative pool `5` | — | — | `0.5334015939` | `-0.0681984061` | Reject |
| 10 | Hard-negative pool `20` | — | — | `0.5935823444` | `-0.0080176556` | Reject |
| 10 | Hard-negative random control | — | — | `0.6038737377` | `+0.0022737377` | Below best |
| 11 | Listwise softmax, lr `0.001` | `0.6471060952` | `0.5262492248` | `0.5866776600` | `-0.0149223400` | Reject |
| 11 | Listwise softmax, lr `0.005` | `0.6569370681` | `0.5299757502` | `0.5934564092` | `-0.0081435908` | Reject; stop convergence loop |

The individual cycle reports remain available in this directory, from
`cycle_01_baseline.md` through `cycle_11_listwise.md`. They contain the local
hypothesis, commands, observations, and next action for each cycle.

## 8. What the trajectory established

The most useful improvement was changing from the official pointwise FM
checkpoint to pairwise training. Pairwise factors `16` first moved primary to
`0.6037581781`; reducing capacity to factors `8` and then lowering the learning
rate to `0.00025` produced the final `0.6044532703`.

The trajectory also tested seed stability, learning rate, factor capacity,
additional negatives, tab-rate and auxiliary feedback blends, hard-negative
mining, and listwise softmax. None of those later directions exceeded the
factors-8/lr-0.00025 checkpoint. The hard-negative and listwise variants were
materially worse, so they are useful negative results for future experiments.

## 9. Token and usage ledger

The following values are from the Codex CLI shutdown usage line and the final
session `token_count` snapshot. The CLI's reported total excludes cache-read
tokens; the raw snapshot's input field includes them.

| Quantity | Tokens | Interpretation |
| --- | ---: | --- |
| Goal controller `tokensUsed` | `271,750` | Structured `/goal` completion field |
| Non-cache input | `218,767` | Prompt/context input excluding cache-read tokens |
| Cache-read input | `10,945,536` | Reused context reported separately by the CLI |
| Cache-write input | `0` | No cache-write input recorded |
| Output | `56,419` | Total output; includes reasoning output |
| Reasoning output | `24,747` | Subset of output; do not add again |
| Reported total excluding cache | `275,186` | `218,767 + 56,419` |
| Raw input including cache | `11,164,303` | `218,767 + 10,945,536` |
| Raw total including cache | `11,220,722` | `11,164,303 + 56,419`; accounting value, not a price |

There is no reliable per-cycle token breakdown in the recorded run. Therefore,
two whole-run snapshots are retained explicitly: `271,750` from the Goal
controller's completion event and `275,186` from the final CLI usage line
excluding cache-read tokens. They represent different accounting observation
points; do not add them or treat their difference as a separate experiment.
The comparable baseline cost is one named whole-run ledger, not an invented
average per cycle. No model price or currency cost was recorded, so this
benchmark does not claim a dollar cost.

For comparison, an older one-shot `codex exec` artifact under
`.git/research-agent-baseline/25e776ec1f30434bbd7037dcf3032ff5/` reports
`1,001,055` total tokens (`979,065` input, `21,990` output, `12,863`
reasoning, `897,536` cache-read). It is not this Goal run: it ended after a
single direct optimization pass and must be excluded from the Goal benchmark
ledger.

## 10. Verification performed at the end

The final agent report recorded the following checks:

- 5 API tests;
- Python compilation;
- synthetic smoke evaluation;
- CLI help and the final default CLI path;
- curated-data row counts and key checks;
- a curated-only path guard;
- `git diff --check`;
- reproduction of the best primary with the default pairwise CLI.

The synthetic result was perfect (`1.0` on all three metrics), but it used only
4 rows and 2 users and is explicitly not part of the public benchmark score.

## 11. Fair comparison recipe

To compare a new agent or agent system against this baseline:

1. Start from a fresh checkout at the same clean public-validation baseline /
   `c5a33f2` starting state, with the same curated data and official
   starter/evaluator. Do not
   start from this post-run tree, which already contains the selected
   pairwise implementation and evidence.
2. Use the same project boundary and the same frozen Goal prompt unless the
   experiment is intentionally testing a different prompt. Record any prompt
   change as a benchmark variant.
3. Keep the model, reasoning effort, sandbox, approval policy, 60-minute/12-
   cycle budget, and per-experiment limit fixed when measuring agent behavior.
4. Report the whole-run wall time and token ledger, including non-cache input,
   cache-read input, output, reasoning subset, and the accounting convention
   for the total.
5. Use the same official public evaluator and report GAUC, nDCG@5, primary, and
   deltas against the published validation reference. Do not use hidden-test
   data for tuning or selection.
6. For a multi-role research-agent system, compare the complete system run
   (all role tokens, orchestration, and wall time) against this complete
   single-agent run. Role-level token tables can be added as secondary
   diagnostics, but must not replace the whole-system budget.

This procedure prevents the recommender-model score from being mistaken for
the agent-system result and prevents a stronger post-run codebase from being
silently given to one side of the comparison.

## 12. Artifacts and caveats

- [Frozen Goal prompt](CODEX_GOAL_PROMPT.md)
- [Machine-readable ledger](CODEX_GOAL_BENCHMARK.json)
- [Final run summary](FINAL.md)
- [Cycle evidence](.)
- Raw Codex session transcript:
  `/Users/frank/.codex/sessions/2026/08/30/rollout-2026-08-30T14-03-59-01a05144-81a9-79e1-a4ab-29ecd23e287d.jsonl`

The later code audit identified an API score-length guard issue and FM
hyperparameter-validation issues. They do not invalidate the recorded
full-length official scores, but a future harness should add those guards
before treating malformed inputs or invalid hyperparameters as benchmark
failures. The complete audit is separate from this frozen run record; this
document intentionally preserves what the agent actually ran and measured.
