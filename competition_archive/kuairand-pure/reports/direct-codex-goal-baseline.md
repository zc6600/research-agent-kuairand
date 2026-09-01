# Direct Codex Agent Goal Baseline

## Executive summary

This document is the report-ready record of the Codex Goal control run for
KuaiRand-Pure. It measures one direct Codex agent working autonomously inside
the task project for a bounded long-horizon run. It is an agent-system
baseline, not a claim that the recommendation model itself is a complete
baseline for the competition.

The run reproduced the official pointwise FM checkpoint, discovered a better
within-user pairwise objective, and then refined its capacity and learning
rate. The final selected checkpoint reached a public-validation primary of
0.6044532703, which is 0.0028532703 above the published validation reference
of 0.6016. No hidden-test score was used for selection or reported as the
result of this run.

> Report-ready summary: A single direct Codex Goal agent, without META,
> Scientist, delegation, subagents, or the Research Agent control plane,
> completed 11 substantial public-validation cycles in under one hour. It
> improved the reproduced pointwise FM checkpoint mainly by switching to
> within-user pairwise training, then selecting eight latent factors and a
> learning rate of 0.00025. Its best public-validation result was
> GAUC=0.6712470735, nDCG@5=0.5376594671, and primary=0.6044532703, or
> +0.0028532703 primary over the published validation reference.

> Audit note: The independent process and implementation audit is recorded in
> [`baseline-protocol-audit.md`](baseline-protocol-audit.md). Until the launcher/provenance and
> pair-construction findings there are resolved, this score should be treated as
> a provisional public-validation result rather than independent confirmation.

## 1. What this baseline measures

The measured system is one direct Codex agent operating in Goal mode. The
baseline deliberately excludes the mechanisms that distinguish Research Agent
from a single coding agent:

- no META layer;
- no Scientist layer;
- no delegation or subagents;
- no Research Agent invocation;
- no hidden-test data;
- no cross-project or parent-workspace access.

The KuaiRand recommendation model is the task through which agent behavior is
observed. Popularity, pointwise FM, and pairwise FM are task-model controls
inside this agent-system benchmark; they must not be confused with the
definition of the agent baseline.

This is a frozen record of the run on 2026-08-30. A future rerun should use a
new benchmark identifier and append a new record rather than overwrite this
one.

## 2. Headline result

| Metric | Codex Goal best public validation | Published validation reference | Delta |
| --- | ---: | ---: | ---: |
| GAUC | 0.6712470735 | 0.6674 | +0.0038470735 |
| nDCG@5 | 0.5376594671 | 0.5357 | +0.0019594671 |
| Primary = mean(GAUC, nDCG@5) | 0.6044532703 | 0.6016 | +0.0028532703 |

The best checkpoint is approximately a 0.474% relative improvement in primary
over the published validation reference. The direct comparison with the
reproduced pointwise FM checkpoint is:

| Comparison | GAUC | nDCG@5 | Primary |
| --- | ---: | ---: | ---: |
| Cycle 1 pointwise FM | 0.6671326322 | 0.5358048805 | 0.6014687564 |
| Best pairwise FM | 0.6712470735 | 0.5376594671 | 0.6044532703 |
| Best minus Cycle 1 | +0.0041144413 | +0.0018545866 | +0.0029845139 |

The improvement is a public-validation result. The published hidden-test
numbers are retained below as context only; the agent did not access them.

## 3. Run identity and experimental boundary

| Field | Recorded value |
| --- | --- |
| Benchmark ID | `codex-goal-2026-08-30-v1` |
| Archived target project | `competition_archive/kuairand-pure/research-worlds/direct-codex-goal-baseline` |
| Run mode | Interactive Codex CLI with a /goal prompt |
| Measured runner | One direct Codex agent |
| Model | gpt-5.6-luna |
| Reasoning effort | high-capacity setting |
| Codex CLI | 0.151.0 |
| Starting point | clean reproducible baseline |
| Sandbox | workspace-write |
| Approval policy | never |
| Hidden-test data | Not used |
| Subagents or delegation | Not used |
| Research Agent invocation | Not used |
| Hard budget | 60 minutes or 12 substantial cycles |
| Completed cycles | 11 substantial cycles |
| Individual experiment target | Under 15 minutes |
| Stopping epsilon | 0.002 primary |

The run started from the clean recorded baseline. The final
post-run tree contains the selected pairwise implementation and evidence, so a
fair rerun must start from a fresh checkout of the recorded starting state.

