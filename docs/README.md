# Research Agent Documentation

This directory contains the deeper documentation behind the high-level [`Research Agent README`](../README.md).

## Reading paths

| If you want to understand... | Read |
|---|---|
| The concise Devpost-ready project story, stack, results, lessons, and team | [`project_story.md`](project_story.md) |
| The problem, core insight, autonomous research trajectory, results, and competition narrative | [`FINAL_REPORT.md`](FINAL_REPORT.md) |
| Scientist / META / Runtime ownership, memory semantics, State, Git, serial and parallel execution | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| The reproducible Research Agent submission, prediction file, evaluator, and evidence bundle | [`../submission/research-agent-kuairand/`](../submission/research-agent-kuairand/) |
| Competition baseline evidence, token comparison, and failure analyses | [`competition_archive/kuairand-pure/`](../competition_archive/kuairand-pure/INDEX.md) |
| Post-hoc trajectory analyses and dated research records | [`trajectories/README.md`](trajectories/README.md) and [`reports/README.md`](reports/README.md) |

## Suggested order

For a first read:

```text
../README.md
    ↓
FINAL_REPORT.md
    ↓
ARCHITECTURE.md
    ↓
../submission/research-agent-kuairand/
    ↓
../competition_archive/kuairand-pure/
```

The README explains the system at a high level. The final report explains *why*
the architecture exists and how it behaved on the competition task.
`ARCHITECTURE.md` records implementation-level contracts. The competition
archive contains only the historical model worlds and analyses cited by the
final report.

## Documentation boundaries

- **README** — product-level mental model, quick start, and navigation.
- **project_story.md** — concise Devpost-ready narrative and team summary.
- **FINAL_REPORT** — competition/research narrative and evidence.
- **ARCHITECTURE** — implementation truth: ownership, persistence, State, and execution semantics.
- **reports/** — dated system and execution audits; useful evidence, but not normative architecture.
- **trajectories/** — post-hoc behavior analyses and dated trajectory records.
- **competition_archive/kuairand-pure/** — report-scoped baseline controls,
  submitted research-world snapshots, audits, and behavioral analyses.

When these documents overlap, implementation contracts in `ARCHITECTURE.md`
should be kept synchronized with the code. Behavioral claims should remain
scoped to the archived evidence rather than silently becoming universal policy.
