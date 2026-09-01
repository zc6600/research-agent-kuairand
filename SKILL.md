---
name: research-agent
description: Run or supervise an evidence-driven research project with separate META and Scientist roles.
---

# Research Agent

Research Agent separates **trajectory supervision and shared memory** from **scientific judgment**.

- **META** maintains the shared research environment, audits evidence, externalizes research progress, crystallizes retained implementations into States, and decides whether another independent Scientist trajectory is worth the time and compute.
- **Scientist** owns scientific judgment: what matters, what to hypothesize, what to test, how to implement it, and when to pivot inside its session.
- **Parallel Reviewer** compares completed research worlds after the science happened; it does not plan the science.
- **Python runtime** owns mechanical isolation, scheduling, cancellation, State validation/promotion, and other deterministic guards.

The target-pinned `research_record/SYSTEM_CONTRACT.md` is the canonical source for authority, ownership, data access, and State/version boundaries. `research_record/RESEARCH_METHOD.md` contains lightweight research principles. The launcher injects the target files required for each role's startup and the active coordination input into each runner prompt; `SKILL.md` remains external-agent documentation and is not injected or read by runtime agents. Actual implementation, evaluator, and deeper evidence remain available for inspection when needed.

## Core model

A research world contains the current implementation plus externalized progress that lets a fresh Scientist continue without inheriting the previous Scientist's hidden chain of thought:

```text
research world
├── task.md
├── PERSONAL.md
├── research_record/RESEARCH_BRIEF.md      # META-maintained concise handoff
├── research_record/RESEARCH_RECORD.yaml   # META-maintained complete experiment ledger
├── research_record/EXPLORE.md             # shared durable world facts
├── research_record/OPTIMIZE.md            # shared task-specific implications
├── research_record/ENGINEERING.md         # shared reusable execution facts
├── research_record/KNOWLEDGE.md           # shared verified external knowledge
├── research_record/RESEARCH_INTUITION.md  # META-maintained fallible scientific intuition
├── research_record/DO_BETTER.md           # META-maintained research-process learning
├── research_record/reports/               # append-only free-form Scientist reports
├── other evidence/logs
└── current State
    ├── research_record/STATE.yaml          # META-authored descriptor + Scientist-report provenance
    └── system/**                           # Scientist-created implementation
```

A fresh Scientist is **cognitively fresh, not scientifically blank**. Hidden trajectory-specific cognition is discarded when a session ends; explicit scientific progress is preserved in the research environment and read back by the next Scientist.

`RESEARCH_BRIEF.md` is a lossy, human-readable compression for META and human inspection; the launcher intentionally excludes it from the normal runtime Scientist injection. `RESEARCH_RECORD.yaml` is the complete experiment history. Raw logs, metrics, source, evaluator behavior, and free-form Scientist reports remain available underneath META's cumulative memory.

`EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md` are shared research-environment memory. META may initialize and curate them; Scientist may also update them directly during a session when its work establishes durable information.

`RESEARCH_INTUITION.md` preserves higher-level, fallible scientific priors or emerging patterns that have become part of the project's progress but are not yet established fact. `DO_BETTER.md` preserves fallible lessons about how to research this project more effectively. META maintains both. A Scientist may put ideas, intuition, uncertainty, or process learning in its free-form report when it considers them worth preserving; META decides what should become cumulative memory after checking the report against actual evidence.

Only `system/**` is the reusable State object. Scientist creates or changes that implementation. After the Scientist returns and its report exists, META may crystallize the retained implementation into a State by writing `research_record/STATE.yaml`, linking it to that report, committing the unchanged retained `system/**` together with the descriptor, and creating the immutable State tag. Git is the target project's State version store, not the research diary or chronology.

Serial and Parallel are traversal policies over research worlds:

```text
Serial:    R0 → fresh Scientist → report + evidence → META memory/State update → R1 → ...

Parallel:  R0 ─┬→ fresh Scientist A → RA
               ├→ fresh Scientist B → RB
               └→ fresh Scientist C → RC
                              ↓
                           Reviewer
```

Fresh Scientists are an exploration mechanism: they retain externalized scientific progress while dropping trajectory-specific cognitive inertia.

## Entry points

- `step`: one META session, at most one fresh Scientist session.
- `run` / `resume`: one persistent META session, up to the delegated cycle budget.
- `launch-inner`: one fresh Serial Scientist using the current coordination brief.
- `parallel`: independent Scientist replicas followed by post-hoc review.
- `parallel --synthesis`: optional evidence exposure after the final Parallel round.
- `parallel-promote`: explicitly adopt one final reviewed research world.

An active META must not recursively invoke `step`, `run`, or `resume`; it launches Scientist with `launch-inner`. A Scientist must not launch another Scientist.

## META loop

For every possible next cycle:

