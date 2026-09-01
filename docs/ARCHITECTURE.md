# Research Agent Architecture

Research Agent separates the lifetime of the **research world** from the lifetime of an individual **Scientist** trajectory.

> **Scientist owns the science. META owns what survives. Runtime owns what must be deterministic.**

This document is the implementation-level reference for role ownership, persistence semantics, State, and execution flow.

## 1. Responsibility boundaries

| Layer | Owns | Must not own |
|---|---|---|
| **Scientist** | Scientific judgment, experiments, implementation changes, evidence, one free-form session report | Cumulative Record/Brief/Intuition/Do Better, `STATE.yaml`, State tags |
| **META** | Audit, cumulative research memory, trajectory-level handoff, State crystallization | Choosing the next hypothesis/model/feature/experiment, editing Scientist implementation, rewriting completed reports |
| **Runtime** | Process isolation, cancellation, State operations, runner configuration, deterministic invariants | Scientific methodology |

The separation is deliberate: META maintains the environment in which the next Scientist thinks; the Scientist decides what to think and do inside it.

## 2. Scientist

Scientist owns scientific judgment:

- what matters in the current task;
- which hypothesis or exploratory question is worth pursuing;
- which experiment, model, objective, feature, or implementation to try;
- how to interpret the evidence;
- when to continue exploiting a mechanism, pivot, or abandon a direction.

There is no mandatory bottleneck lifecycle and no fixed research trajectory. Research techniques are tools, not process KPIs.

A Scientist may run multiple useful experiments in one session. A failed experiment may naturally motivate a diagnostic, confound control, or more precise follow-up before the trajectory ends.

Scientist may update shared working memory when its work establishes durable facts or reusable knowledge:

- `EXPLORE.md`
- `OPTIMIZE.md`
- `ENGINEERING.md`
- `KNOWLEDGE.md`

Scientist owns experiment evidence, implementation changes under `system/**`, and one final free-form report.

Scientist does **not** write cumulative `RESEARCH_RECORD.yaml`, `RESEARCH_BRIEF.md`, `RESEARCH_INTUITION.md`, `DO_BETTER.md`, or `STATE.yaml`, and does not create State tags.

## 3. META

META owns trajectory-level supervision and maintenance of the persistent research world.

After a Scientist session, META reads the new report and inspects actual source changes, logs, metrics, evaluator behavior, and other evidence. It may then:

1. update `RESEARCH_RECORD.yaml` from meaningful experiments and evidence;
2. crystallize a retained `system/**` implementation into an immutable State by writing `STATE.yaml` without changing Scientist-authored code;
3. rewrite `RESEARCH_BRIEF.md` as a concise description of current knowledge;
4. reconcile useful updates in `EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md`;
5. update `RESEARCH_INTUITION.md` and `DO_BETTER.md` when warranted;
6. audit unsupported claims, leakage, evaluator misuse, confounds, and weak evidence;
7. decide whether another independent Scientist trajectory is worth the cost.

META may decide what information survives into the next research world. It must not prescribe the next hypothesis, experiment, feature, objective, model family, or research direction. It must not edit `system/**` or rewrite a completed Scientist report.

> **META is a selective persistence operator, not a research planner.**

## 4. Runtime

Deterministic Python code owns boundaries that should not depend on model judgment:

- process isolation and cancellation;
- State operations and materialization;
- runner configuration;
- CLI/model/effort resolution;
- other mechanical invariants.

The runtime deliberately does not encode a mandatory scientific state machine. Research heuristics remain priors rather than process KPIs.

## 5. Research memory

The system separates information by the role it should play in future research, rather than placing everything in one conversation history.

| Epistemic role | Artifacts | Meaning |
|---|---|---|
| **Evidence and provenance** | `RESEARCH_RECORD.yaml`, `research_record/reports/**`, logs/metrics | What happened and what evidence exists |
| **Verified/shared knowledge** | `EXPLORE.md`, `ENGINEERING.md`, `KNOWLEDGE.md` | Durable facts about data, evaluator, environment, and reusable external knowledge |
| **Task-specific optimization implications** | `OPTIMIZE.md` | How benchmark mechanics should influence efficient optimization without prescribing the next scientific direction |
| **Current research state** | `RESEARCH_BRIEF.md` | Lossy compression of what a fresh Scientist most needs to know now |
| **Fallible priors** | `RESEARCH_INTUITION.md`, `DO_BETTER.md` | Scientific intuition and process lessons that may help but are not facts or instructions |
| **Reusable implementation** | `STATE.yaml`, `system/**` | Recoverable implementation state and provenance |

A fresh Scientist normally starts from the maintained memory stack rather than rereading every historical report. It may inspect raw reports, logs, evaluator code, source, or State provenance when summaries are insufficient or worth challenging.

## 6. Free-form Scientist reports

A Scientist writes one free-form report at the end of a session. There is no report schema, required section list, or checklist.

```text
Scientist session ends
        ↓
write one report
        ↓
report persists verbatim
        ↓
META reads it + checks evidence
```

The report is append-only provenance, not factual authority by itself and not hidden chain-of-thought. Serial sessions normally use `research_record/reports/cycle-<cycle-id>.md`; parallel sessions normally use `research_record/reports/branch-<branch-id>.md`. Existing reports are never overwritten; occupied preferred names receive a unique suffix.