The launch used the Codex Goal interface with `gpt-5.6-luna`, workspace-write
sandboxing, no approval prompts, and a 60-minute budget.

The exact frozen Goal prompt is preserved in the local raw run record. Its
essential contract was to stay inside the child project, use only curated
public data and the official evaluator, iterate until the budget or
convergence rule, keep the best valid checkpoint, and record every meaningful
cycle.

## 4. Time, stopping rule, and accounting

The timestamps below are UTC.

| Event | Timestamp |
| --- | --- |
| Codex process started | 2026-08-30 06:03:58.834 |
| Goal submitted | 2026-08-30 06:04:33.214 |
| Final agent message | 2026-08-30 06:55:18.708 |
| PTY/process closed | 2026-08-30 07:01:53.407 |

| Duration measure | Value | Interpretation |
| --- | ---: | --- |
| Process wall time | 3,474.573 s (57m 54.573s) | Includes terminal drain after the final message |
| Goal to final message | 3,045.494 s (50m 45.494s) | Interactive Goal session |
| Goal controller time | 2,920 s (48m 40s) | Structured Goal completion record |
| Recorded active tool time | Approximately 29m | Tool execution only; not wall time |

The run did not reach the 60-minute or 12-cycle hard limit. It stopped after
the best checkpoint had been found and at least three consecutive meaningful
full public-validation evaluations failed to improve primary by more than
epsilon=0.002. There was no external blocker.

## 5. Evaluation protocol

The agent trained only on curated train rows under competition_data/data and
used the official evaluator on the curated public validation split. Checkpoint
selection used the highest completed public-validation primary.

The reported metrics were:

- GAUC;
- nDCG@5;
- primary = mean(GAUC, nDCG@5).

| Reference | GAUC | nDCG@5 | Primary | Use |
| --- | ---: | ---: | ---: | --- |
| Published public validation | 0.6674 | 0.5357 | 0.6016 | Main comparison reference |
| Published hidden test | 0.6610 | 0.5282 | 0.5946 | Context only; not accessed |
| Popularity control, prior=20 | 0.6387257649 | 0.5227180938 | 0.5807219293 | Local sanity/control model |
| Synthetic smoke | 1.0 | 1.0 | 1.0 | Four rows and two users; not a task score |

The synthetic score is explicitly excluded from all benchmark claims.

## 6. Best checkpoint

The selected task model used five official FM fields and sampled one same-user
training negative for each positive.

| Parameter | Value |
| --- | --- |
| Pair construction | One same-user train negative per positive |
| Latent factors | 8 |
| Learning rate | 0.00025 |
| Epochs | 40 |
| Batch size | 8192 |
| Early-stopping patience | 4 |
| Seed | 0 |

The reproducing command was:

~~~bash
.venv/bin/python -m system.cli evaluate-fm-pairwise \
  --data-dir competition_data/data --split valid
~~~

The resulting official public-validation metrics were
GAUC=0.6712470735, nDCG@5=0.5376594671, and primary=0.6044532703.

## 7. Complete experiment trajectory

The table preserves every recorded public-validation outcome. A dash means
that the cycle record did not preserve that component metric; it is not
reconstructed from rounded or missing data. Primary deltas are against the
published validation primary of 0.6016.

