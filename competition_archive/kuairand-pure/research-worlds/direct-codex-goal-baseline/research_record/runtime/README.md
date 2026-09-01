# Runtime state

This ignored directory contains replaceable operational coordination state.
`current-brief.json` is Serial META's current process-supervision brief for the
next Scientist. Each external `step`, `run`, or `resume` gets isolated scratch
under:

```text
tmp/<run-id>/
├── run.json
└── meta/
    ├── result.json
    ├── usage.json
    └── meta.log
```

`run.json` is the lifecycle record for that external run. `meta/result.json` is
the META process's final handoff. `meta/meta.log` is the raw runner log.
`meta/usage.json` is the finalized run-level usage observation: it is measured
only when comparable before/after runner telemetry exists; otherwise it remains
explicitly unavailable.

The before/after telemetry snapshots used to calculate a run delta are
transient launcher state and are not persisted. There is no `latest-*` copy of
run usage or the META log; consumers locate the latest run through `run.json`
and read that run's canonical files directly. While the latest run is still
active, a final `usage.json` may not exist yet. Consumers must not substitute a
previous run's usage.

The `meta/` directory belongs to one Serial META process. During `run` or
`resume`, that same META process may rewrite `current-brief.json` and launch
multiple fresh Scientist processes before writing one final `result.json`.

META owns serial cycle sequencing and the delegated cycle policy. Runtime
scratch does not contain a launch counter, inferred cycle count, or separate
enforcement ledger. The next target-global cycle id is derived only from META's
current brief.

Current serial briefs use schema v2 and carry process-level `concerns`,
`constraints`, and `budget`. They do not assign a scientific objective; the
Scientist chooses the research boundary. Other schema versions are rejected.

These files are not a second research ledger and are not committed as control
history. The current serial brief is passed directly to Scientist through
`RESEARCH_AGENT_BRIEF`; it is not hashed or copied into an immutable archive.

Scientific evidence belongs in current semantic research records, experiment
logs/results, explicit evidence artifacts, and observed State behavior. Git
State snapshots establish which implementation belongs to a State; Git commit
history is not the research chronology or evidence ledger. Preserve telemetry
scope; whole-run usage must not be relabeled as Scientist-only.

## Opt-in Parallel runs

`research-agent parallel` is a separate branching mode. It leaves the target
research world unchanged during exploration and stores coordinator files below
the same run directory:

```text
parallel/
├── manifest.json
├── base-memory/
├── review-r<round>.normalized.json
├── aggregate.json
├── aggregate.md
├── result.json
├── meta/reviewer-r<round>/
├── usage/<branch>/
└── branches/
    ├── r<round>-<branch>.json
    ├── r<round>-<branch>.log
    └── r<round>-<branch>-memory/
```

There is no Parallel planner artifact. For every selected parent research world,
the coordinator mechanically creates independent Scientist replicas. Inside
each isolated worktree the formal coordination input is
`research_record/runtime/parallel-branch/parallel-branch.json`, exposed through
`RESEARCH_AGENT_PARALLEL_CONTEXT`. It contains branch identity, ancestry,
candidate State identity, constraints, budget, and output paths only; it does
not prescribe a scientific question or experiment.

Each Scientist independently chooses its own bottleneck-bounded research
iteration. The coordinator snapshots branch results, logs, and mutable research
memory into the ignored Parallel runtime before review. A branch may commit a
candidate `system/** + research_record/STATE.yaml`, but it does not create an
immutable `state/*` tag.

After the replicas finish, a post-hoc Parallel Reviewer audits the completed
research worlds. Reviewer selection is incumbent-preserving: an existing
selected branch remains eligible alongside newly explored branches, so another
round does not implicitly discard a stronger parent. The Reviewer does not
merge research memory or prescribe future scientific work; `next_action` is
process-level only.

After a successful Parallel run, the disposable Reviewer control worktree and
unselected Scientist worktrees are removed; only final Reviewer-selected
worktrees are retained for optional adoption. A failed or interrupted run
retains Scientist worktrees for inspection.

`--rounds` controls Scientist/reviewer rounds. `--branches` sets the number of
independent Scientist replicas per selected parent, `--keep` limits reviewed
research worlds carried into another round, and `--parallelism` controls actual
Scientist concurrency. These are traversal controls over research worlds; State
remains the reusable system abstraction.

`--share-inputs` is currently disabled. A symlink would expose writable source
data across branches and supported runners do not share one portable read-only
mount mechanism. Omit the flag so inputs are copied into each isolated
worktree.

`base-memory/` snapshots the target's Scientist-owned research continuity at
Parallel start. `parallel-promote` refuses adoption if those target artifacts
changed in the meantime, so a reviewed branch cannot silently overwrite newer
serial research.

`research-agent parallel-promote --allow-edits` adopts one reviewed research
world. It copies the selected branch's `RESEARCH_RECORD.yaml`, `EXPLORE.md`,
`KNOWLEDGE.md`, `ENGINEERING.md`, logs, and archives into the target. If the
branch also has a candidate State, promotion validates the State boundary and
`derived_from`, fast-forwards the candidate commit, and creates the immutable
tag through the canonical State machinery. A diagnostic-only branch with no new
State is still adoptable; in that case research memory advances while target
`HEAD` stays unchanged.
