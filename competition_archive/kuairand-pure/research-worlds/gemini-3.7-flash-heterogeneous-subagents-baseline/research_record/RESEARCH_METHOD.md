# Research Method

This file is the canonical source for **how Scientist does good research inside one iteration**. Permissions, role authority, data access, and State ownership come from `SYSTEM_CONTRACT.md`.

The central loop is:

```text
observe the real system
        ↓
identify the limiting uncertainty / mechanism
        ↓
form or select one bottleneck
        ↓
compare plausible explanations
        ↓
choose the cheapest faithful discriminating evidence
        ↓
run + audit
        ↓
update beliefs and research memory
        ↓
retain only supported system changes
```

A bottleneck is an evidence-backed limiting mechanism, not merely a score gap or a promising technique.

## Research memory

Use the existing project artifacts for their intended meanings:

- `RESEARCH_RECORD.yaml`: active/closed bottlenecks, hypotheses, diagnostics, experiments, evidence, interventions.
- `EXPLORE.md`: actual observed data/source semantics.
- `ENGINEERING.md`: reusable execution, environment, machine, and diagnostic facts.
- `KNOWLEDGE.md`: verified external sources and reusable research knowledge.
- `STATE.yaml`: description of the currently materialized reusable State.

Mutable research memory and State versioning are separate. Git is not research chronology.

## Bootstrap the world before reasoning from it

Before forming a data-dependent hypothesis, make sure `EXPLORE.md` is grounded in real observations from the target data and source code. Verify the relevant:

- schema and feature meaning;
- official split semantics;
- row and label alignment;
- label availability/cutoff;
- time/order semantics;
- feature observation cutoff;
- leakage boundary;
- evaluator behavior when it affects interpretation.

Preserve output row order separately from temporal history order when both matter.

If a required semantic is unknown or contradictory, stop the dependent experiment and record the blocker. A generic or copied EDA is not evidence.

When `KNOWLEDGE.md` is empty or generic, seed only enough verified primary knowledge to make the landscape navigable: dataset/domain source, evaluator/benchmark source, baseline/reference implementation, and a small number of major method families when genuinely relevant. Stop once the landscape is useful; literature collection is not the research objective.

## Bottleneck formation

A candidate bottleneck is recorded as `forming` until evidence makes it actionable.

Before promoting a candidate to `active`:

1. State the reproducible symptom and affected metric/component/population.
2. Separate observed facts from mechanism interpretation.
3. List plausible competing explanations.
4. Define a bounded diagnostic question that can distinguish them.
5. Preregister the diagnostic protocol, expected observation, falsifier, controls, fidelity, seed/budget, and stop condition.
6. Run at least two orthogonal views when practical rather than relying on one ambiguous signal.
7. Audit leakage, evaluator artifacts, randomness, proxy fidelity, unfair controls, and alternative explanations.
8. Mark the bottleneck active only when evidence explains why it is more actionable than its alternatives.

Insufficiently supported candidates remain `forming` or are closed as rejected. Reopening a historical bottleneck requires new formation evidence rather than merely renewed interest.

## Hypotheses

A useful hypothesis is a concrete, falsifiable mechanism claim inside the active bottleneck. It should connect:

```text
mechanism
→ predicted observable pattern
→ distinguishing control
→ result that would weaken or falsify it
```

Do not substitute blind sweeps, seed fishing, validation-specific tweaks, or leaderboard-only tricks for a scientific hypothesis.

`RESEARCH_INTUITION.md` may inspire candidate hypotheses, but an intuition is not evidence. Translate it into a testable claim and judge that claim independently.

## Cheap faithful evidence

Respect the resource and runtime constraints declared in `PERSONAL.md` and the active coordination budget.

Prefer the **cheapest experiment or diagnostic that faithfully distinguishes the important competing explanations**. Cheap is valuable because it buys more learning per unit cost, not because low fidelity is automatically better.

Use:

- **Smoke** for syntax, schema, evaluator contracts, and tiny numerical sanity checks.
- **Medium** for lower-cost mechanism tests when a fixed subset/holdout preserves the relevant structure. Subsampling must preserve the evaluation metric's grouping unit (e.g. preserving complete group/user/query/session clusters) rather than raw row slicing.
- **Full** for confirmatory evidence when lower fidelity cannot preserve the mechanism or required statistical power.

Escalate fidelity only when cheaper evidence cannot answer the question. If no cheap proxy is scientifically faithful, say so and run the needed higher-fidelity experiment rather than optimizing a misleading proxy.

## Experiment discipline

Before each experiment begins, record:

- `protocol`: data/split, comparator/control, fidelity, seeds, budget, stop condition, and exact recipe;
- `expected_result`: the predicted observation and what would weaken/falsify the hypothesis.

Do not rewrite either field after seeing the result.

After execution, record separately:

- `actual_result`;
- `events` including errors, timeouts, retries, and recoveries;
- `evaluation` including fidelity, split, measured metrics, comparator State, and comparable improvement when available;
- `result_audit` covering leakage, evaluator artifacts, validation overfitting, randomness, proxy failure, unfair controls, and alternative explanations;
- `conclusion`: what the evidence changes about the hypothesis;
- resources actually consumed, leaving unknown values unknown.

An empirical effect may be real while its proposed causal explanation is wrong. Write conclusions after the audit, not before.

Preserve failed and negative experiments. A failed gate that resolves uncertainty is valid research progress.

## Gate before expensive confirmation

For a nontrivial mechanism, feature, objective, or sampling change, use a cheap faithful validation gate when one exists:

1. preregister the mechanism prediction and fixed gate criterion;
2. preregister the one confirmatory Full recipe that will run if the gate passes;
3. run the gate with an appropriate control;
4. if the gate fails, record the negative result and normally stop that hypothesis;
5. if it passes, run the preregistered confirmation rather than opening an unbounded sweep.

Gate and confirmation belong to the same bottleneck-bounded iteration. A quick first gate is not automatically the end of the iteration if a complementary test inside the same bottleneck is still high-value.

## One-iteration loop

One iteration stays inside one active bottleneck, or inside one bounded bottleneck-formation question when no active bottleneck is justified.

1. Read the current coordination input, `STATE.yaml`, research memory, `EXPLORE.md`, relevant `system/**`, evidence/logs, and State metadata needed for implementation ancestry.
2. Establish the current State baseline before touching State-controlled files. A worktree whose `system/**` and `STATE.yaml` match the named immutable State is a **legitimate materialized State** even when those files differ from `HEAD`. In Parallel, the context-recorded provisional parent is likewise a valid baseline.
3. Select the active bottleneck or one forming-bottleneck question. The **boundary follows that bottleneck**.
4. Identify the important competing explanations and choose the highest-information test that fits the declared budget, preferring the cheapest faithful evidence.
5. Record the protocol and expected result for each experiment before that experiment begins.
6. Execute the coherent scientific work needed inside the boundary. Multiple hypotheses, diagnostics, controls, and experiments are allowed when useful; do not switch bottlenecks mid-iteration.
7. Record actual results, audits, events, resources, conclusions, and reusable facts.
8. Decide which `system/**` changes, if any, deserve retention. Restore temporary or unsupported changes.
9. If retained `system/**` changes create a new State, update the matching `STATE.yaml`, update research-memory `resulting_state` references, and **commit only the retained `system/**` version plus `STATE.yaml`**. Do not create a Git commit merely because research memory changed.
10. Create the immutable State through `research-agent state create` in Serial mode. Parallel branches defer immutable State tags to promotion.
11. Give a concise execution reflection and return control.

A purely diagnostic iteration that leaves `system/**` unchanged updates research memory and creates no State commit.

## Reusing and creating States

Do not create a missing `STATE.yaml` as a **standalone placeholder**.

If there is no valid State history, establish an actual reusable implementation under `system/**`, write the matching initial `STATE.yaml`, commit the State-controlled files together, then create the immutable first State.

If State history already exists but `STATE.yaml` is missing or inconsistent, report a State-integrity problem rather than inventing a replacement.

To reuse a historical State, do not use whole-repository checkout/reset. Use:

```bash
research-agent state materialize --target <project> <state-id>
```

This changes only the State-controlled implementation/descriptor while mutable research memory stays at current research time.

A new State is created only after retained `system/**` plus matching `STATE.yaml` are committed together:

```bash
research-agent state create --target <project> <state-id>
```

Historical State records are immutable. New observations about an old State go into current research memory rather than rewriting the historical State snapshot.

## External knowledge

Search externally only when existing project knowledge is insufficient for the current bottleneck or its formation. Prefer primary sources, open the relevant material, summarize in your own words, and record how it informs a concrete hypothesis or diagnostic rather than collecting citations without a research decision.

## Closing a bottleneck

Close a bottleneck only after reviewing its complete evidence and recording:

- what was learned;
- which conclusions future work must respect;
- where reusable engineering or external knowledge was transferred;
- what remains uncertain;
- why another experiment in this bottleneck now has low expected scientific value.

Closure is not “the score stopped increasing.” It is a judgment that continued work on this bottleneck is no longer a good use of research effort given the evidence and available alternatives.
