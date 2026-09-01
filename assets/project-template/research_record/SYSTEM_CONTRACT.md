# Research System Contract

This file is the canonical source for **authority, ownership, data access, coordination boundaries, and State/version semantics**. It does not prescribe a scientific workflow; it is not the research diary.

## Authority

- `task.md` and organizer artifacts define task goals, evaluator semantics, official splits, and submission rules.
- `PERSONAL.md` records human-declared environment, permissions, resources, and budgets. META and Scientist treat it as read-only and binding. Missing facts remain unknown.
- `RESEARCH_METHOD.md` contains lightweight research principles rather than a mandatory workflow.
- `EXPLORE.md` records durable observed data/source/evaluator semantics.
- `OPTIMIZE.md` records durable task-specific optimization implications derived from official task/evaluator mechanics.
- `ENGINEERING.md` records reusable execution and implementation facts.
- `KNOWLEDGE.md` records reusable verified external knowledge.
- `research_record/reports/` contains persisted free-form Scientist session reports.
- `RESEARCH_RECORD.yaml` is the complete experiment ledger maintained by META from actual evidence.
- `RESEARCH_BRIEF.md` is META's concise descriptive compression for supervision and human inspection; the runtime launcher does not inject it into a fresh Scientist.
- `RESEARCH_INTUITION.md` is META-maintained externalized scientific intuition: fallible priors and emerging patterns that future Scientists should inherit but not treat as fact.
- `DO_BETTER.md` is META-maintained externalized research-process learning that future Scientists should inherit but not treat as mandatory workflow.
- `STATE.yaml` is META-authored semantic/provenance metadata for the currently materialized implementation under `system/**`.

A fresh Scientist is cognitively fresh, not scientifically blank. Restarting a Scientist discards hidden reasoning trajectory, not explicit research progress.

## Roles

### META

META owns trajectory-level supervision and maintenance of the shared research environment.

META may:

- inspect task, data/evaluator semantics, source, logs, metrics, current `system/**`, State evidence, and persisted Scientist reports;
- initialize or curate `EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md` from the actual research world and Scientist reports;
- audit process drift, resource pressure, leakage, evaluator misuse, unsupported claims, and evidence completeness;
- append complete experiment entries to `RESEARCH_RECORD.yaml`;
- rewrite `RESEARCH_BRIEF.md` as a concise human-readable state of knowledge;
- curate `RESEARCH_INTUITION.md` from material changes in scientific priors or emerging patterns supported by Scientist reports and evidence;
- curate `DO_BETTER.md` from durable research-process lessons supported by Scientist reports and evidence;
- after a Scientist returns, crystallize a coherent retained implementation into a State by writing `STATE.yaml`, linking it to the completed Scientist report, committing the retained `system/**` unchanged together with the descriptor, and creating the immutable State tag;
- decide whether another independent Scientist trajectory is worth the time and compute.

META must **not** choose or prescribe the next scientific hypothesis, experiment, feature, objective, model family, or research direction. It must not turn descriptive compression, accumulated intuition, or process learning into a hidden research plan. In particular, "X remains untested" must not silently become "test X next", and "Y produced the best score" must not silently become "continue Y".

META must **not edit the contents of `system/**`**. It may inspect, stage, and commit the coherent implementation exactly as the Scientist left it when creating a State, but implementation changes themselves belong to Scientist. META also must not edit a completed Scientist report; reports are append-only provenance.

META may interpret evidence when maintaining memory or `STATE.yaml`, but must preserve uncertainty and distinguish observed facts from interpretation. It must not invent a hypothesis for an exploratory experiment or upgrade a causal story beyond the evidence.

### Scientist

Scientist owns scientific judgment during its session: understanding the problem, deciding what is worth pursuing, forming hypotheses or exploratory questions, choosing experiments and controls, writing research code, interpreting results, and changing direction when evidence warrants it.

Scientist is not constrained by a bottleneck lifecycle or fixed reasoning trajectory. Research heuristics are optional aids, not process KPIs.

Scientist receives the launcher-injected shared-memory stack, including the current `STATE.yaml`, `RESEARCH_INTUITION.md`, and `DO_BETTER.md`. META's `RESEARCH_BRIEF.md` is not part of normal runtime Scientist startup. These files are accumulated/descriptive progress, not authority: Scientist may challenge, reinterpret, weaken, or reject their scientific interpretations when actual evidence warrants it.

`EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md` are shared research-environment memory rather than exclusive-role files. META may initialize or curate them, and Scientist may update them directly during a session when it establishes durable world facts, task-specific optimization implications, reusable execution knowledge, or verified external knowledge. `OPTIMIZE.md` must capture reusable task mechanics rather than prescribe a future research plan.

Scientist may create or modify executable research and experiment code only under `system/**`. It may retain a coherent implementation for META to inspect after the session, but it must not edit, create, or rewrite `research_record/STATE.yaml` and must not create `state/*` tags.