The design is intentionally permissive: intuition, uncertainty, dead ends, explanations, and process observations can appear naturally without turning reflection fields into a second objective.

## 7. State and Git

A reusable State is intentionally narrow:

```text
State = system/**
```

`system/**` is created or changed by Scientist. `STATE.yaml` is written by META only after the Scientist has finished its report and META has audited the evidence. It records the retained implementation and provenance, including the producing Scientist report.

The order is:

```text
Scientist changes system/**
→ Scientist preserves evidence
→ Scientist writes final free-form report
→ Scientist returns
→ META audits report + evidence + actual system/**
→ META writes STATE.yaml when the implementation deserves a State
→ META commits unchanged system/** + STATE.yaml
→ META creates immutable state/<id> tag
```

A session can produce useful evidence without producing a new State. Git versions reusable implementation States, not research time. Historical State materialization restores the implementation and matching descriptor without rewinding current research memory.

The best current State is a recoverable reference and fallback. It is not conceptually required to remain the center of future search.

## 8. Serial trajectory handoff

`step`, `run`, and `resume` start one META process. Each delegated Scientist process is fresh.

```text
persistent research world
        ↓
     fresh Scientist
        ↓
reason / code / experiment
        ↓
evidence + implementation + report
        ↓
        META
        ↓
audit / compress / preserve / optional State
        ↓
updated research world
        ↓
     fresh Scientist
```

The new Scientist inherits the experience of previous research without inheriting the previous Scientist's hidden cognitive trajectory.

The coordination brief contains process concerns, constraints, budget, and identity only. It does not assign science.

## 9. Parallel trajectories

Parallel execution is the breadth counterpart to serial handoff.

> **Serial handoff preserves continuity across time. Parallel sampling preserves diversity across alternatives.**

A Parallel run starts from one externalized research world and creates independent successor worlds in isolated Git worktrees:

```text
                 world R0
              /     |     \
             /      |      \
      Scientist A Scientist B Scientist C
          ↓           ↓           ↓
        world A     world B     world C
             \       |       /
              \      |      /
               Reviewer
                  ↓
          selected worlds
```

Each replica receives the same inherited starting progress but runs as its own fresh Scientist trajectory. Branches do not share a live conversation or one mutable implementation. Each branch keeps its own report, evidence, implementation candidate, and memory snapshot.

The Reviewer compares completed research worlds post hoc. Selection does not mutate the target automatically: reviewed worktrees remain isolated until an explicit `parallel-promote` adopts one branch.

The CLI exposes the breadth and selection budget directly:

```text
--rounds       number of Scientist/reviewer rounds
--branches     independent replicas per selected parent world
--keep         maximum reviewed worlds carried forward
--parallelism  maximum concurrent Scientist worktrees
```

### 9.1 Optional evidence synthesis

Parallel independence creates the same tension discussed in the research design: branch diversity is useful, but research branches may discover complementary knowledge.

`--synthesis` provides a deliberately narrow, late form of cross-branch learning. It runs only after the final Parallel review, and only when the Reviewer judges that at least two completed worlds contain materially complementary evidence worth exposing to one fresh Scientist.

The synthesis boundary is strict:

- exactly one currently selected branch is the **primary implementation parent**;
- other completed branches are copied as **reference-only evidence inputs**;
- branch code is not merged;
- branch memories are not merged into one shared memory state;
- scores are not added or combined;
- evidence from another branch is not automatically treated as true;
- the synthesis Scientist retains authority over whether anything is scientifically worth testing.

```text
primary world A ───────────────┐
                               │ implementation parent
world B evidence ──┐           │
world C evidence ──┴─ reference-only inputs
                               ↓
                       fresh Scientist
                               ↓
                    optional synthesis world
```

This implements a simple ordering:

> **Independence first, selective evidence sharing later.**

The design intentionally avoids continuously synchronizing every branch into one common research history, because doing so would reduce the framing independence that Parallel is meant to create.

## 10. Heterogeneous model roles

META and Scientist can use different CLIs, models, and reasoning-effort settings. Competition runners support role-specific configuration such as `--meta-cli`, `--scientist-cli`, `--meta-model`, `--scientist-model`, `--meta-effort`, and `--scientist-effort`, while shared model/effort settings remain available as fallbacks.

This is an architectural affordance rather than a hard-coded model policy. Different roles may benefit from different model behavior, and observed model-specific search tendencies should not be encoded as universal research rules.

## 11. Research principles

The project keeps only a few default heuristics:

- optimize the real valid task/evaluator, not compliance with a research template;
- understand enough of the real data/evaluator to avoid optimizing a false proxy;
- prefer measured evidence over plausible prose;
- preserve negative and failed experiments;
- preserve useful scientific intuition without confusing it with fact or instruction;
- use cheaper evidence when it faithfully answers the question;
- separate observed effects from causal stories;
- keep exact evidence beneath prose summaries;
- keep universal research heuristics in `RESEARCH_METHOD.md` and task-specific benchmark implications in `OPTIMIZE.md`;
- add new control mechanisms only after observed failures justify them.

The research method is a prior, not a policy.