| Cycle | Variant | GAUC | nDCG@5 | Primary | Delta vs 0.6016 | Decision |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Official pointwise FM checkpoint | 0.6671326322 | 0.5358048805 | 0.6014687564 | -0.0001312436 | Establish baseline |
| 2 | Train-only tab-rate blend diagnostic | 0.6675545637 | 0.5360836719 | 0.6018191178 | +0.0002191178 | Diagnostic only; not retained |
| 2 | Group-rank diagnostic, best recorded | — | — | 0.6017050000 | +0.0001050000 | Below frontier |
| 3 | Pairwise FM, factors 16, lr 0.001 | 0.6702483708 | 0.5372679854 | 0.6037581781 | +0.0021581781 | Retain pairwise direction |
| 4 | Pairwise, seed 1 | 0.6696339610 | 0.5372469512 | 0.6034404561 | +0.0018404561 | Seed stability check |
| 4 | Pairwise, seed 2 | 0.6695923645 | 0.5370549740 | 0.6033236693 | +0.0017236693 | Seed stability check |
| 5 | Pairwise, factors 16, lr 0.0005 | 0.6704166044 | 0.5373013575 | 0.6038589810 | +0.0022589810 | Small gain; continue |
| 5 | Pairwise, factors 16, lr 0.002 | 0.6688596654 | 0.5364221826 | 0.6026409240 | +0.0010409240 | Reject higher lr |
| 6 | Two same-user negatives per positive | 0.6702011069 | 0.5371198262 | 0.6036604666 | +0.0020604666 | Reject; below frontier |
| 7 | Pairwise, factors 8 | 0.6710279481 | 0.5374375032 | 0.6042327257 | +0.0026327257 | New frontier |
| 7 | Pairwise, factors 32 | 0.6696778442 | 0.5371252408 | 0.6034015425 | +0.0018015425 | Reject |
| 8 | Pairwise, factors 8, lr 0.00025 | 0.6712470735 | 0.5376594671 | 0.6044532703 | +0.0028532703 | Final best checkpoint |
| 8 | Pairwise, factors 8, lr 0.00075 | — | — | 0.6041803564 | +0.0025803564 | Below best |
| 8 | User-tab auxiliary blend | 0.6704557381 | 0.5373354569 | 0.6038955975 | +0.0022955975 | Reject |
| 8 | Video-tab auxiliary blend | 0.6705311633 | 0.5369507543 | 0.6037409588 | +0.0021409588 | Reject |
| 9 | Auxiliary is_click, weight 0.1 | 0.6706593093 | 0.5374222306 | 0.6040407700 | +0.0024407700 | Below best |
| 10 | Hard-negative pool 1 | — | — | 0.5133061084 | -0.0882938916 | Reject; diagnose |
| 10 | Hard-negative pool 5 | — | — | 0.5334015939 | -0.0681984061 | Reject |
| 10 | Hard-negative pool 20 | — | — | 0.5935823444 | -0.0080176556 | Reject |
| 10 | Hard-negative random control | — | — | 0.6038737377 | +0.0022737377 | Below best |
| 11 | Listwise softmax, lr 0.001 | 0.6471060952 | 0.5262492248 | 0.5866776600 | -0.0149223400 | Reject |
| 11 | Listwise softmax, lr 0.005 | 0.6569370681 | 0.5299757502 | 0.5934564092 | -0.0081435908 | Reject; stop convergence loop |

## 8. Analysis and scientific interpretation

### 8.1 The main gain came from objective alignment

The Cycle 1 pointwise FM checkpoint reproduced the published reference closely:
primary 0.6014687564 versus 0.6016. The first substantive improvement came
from sampled within-user pairwise training, which raised primary to
0.6037581781. This is consistent with the evaluator's ranking-oriented
structure: the agent changed the training signal from independent point
prediction to relative ordering among impressions from the same user.

The final checkpoint improved primary by 0.0029845139 over the reproduced
pointwise checkpoint. The strongest evidence in this run therefore supports
the objective change, not merely a larger model.

### 8.2 The best capacity was smaller, not larger

At the same pairwise direction, factors=8 reached primary 0.6042327257,
whereas factors=32 reached 0.6034015425. The result suggests that the
pointwise-optimal capacity did not transfer directly to the pairwise
objective. In this data and training regime, a smaller representation was
better behaved on public validation.

### 8.3 Learning-rate refinement mattered after the capacity change

With factors=8, lowering the learning rate to 0.00025 produced the final
0.6044532703. The nearby 0.00075 variant reached 0.6041803564, so the final
refinement was measurable but modest (-0.0002729139 relative to the best). At
factors=16, the higher 0.002 rate fell to 0.6026409240. The trajectory
therefore supports an interaction between objective, capacity, and optimization
schedule.

### 8.4 More negatives were not automatically better

Two same-user negatives per positive reached 0.6036604666, below the
one-negative factors=16 result of 0.6038589810. This rejects the simple
assumption that more pairwise comparisons necessarily improve ranking quality.
The useful conclusion is conditional: sampling density must be tuned together
with the optimizer and model capacity.

### 8.5 Additional features and auxiliary feedback did not beat the frontier

The user-tab, video-tab, and auxiliary is_click variants all remained below
0.6044532703. The best auxiliary result was is_click with weight 0.1 at
0.6040407700. In this run, the five official FM fields plus the pairwise
training formulation were a better-controlled choice than adding correlated
feedback or explicit crosses.

### 8.6 Hard-negative mining and listwise training were useful negative results