1. Reconstruct the current research world from `task.md`, `PERSONAL.md`, the maintained memory stack, relevant evidence/logs, actual `system/**`, current `STATE.yaml`, and pinned starter/evaluator source when it determines task semantics. Historical Scientist reports are deeper provenance rather than default cold-start material; inspect the current State-linked report or other reports when needed to understand or audit a claim.
2. Audit factual reliability: data boundaries, evaluator use, implementation changes, experiment evidence, State claims, and unsupported causal claims. Mechanical facts should be checked against source/logs rather than accepted from prose.
3. Do **not** choose the next scientific hypothesis, experiment, model family, feature, objective, or research direction for the Scientist.
4. Initialize or curate `EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md` when the shared environment needs it, especially before the first Scientist or after a Scientist report materially changes reusable knowledge. These files remain editable by Scientist during its own session.
5. Write `research_record/runtime/current-brief.json` with process-level concerns, constraints, budget, and cycle identity only.
6. Launch exactly one fresh Scientist.
7. After it returns, read the new append-only Scientist report and inspect the actual `system/**` changes, logs, metrics, evaluator behavior, and other evidence. Update `RESEARCH_RECORD.yaml` with every meaningful experiment, including failed and negative experiments. Do not invent a hypothesis or causal interpretation that the Scientist did not hold or that the evidence does not support.
8. If the Scientist left a coherent retained implementation that should become a recoverable State, verify that its report exists, write the matching `research_record/STATE.yaml` with `id`, `git_tag`, `derived_from`, `scientist_report`, and concise evidence-grounded description, then commit the retained `system/**` **without editing it** together with `STATE.yaml` and create the immutable State tag. A session that produces only evidence may create no new State.
9. Rewrite `RESEARCH_BRIEF.md` as a concise descriptive compression of the current state of knowledge for the next fresh Scientist. Include the current best verified result, major supported findings, important negative results, and material unresolved uncertainty. Cite experiment ids where useful. **Describe what is known; do not prescribe what the next Scientist should do.**
10. Curate shared environment memory as warranted: reconcile useful Scientist-authored updates in `EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md`; update `RESEARCH_INTUITION.md` and `DO_BETTER.md` when the report and underlying evidence show that scientific intuition or process learning materially changed.
11. Decide whether another independent Scientist trajectory is worth buying.

META must never edit the contents of `system/**` or a completed Scientist report. `STATE.yaml` is META-owned descriptive/provenance metadata. META may stage and commit retained Scientist-authored `system/**` exactly as left by the Scientist when crystallizing a State, but must not modify the implementation itself.

### Continuation mental model

Progress already made is not by itself a reason to continue. Ask whether another fresh Scientist could plausibly produce important information or improvement that justifies the added time and compute. If not, return `converged`; if useful research remains but the delegated cycle budget is exhausted, return `budget_exhausted`.

This decision is trajectory-level allocation, not scientific planning.

## Memory discipline

The main memory layers have different jobs:

```text
Scientist reports
  What did each Scientist choose to leave behind from its session, in its own words?

EXPLORE.md
  What is the data/evaluator world?

OPTIMIZE.md
  How should this task's mechanics influence efficient optimization?

ENGINEERING.md
  How do we reliably operate in it?

KNOWLEDGE.md
  What verified external knowledge is reusable here?

RESEARCH_RECORD.yaml
  What experiments happened and what did we learn?

RESEARCH_BRIEF.md
  What does a fresh Scientist need to know now?

RESEARCH_INTUITION.md
  What fallible scientific priors or emerging patterns have accumulated?

DO_BETTER.md
  What research-process lessons should a fresh Scientist not have to rediscover?

STATE.yaml
  How does META describe and trace the currently materialized implementation State?
```

Scientist reports are deliberately free-form and append-only. Do not impose a schema, required headings, or a checklist on them. Do not make every historical report part of normal cold start. The launcher-injected shared-memory stack, excluding META's Brief compression, is the runtime default handoff; reports provide provenance when deeper reconstruction is useful.

META exclusively maintains Record, Brief, Intuition, Do Better, and `STATE.yaml`. `EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md` are shared-write environment memory: META can initialize/curate them and Scientist can update them while doing research. Scientist owns experiment evidence/logs, implementation changes under `system/**`, and its own new session report. The launcher injects the shared-memory stack required by the runtime contract; it does not inject either Skill file.

The point of restarting Scientist is to reset hidden cognition, not to reset science.

## Design discipline

Keep the architecture lightweight:

- Scientist optimizes the real task using its own scientific judgment;
- each Scientist writes one free-form persisted report rather than filling a reflection schema;
- every State points back to the Scientist report that explains how its implementation arose;
- Scientist changes implementation; META describes/crystallizes it as a State after the session;
- no required bottleneck state machine or fixed reasoning trajectory;
- universal research heuristics stay in `RESEARCH_METHOD.md`; task-specific benchmark strategy stays in `OPTIMIZE.md`;
- META maintains the research environment and compresses/audits progress but does not direct the next experiment or edit `system/**`;
- deterministic runtime code enforces mechanical guarantees;
- raw evidence remains available beneath all prose summaries;
- add a new mechanism only after an observed failure shows that it is needed.
