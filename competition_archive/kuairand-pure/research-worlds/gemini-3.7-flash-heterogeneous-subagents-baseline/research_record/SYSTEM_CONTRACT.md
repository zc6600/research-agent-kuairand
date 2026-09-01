# Research System Contract

This file is the canonical source for **authority, ownership, data access, coordination boundaries, and State/version semantics**. It does not define the current research plan or teach scientific method; that belongs in `RESEARCH_METHOD.md`.

## Authority

- `task.md` and organizer artifacts define task goals, evaluator semantics, official splits, and submission rules.
- `PERSONAL.md` records human-declared environment, permissions, resources, and budgets. META and Scientist must treat it as read-only and binding. Missing facts remain unknown.
- `RESEARCH_METHOD.md` defines scientific procedure.
- `EXPLORE.md` records Scientist-observed data/source semantics.
- `RESEARCH_INTUITION.md` and `DO_BETTER.md` are META-owned fallible memory, not scientific evidence or delegated objectives.

## Roles

### META

META owns Serial process supervision: cycle sequencing, process-level concerns, resource pressure, drift/repetition detection, source/evidence audit after Scientist returns, and the decision whether another Scientist iteration is worth the time and compute.

META does **not** choose the Scientist's bottleneck, hypothesis, experiment, or research boundary and does not implement Scientist experiments.

### Scientist

Scientist owns scientific judgment inside exactly one iteration: reconstructing the scientific situation, selecting or forming the bottleneck, choosing competing explanations, hypotheses, diagnostics, controls and experiments, executing research code, auditing results, preserving evidence, and deciding which system changes deserve a new State.

Scientist performs one bottleneck-bounded iteration and returns control. It may read META memory as a fallible prior, but must translate any useful idea into its own testable claim before acting scientifically.

### Parallel Reviewer

Reviewer acts only after completed Parallel research worlds exist. It compares evidence and allocates future compute by selecting research worlds. It may value uncertainty reduction, falsification, bottleneck clarification, reusable knowledge, or State improvement.

Reviewer must not prescribe the next scientific question, bottleneck, hypothesis, experiment, or research boundary. It does not merge branch research memory or promote States.

### Runtime

The Python runtime owns deterministic mechanics: role/process boundaries, worktree isolation, scheduling, cancellation, usage capture, State validation, worktree cleanup, and guarded promotion. Runtime code must not become a second scientific planner.

## Write ownership

| Artifact | Writer |
|---|---|
| `SYSTEM_CONTRACT.md`, `RESEARCH_METHOD.md` | release / human migration |
| `PERSONAL.md` | human / bootstrap only |
| `RESEARCH_INTUITION.md`, `DO_BETTER.md` | META |
| Serial `runtime/current-brief.json` | META |
| Parallel branch context / runtime coordination | coordinator |
| `system/**` | Scientist |
| `STATE.yaml`, `RESEARCH_RECORD.yaml`, `EXPLORE.md`, `ENGINEERING.md`, `KNOWLEDGE.md`, logs, archives | Scientist |

All Scientist-created or Scientist-modified research and experiment code belongs under `system/**`.

## Coordination

### Serial

Serial Scientist receives `RESEARCH_AGENT_BRIEF`, normally `research_record/runtime/current-brief.json`, schema v2. The brief contains process-level `concerns`, `constraints`, and `budget`. It may describe drift, repetition, stalled progress, resource pressure, or blockers, but it must not assign a scientific objective.

### Parallel

Parallel Scientist receives `RESEARCH_AGENT_PARALLEL_CONTEXT`. It contains only branch identity, ancestry, candidate State identity, constraints, budget, and output paths. It must not contain `question`, `instructions`, `expected_evidence`, a bottleneck, hypothesis, experiment, or another scientific objective.

Replicas from the same parent intentionally receive the same scientific research world. Parallel currently relies on independent Scientist reasoning/execution rather than a planner that forces different directions.

### Synthesis

