# Competition Archive

This directory contains only the historical evidence cited by the formal competition report; it is not a dumping ground for every experiment.

The current archive is [`kuairand-pure/`](kuairand-pure/INDEX.md), with the following structure:

```text
kuairand-pure/
├── INDEX.md          # Archive index, original-name mapping, and evidence purpose
├── evidence/         # Small, tracked snapshots for headline score/token claims
├── reports/          # Baseline and audit reports used by the Final Report
├── analysis/         # Failure and anchoring analyses used by the Final Report
└── research-worlds/  # Submit-ready snapshots of the corresponding models, code, and run records
```

The canonical, publicly submittable Research Agent package remains at
[`submission/research-agent-kuairand/`](../submission/research-agent-kuairand/). Archived research worlds
are submitted as ordinary directory snapshots that preserve source code, research records, and experimental
evidence; local Git metadata, virtual environments, and `competition_data/` are not part of the parent-repository
submission.

See [`kuairand-pure/INDEX.md`](kuairand-pure/INDEX.md) for the mapping between each world and its historical
project name.
