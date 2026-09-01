# Research Method

This file describes lightweight principles for good research. It is **not** a mandatory reasoning workflow and should not compete with the real task objective.

The Scientist should optimize the valid task/evaluator using its own judgment. The method exists to help when useful, not to create a second proxy objective such as “follow the research process correctly.” Task-specific benchmark tactics belong in `OPTIMIZE.md`, not here.

A good default loop is:

```text
understand the real task/data/evaluator
        ↓
identify a worthwhile question, opportunity, or hypothesis
        ↓
run the most informative practical experiment
        ↓
measure with valid evidence
        ↓
update beliefs and implementation
        ↓
continue, pivot, or stop
```

The Scientist may skip, reorder, or repeat these steps when the task demands it.

## Shared research progress

A fresh Scientist is cognitively fresh, not scientifically blank. The previous session's hidden reasoning trajectory is discarded, while explicit research progress remains available in the project.

The persistent research world is split by purpose:

- `RESEARCH_BRIEF.md`: META-maintained concise descriptive handoff for a fresh Scientist.
- `RESEARCH_RECORD.yaml`: META-maintained complete experiment ledger.
- `EXPLORE.md`: shared durable data, evaluator, source, split, timing, and leakage semantics.
- `OPTIMIZE.md`: shared durable task-specific optimization implications derived from official task/evaluator mechanics.
- `ENGINEERING.md`: shared reusable execution, environment, machine, and implementation facts.
- `KNOWLEDGE.md`: shared verified reusable external knowledge.
- `RESEARCH_INTUITION.md`: META-maintained fallible scientific intuition accumulated across sessions.
- `DO_BETTER.md`: META-maintained fallible research-process learning accumulated across sessions.
- `reports/`: append-only free-form Scientist session reports.
- experiment logs/results: raw evidence beneath prose summaries.
- `STATE.yaml`: META-authored description/provenance of the currently materialized reusable implementation.
- `system/**`: Scientist-authored executable implementation.

META may initialize or curate `EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md`; Scientist may also update them directly while researching. They are shared environment memory, not exclusive-role files.

Scientist reports are deliberately unstructured. A Scientist writes what it considers worth leaving behind from its session; there is no required report template, checklist, or field set. Reports are never rewritten by META or a later Scientist. The maintained memory stack is the normal cold-start handoff; historical reports are deeper provenance to inspect when a summary is insufficient, worth challenging, or linked from the current State.

These artifacts have different epistemic roles. Intuition and process lessons are progress, but they are not facts or mandatory instructions. A fresh Scientist may challenge any summary or fallible memory by inspecting the Record, a State-linked report, other prior reports, raw evidence, source, or evaluator directly.

Mutable research memory and State versioning are separate. Git is not research chronology.

## Ground the world before depending on it

Before making a data-dependent claim, inspect enough of the real data and evaluator to understand the semantics that materially affect the experiment. Keep `EXPLORE.md` current for facts such as schema/feature meaning, official split semantics, ordering/time semantics, leakage boundaries, or evaluator behavior when those facts matter.

Do not turn “EDA” into a ceremony. Inspect what is needed to avoid optimizing a misunderstood world. Unknown facts may remain unknown until a scientific decision actually depends on them.

When an observed task/evaluator fact has a durable consequence for how this particular benchmark should be optimized, record that implication in `OPTIMIZE.md` rather than turning it into a universal method rule.

## Hypotheses without a hypothesis bureaucracy

Hypotheses are valuable because fresh Scientists need to know why experiments were run and what the results mean.

For a substantive hypothesis-driven experiment, make the working hypothesis explicit before or as the experiment is run:

```text
why this might matter
→ what change is being tested
→ what observation would strengthen or weaken the idea
```

Exploratory experiments are also legitimate. If the purpose is simply to learn whether a broad direction has signal, record it as exploratory rather than manufacturing a causal hypothesis after seeing the result.

There is no required bottleneck lifecycle, no forming/active/closed state machine, and no requirement that a session remain inside one named bottleneck. A Scientist may use the concept of a bottleneck when it improves reasoning, but it is not part of the control protocol.

## Experiments

A meaningful experiment should leave enough evidence for another Scientist and META to reconstruct what actually happened.

Preserve, when applicable:

- the hypothesis or exploratory question;
- the intervention or configuration;
- comparator/control;
- data/split/fidelity/seed when relevant;
- exact measured metrics;
- failures, retries, and unexpected events;
- evidence/log paths;
- the implementation context that produced the result;
- the interpretation and important limitations.