When synthesis is explicitly enabled, the context may additionally contain `kind: synthesis`, one `primary_branch`, `informed_by`, and copied `synthesis_inputs`.

The primary branch is the only implementation and State parent. `informed_by` worlds provide reference-only evidence. Their claims are not automatically true, compatible, or merged. The fresh Scientist may reject synthesis entirely. Research provenance may be DAG-shaped through `informed_by`; reusable State lineage remains single-parent.

All coordination JSON is process state, not scientific evidence.

## Research memory and evidence

Scientific continuity lives in current Scientist-owned artifacts such as:

- `RESEARCH_RECORD.yaml`
- `EXPLORE.md`
- `ENGINEERING.md`
- `KNOWLEDGE.md`
- experiment logs/results and explicit evidence files
- observed State behavior

Failed, negative, diagnostic-only, and uncertainty-reducing work is valid scientific continuity even when it creates no State.

`RESEARCH_INTUITION.md` is META's optional high-level prior memory. `DO_BETTER.md` is META's optional process/tooling memory. Neither is scientific evidence. Recording, repeating, or exposing a claim does not validate it.

## State and Git

Git in the target project is the version store for reusable States. It is **not** the research diary, research chronology, or scientific-evidence ledger.

The reusable State object is exactly:

```text
system/**
```

`research_record/STATE.yaml` describes the currently materialized State and is committed alongside a State snapshot so materialization can restore the matching description. It is not itself part of the reusable State object.

Mutable research memory is separate from State versioning and remains at current research time. `HEAD`, commit order, and commit SHA must not be interpreted as research chronology. A State id identifies a reusable implementation version, not a research-time point.

A correctly materialized historical State may differ from `HEAD`. That is valid when `system/**` and `STATE.yaml` match the named immutable State. Reusing an earlier State must use the guarded materializer rather than whole-repository checkout/reset so mutable research memory does not rewind.

State commits contain only the retained `system/**` version plus its matching `STATE.yaml`. State tags are immutable. Research-memory changes alone never require a State commit.

## Parallel State rules

Parallel candidate States are provisional until explicit promotion. A branch may commit `system/**` plus matching `STATE.yaml`, but must not create `state/*` tags.

A child may start from a provisional parent candidate. If it creates another State, `derived_from` must identify the context-recorded base State. A diagnostic-only child may retain the inherited provisional State unchanged.

`parallel-promote` adopts one final reviewed research world. It validates accepted ancestry, promotes every accepted provisional State needed to keep immutable lineage complete, adopts Scientist-owned research memory, and refuses to overwrite target research memory that changed after Parallel started. Promotion is guarded as one logical transaction and rolls back State refs/files and research memory if adoption fails.

## Data access

Hidden-test rows, features, and labels are unavailable during development. META, Reviewer, and Scientist must not inspect, count, summarize, encode, score, or derive aggregates from hidden-test data.

When `competition_data/manifest.json` exists, use only the curated development files under `competition_data/`. Do not reopen a mixed source or recreate hidden/public splits.

Parallel inputs are copied into isolated worktrees. `--share-inputs` remains disabled until the runtime can provide a portable read-only boundary. Synthesis evidence is copied for the same reason.

Final hidden-test evaluation is permitted only at the task's final-submission stage and must not be used for development or checkpoint selection.

## Resource policy

Concrete resource limits belong to `PERSONAL.md` or explicit coordination budgets, not generic agent code. Agents must respect those declared limits.

Efficiency is a scientific-operational principle rather than a fixed universal timeout: prefer the cheapest evidence that faithfully answers the question, and spend more only when cheaper evidence is insufficient. META may communicate resource pressure, but it may not turn that pressure into a prescribed scientific objective.

## Process termination

Serial META owns the delegated `max_cycles` policy. A lack of benchmark gain alone does not imply convergence, and progress already made alone does not justify continuation.

Semantic convergence means that no currently plausible next Scientist iteration has enough expected information or improvement value to justify its additional cost. If useful research remains but the delegated cycle budget ends, the correct status is `budget_exhausted`, not `converged`.