Hard-negative mining was strongly unstable: primary fell to 0.5133061084 with
pool=1, 0.5334015939 with pool=5, and 0.5935823444 with pool=20. The random
control recovered to 0.6038737377 but still did not approach the frontier.
This points to a mismatch or instability in the hard-negative construction,
not evidence that difficult negatives are universally unhelpful.

Listwise softmax also underperformed in the tested implementation. The best of
the two recorded listwise settings reached only 0.5934564092. Within this
task, data path, and evaluator, sampled pairwise training was the better
alignment.

### 8.7 The run demonstrates autonomous search, not general superiority

The agent performed baseline reproduction, hypothesis generation, code changes,
official evaluation, checkpoint retention, negative-result diagnosis, and
stopping-rule application without the Research Agent control plane. That is
the agentic result being measured.

The model score is still a single public-validation outcome from one direct
agent run. It should be used as a control when comparing complete systems. A
Research Agent system must be compared using whole-system wall time and token
usage, including orchestration and all roles, rather than only comparing the
best task-model score.

## 9. Token and resource ledger

The run recorded two valid token accounting snapshots. They are different
observation points and must not be added together.

| Quantity | Tokens | Interpretation |
| --- | ---: | --- |
| Goal controller tokensUsed | 271,750 | Structured Goal completion field |
| Non-cache input | 218,767 | Input excluding cache-read tokens |
| Cache-read input | 10,945,536 | Reused context reported separately |
| Cache-write input | 0 | No cache-write input recorded |
| Output | 56,419 | Total output, including reasoning output |
| Reasoning output | 24,747 | Subset of output; do not add again |
| Reported total excluding cache | 275,186 | Non-cache input plus output |
| Raw input including cache | 11,164,303 | Non-cache input plus cache-read input |
| Raw total including cache | 11,220,722 | Raw input including cache plus output |

No per-cycle token breakdown or currency cost was recorded. For system
comparisons, use one whole-run accounting convention consistently and report
the convention explicitly. The older one-shot Codex exec artifact with
1,001,055 total tokens belongs to a different run and is excluded from this
Goal benchmark; it must not be merged into the Goal ledger.

## 10. Verification and caveats

The final run recorded these checks:

- five API tests;
- Python compilation;
- synthetic smoke evaluation;
- CLI help and the final default CLI path;
- curated-data row-count and key checks;
- a curated-only path guard;
- git diff --check;
- reproduction of the best primary with the default pairwise CLI.

The later code audit identified an API score-length guard issue and FM
hyperparameter-validation issues. Those issues do not invalidate the recorded
full-length official scores, but a future benchmark harness should add the
guards before treating malformed inputs or invalid hyperparameters as
benchmark failures.

The public-validation selection rule creates a model-selection bias if the same
split is reused across many cycles. This run reports that fact rather than
claiming hidden-test generalization. The published hidden-test reference is
context only and was not available to the agent.

## 11. Fair comparison recipe

To compare another agent or agent system with this control:

1. Start from a fresh checkout of the clean recorded baseline, with the same
   curated data and official starter/evaluator. Do not start from the post-run
   pairwise tree.
2. Use the same project boundary and frozen Goal prompt, or record any prompt
   change as a separate benchmark variant.
3. Keep the model, reasoning effort, sandbox, approval policy, 60-minute/12-
   cycle budget, and per-experiment limit fixed.
4. Report whole-run wall time and the complete token ledger, including the
   cache accounting convention.
5. Use the official public evaluator and report GAUC, nDCG@5, primary, and
   deltas against the published validation reference.
6. Exclude hidden-test data from tuning and checkpoint selection.
7. For a multi-role research system, include all role and orchestration costs
   in the whole-system comparison. Role-level tables are secondary diagnostics.

This recipe keeps the task-model score separate from the agent-system result
and prevents a stronger post-run codebase from being silently given to one
side.

## 12. Source artifacts

The report was compiled from the original local Codex Goal run record under
competition_archive/kuairand-pure/research-worlds/direct-codex-goal-baseline/baseline_runs/. The source record
contains:

- CODEX_GOAL_BENCHMARK.md, the human-readable ledger;
- CODEX_GOAL_BENCHMARK.json, the machine-readable ledger;
- CODEX_GOAL_PROMPT.md, the frozen Goal prompt;
- FINAL.md, the final checkpoint summary;
- cycle_01_baseline.md through cycle_11_listwise.md, the per-cycle evidence.

The raw session transcript is intentionally treated as local execution
evidence rather than a public report artifact. The normalized figures above
are the values to cite in the competition or research report.