This information belongs in evidence and META's experiment ledger; it does **not** define the format of the Scientist's free-form session report.

Failed and negative experiments are first-class research history. Do not discard them merely because they did not improve the benchmark.

## Cheap faithful evidence

Cheaper evidence is useful when it preserves the mechanism needed to answer the question. Smoke tests, reduced datasets, proxy evaluations, and short training runs can accelerate research, but they are tools rather than universally required gates.

Do not optimize for cheapness itself. If a proxy changes the relevant grouping, temporal structure, statistical power, or evaluator semantics, use the fidelity needed for a trustworthy answer.

When using a reduced subset for a grouped or ranking evaluation, preserve the grouping unit relevant to the evaluator — for example complete user, query, or session groups — rather than blindly slicing raw rows when that would change the structure of the measurement.

If the official task makes Full evaluations scarce — for example through a convergence counter, submission limit, or large compute cost — the resulting strategy belongs in `OPTIMIZE.md`. That task-specific strategy may strongly favor small faithful screening experiments without turning “gate before Full” into a universal rule.

## Interpretation

Separate observations from explanations.

A measured improvement can be real even when the proposed mechanism is wrong. A failed experiment can be informative even when it produces no new State. When several explanations remain possible, keep that uncertainty rather than forcing a single narrative.

Do not overclaim from one seed, one slice, or one proxy merely to make the research story cleaner.

## External knowledge

Search externally when it can materially improve the research decision. Prefer primary sources and use literature to generate or evaluate concrete ideas, not to satisfy a citation quota or populate `KNOWLEDGE.md` for its own sake.

## State

Only `system/**` is the reusable State object, and Scientist owns changes to it. `STATE.yaml` is META-authored descriptive/provenance metadata and is read-only to Scientist.

Before changing `system/**`, Scientist should understand the valid currently materialized baseline from `STATE.yaml`, actual implementation, and evidence. A correctly materialized historical State is legitimate even when it differs from `HEAD`.

State creation happens after a Scientist session:

```text
Scientist changes system/**
→ Scientist preserves evidence
→ Scientist writes its free-form report
→ Scientist returns
→ META inspects report + evidence + actual system/**
→ META decides whether the retained implementation should become a State
→ META writes STATE.yaml
→ META commits unchanged system/** + STATE.yaml
→ META creates immutable state/<id> tag
```

Each new `STATE.yaml` includes a `scientist_report` project-relative path under `research_record/reports/` pointing to the **already existing** report from the Scientist session that produced the implementation. This is a provenance pointer, not part of the reusable State object and not a constraint on report content.

META must not change `system/**` while crystallizing a State. It may stage and commit the retained Scientist-authored implementation exactly as left by Scientist together with the descriptor it writes.

If there is no valid State history, Scientist may establish an actual reusable implementation under `system/**` and report its work, but Scientist must not create a placeholder `STATE.yaml`. META creates the initial descriptor and State only after the Scientist returns.

To reuse a historical State, do not reset the whole repository. Use:

```bash
research-agent state materialize --target <project> <state-id>
```

This changes only the State-controlled implementation/descriptor while mutable research memory and append-only reports remain at current research time. The command also returns the linked Scientist report path so the State's origin is immediately discoverable.

A new State is created by META only after the linked Scientist report exists and retained `system/**` plus matching `STATE.yaml` are committed together:

```bash
research-agent state create --target <project> <state-id>
```

Research-memory changes alone do not require a Git commit. A Scientist session that produces useful evidence but no retained implementation change may produce no new State.

## What META records after a Scientist returns

META reconstructs the session from the Scientist's persisted free-form report plus actual source changes, logs, metrics, evaluator behavior, and implementation evidence.

For every meaningful experiment, META appends a concise entry to `RESEARCH_RECORD.yaml`. META must not invent a hypothesis that the Scientist did not hold, turn an exploratory run into a causal claim, or upgrade an interpretation into a fact.

META may reconcile or curate `EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md` after the Scientist's own session updates. META rewrites `RESEARCH_BRIEF.md` as a descriptive compression of the current state of knowledge and curates `RESEARCH_INTUITION.md` and `DO_BETTER.md` when the report and evidence warrant it. These cumulative layers must not prescribe the next hypothesis, experiment, model family, or research direction.

If a coherent retained implementation deserves a recoverable checkpoint, META writes `STATE.yaml` from the actual implementation, report, and evidence, then crystallizes the State without editing Scientist-authored `system/**`.

A fresh Scientist inherits the explicit progress stack while remaining free to challenge it. Raw evidence remains the final audit layer beneath every summary, intuition, process lesson, and report.
