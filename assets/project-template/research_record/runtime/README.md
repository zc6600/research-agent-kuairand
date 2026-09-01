# Runtime state

This ignored directory contains replaceable operational coordination state. It is not a second research ledger and is not scientific evidence.

## Serial

`current-brief.json` is Serial META's current process-supervision brief for the next Scientist. Each external `step`, `run`, or `resume` gets isolated scratch under:

```text
tmp/<run-id>/
├── run.json
└── meta/
    ├── result.json
    ├── usage.json
    └── meta.log
```

`run.json` records the external run lifecycle. `meta/result.json` is META's final process handoff. `meta/meta.log` is the raw runner log. `meta/usage.json` is finalized run-level usage when comparable telemetry exists; otherwise usage remains explicitly unavailable.

The same META process may rewrite `current-brief.json` and launch multiple fresh Scientists during `run` or `resume`. META owns Serial sequencing and the delegated cycle policy. The brief carries process-level concerns, constraints, budget, and identity; it does not assign scientific work.

Each Serial Scientist writes one free-form append-only report under `research_record/reports/`, normally using its cycle identity. Reports are research provenance rather than runtime state and have no runtime schema.

A Scientist may leave retained implementation changes under `system/**`, but does not write `STATE.yaml`. After the report exists and the Scientist returns, META may crystallize the retained implementation into a State by writing `STATE.yaml`, committing the unchanged Scientist-authored implementation together with the descriptor, and creating the immutable tag.

Scientific evidence belongs in current semantic research records, Scientist reports, experiment logs/results, explicit evidence artifacts, source/evaluator observations, and measured State behavior. Git commit history is not research chronology.

## Parallel

`research-agent parallel` uses isolated worktrees and stores coordinator artifacts below the same ignored run directory:

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
```

There is no Parallel scientific planner. Each Scientist receives branch identity, ancestry, constraints, budget, and output paths, then independently chooses its science. Each branch writes a free-form append-only Scientist report; the coordinator snapshots reports, results, logs, and mutable research artifacts without parsing report contents.

Parallel Scientists follow the same ownership rule as Serial Scientists: they may change `system/**` but do not write `STATE.yaml` or create State tags. A selected Parallel implementation can become a canonical State only after post-Scientist META-style supervision writes the descriptor from the selected report and evidence without changing the implementation.

The current legacy Parallel promotion path predates this State-ownership simplification. It must not be interpreted as granting Scientist ownership of `STATE.yaml`. Until that promotion path is refactored around post-Scientist State crystallization, use Parallel primarily for isolated research/evidence comparison rather than assuming a code-changing branch can be canonically promoted unchanged.

`--share-inputs` remains disabled because supported runners do not share one portable read-only mount mechanism. Inputs are copied into isolated worktrees instead.

Runtime coordination JSON, branch manifests, Reviewer results, and usage files are operational state only. They never override `SYSTEM_CONTRACT.md` ownership or become scientific evidence merely because they are persisted.