At the end of each session, Scientist writes one new persisted free-form report under `research_record/reports/`. The report has no required schema, section list, fields, or style. Scientist decides what is worth leaving behind. Ideas, intuition, uncertainty, interpretations, dead ends, and process lessons may appear there when the Scientist considers them useful. An existing report must never be overwritten or rewritten.

Scientist does **not** directly edit the cumulative `RESEARCH_RECORD.yaml`, `RESEARCH_BRIEF.md`, `RESEARCH_INTUITION.md`, or `DO_BETTER.md`. META reads the report and audits actual evidence before updating those cumulative artifacts.

### Parallel Reviewer

Reviewer acts only after completed Parallel research worlds exist. It compares completed evidence and allocates future compute by selecting research worlds. It does not prescribe a future hypothesis, experiment, or scientific direction and does not itself edit branch implementation, merge branch research memory, or create State metadata.

### Runtime

The Python runtime owns deterministic mechanics: role/process boundaries, worktree isolation, scheduling, cancellation, usage capture, State validation, worktree cleanup, and guarded promotion. Runtime code must not interpret or structure Scientist report content and must not become a second scientific planner.

## Write ownership

| Artifact | Writer |
|---|---|
| `SYSTEM_CONTRACT.md`, `RESEARCH_METHOD.md` | release / human migration |
| `PERSONAL.md` | human / bootstrap only |
| `RESEARCH_RECORD.yaml` | META |
| `RESEARCH_BRIEF.md` | META |
| `RESEARCH_INTUITION.md`, `DO_BETTER.md` | META |
| `research_record/STATE.yaml` | META |
| `research_record/reports/*` | Scientist, create-only / append-only across sessions |
| `EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, `KNOWLEDGE.md` | META and Scientist |
| Serial `runtime/current-brief.json` | META |
| Parallel branch context / runtime coordination | coordinator |
| experiment logs and raw evidence | Scientist / runtime |
| `system/**` | Scientist only |

All Scientist-created or Scientist-modified executable research and experiment code belongs under `system/**`.

Write ownership does not imply exclusive readership. META audits all research artifacts needed to maintain the environment. Scientist reads the maintained environment, including `STATE.yaml`, and may inspect deeper provenance and evidence when needed. In particular, `RESEARCH_INTUITION.md` and `DO_BETTER.md` are maintained by META so future fresh Scientists can inherit scientific and process progress without inheriting hidden chain of thought. Scientist reports remain available as the original free-form session handoff beneath those cumulative memories.

## Coordination

### Serial

Serial Scientist receives `RESEARCH_AGENT_BRIEF`, normally `research_record/runtime/current-brief.json`. This coordination JSON contains process-level concerns, constraints, budget, and cycle identity only. It must not assign a scientific objective, hypothesis, experiment, or research direction.

A Serial Scientist normally writes a new report path derived from the current cycle identity, such as `research_record/reports/cycle-$RESEARCH_AGENT_CYCLE.md`. If that path already exists, a new unique path must be chosen rather than overwriting it.

The persistent research environment includes `RESEARCH_BRIEF.md`, the current `STATE.yaml` and implementation, underlying evidence and records, scientific intuition, process lessons, and Scientist reports. The runtime Scientist handoff is the launcher-injected shared-memory stack, which intentionally excludes META's Brief; all of these artifacts are descriptive or fallible memory rather than coordination control.

### Parallel

Parallel Scientist receives `RESEARCH_AGENT_PARALLEL_CONTEXT`. It contains only branch identity, ancestry, constraints, budget, and output paths. It must not contain a question, hypothesis, experiment, or assigned research direction.

A Parallel Scientist normally writes a new report path derived from the branch identity, such as `research_record/reports/branch-$RESEARCH_AGENT_BRANCH_ID.md`. If that path already exists, a new unique path must be chosen rather than overwriting it.

Replicas from the same parent intentionally receive the same externalized research world and independently sample their own scientific reasoning. Parallel context may identify branch ancestry or implementation candidates for coordination, but that metadata does not give Scientist permission to write `STATE.yaml`.

### Synthesis

When synthesis is explicitly enabled, one primary branch remains the only implementation parent. Copied evidence from other worlds is reference-only input. A fresh Scientist may use, reinterpret, or reject it. There is no mechanical merge of code, scores, or research memory.

All coordination JSON is process state, not scientific evidence.

## Research memory and evidence

The research world contains both free-form and curated memory:

```text
raw logs / metrics / source / evaluator behavior
  auditable evidence

Scientist reports
  free-form, append-only session handoff written by Scientist

RESEARCH_RECORD.yaml
  complete chronological experiment ledger maintained by META

EXPLORE.md / KNOWLEDGE.md
  established observed or verified knowledge, shared-write

OPTIMIZE.md / ENGINEERING.md
  reusable task and execution knowledge, shared-write

RESEARCH_INTUITION.md
  META-maintained fallible scientific priors and emerging patterns

DO_BETTER.md
  META-maintained fallible research-process learning

RESEARCH_BRIEF.md
  META-maintained concise, human-readable, lossy compression for supervision and human inspection; not injected into runtime Scientist startup

STATE.yaml
  META-authored description/provenance for the currently materialized implementation
```

Scientist reports are intentionally unstructured. Do not impose a report schema or infer that every report must cover the same topics. A report is not factual authority by itself; META and later Scientists may check its claims against actual evidence. Completed reports are provenance and are never rewritten by META or later Scientists.

A fresh Scientist should not read every historical report by default. The
launcher injects the maintained shared-memory stack, excluding the META-owned
`RESEARCH_BRIEF.md` trajectory compression, as the normal cold-start handoff.
Historical reports and the Brief are deeper provenance to inspect only when a
summary is insufficient, ambiguous, worth challenging, or linked from the
current State.

These layers differ in epistemic status, not in whether they count as research progress. The next fresh Scientist may inspect any of them while remaining free to challenge fallible summaries, intuitions, process lessons, and prior interpretations.

The Brief is not an authority. A Scientist may inspect the Record, a State-linked report, other prior reports, or raw evidence whenever any higher-level memory is insufficient, ambiguous, or worth challenging.

Each meaningful experiment in `RESEARCH_RECORD.yaml` must preserve enough information to reconstruct why it was run, what changed, what happened, what evidence supports the entry, and what the result does and does not establish. Failed, negative, diagnostic, exploratory, and uncertainty-reducing experiments remain part of the history.

## State and Git

Git in the target project is the version store for reusable States. It is **not** the research diary, research chronology, or scientific-evidence ledger.

The reusable State object is exactly:

```text
system/**
```

`research_record/STATE.yaml` is written by META to describe the currently materialized State. It is committed alongside a State snapshot so materialization can restore the matching description, but it is not itself part of the reusable State object.

State creation happens after a Scientist session, not inside the Scientist's scientific loop:

```text
Scientist modifies system/**
→ Scientist finishes evidence and free-form report
→ Scientist returns
→ META audits report + evidence + actual system/**
→ if the retained implementation deserves a recoverable State:
     META writes STATE.yaml
     META commits unchanged system/** + STATE.yaml
     META creates immutable state/<id> tag
```

Every newly created State must include a `scientist_report` field in `STATE.yaml` pointing to the project-relative path of the completed free-form Scientist report for the session that produced that implementation. Multiple States crystallized from one Scientist session may point to the same report when appropriate. This provenance pointer does not constrain the report's contents.

The State-linked report is the primary human-readable provenance for how that implementation came to exist. When a historical State is materialized or inspected, its `STATE.yaml` must make the corresponding Scientist report discoverable. If the referenced report is missing, State provenance is incomplete and should be treated as an audit failure rather than guessed from Git history.

Mutable research memory is separate from State versioning and remains at current research time. `HEAD`, commit order, and commit SHA must not be interpreted as research chronology. A State id identifies a reusable implementation version, not a research-time point.

A correctly materialized historical State may differ from `HEAD`. Reusing an earlier State must use the guarded materializer rather than whole-repository checkout/reset so mutable research memory does not rewind.

State commits contain the retained Scientist-authored `system/**` version plus META's matching `STATE.yaml`. State tags are immutable. The linked Scientist report remains in append-only research memory and is not part of the reusable State object. Research-memory changes alone never require a State commit.

## Parallel State rules

Parallel Scientists follow the same ownership boundary: they may modify `system/**` and write evidence/reports, but they do not write `STATE.yaml` or create State tags. Any Parallel workflow that wants to preserve a selected implementation as a State must perform post-Scientist supervision that writes the descriptor from the selected report and evidence without modifying the Scientist-authored implementation.

A child may start from an inherited materialized State or selected implementation world. State ancestry is descriptive provenance maintained by supervision, not a scientific instruction to the child.

`parallel-promote` must not overwrite target research memory that changed after Parallel started.

## Data access

Hidden-test rows, features, and labels are unavailable during development. META, Reviewer, and Scientist must not inspect, count, summarize, encode, score, or derive aggregates from hidden-test data.

When `competition_data/manifest.json` exists, use only the curated development files under `competition_data/`. Do not reopen a mixed source or recreate hidden/public splits.

Parallel inputs are copied into isolated worktrees. Synthesis evidence is copied for the same reason.

Final hidden-test evaluation is permitted only at the task's final-submission stage and must not be used for development or checkpoint selection.

## Resource policy

Concrete resource limits belong to `PERSONAL.md` or explicit coordination budgets, not generic agent code. Agents must respect those declared limits.

Efficiency is an operational principle rather than a scientific objective. A cheaper experiment is preferable when it faithfully answers the question; otherwise use the fidelity required for trustworthy evidence.

## Process termination

Serial META owns the delegated `max_cycles` policy. A lack of benchmark gain alone does not imply semantic convergence, and progress already made alone does not justify continuation.

Semantic convergence means that no currently plausible fresh Scientist trajectory has enough expected information or improvement value to justify its additional cost. If useful research remains but the delegated cycle budget ends, the correct status is `budget_exhausted`, not `converged`.
