# Variant 03 — Runtime Storyboard

This variant retells the SciOdyssey deck as a live runtime trace: `task.md` is read, the Scientist acts, the evaluator verifies, and META retains the evidence before the next trajectory begins.

## Design rationale

- Preserves the main deck contract: Slidev default theme, 16:9 canvas, Avenir Next / Fira Code, white background, chapter kickers, and the existing blue/orange/rose/purple/aqua palette.
- Uses a single visible `READ → ACT → VERIFY → RETAIN` status spine instead of an orbit or dense component grid.
- Makes the entry page a boot screen for `task.md`, `PERSONAL.md`, and the documented `step` command.
- Makes the handoff/system page the visual hinge: Scientist owns scientific judgment, META audits and preserves, and Runtime enforces deterministic mechanics.
- Keeps the benchmark, convergence, result, and reproducibility claims grounded in the repository README, project story, final report, KuaiRand task contract, and `PERSONAL.md`.

## Run

```bash
npm install
npm run dev
npm run build
```

The variant is self-contained and does not modify the main deck or other variants.
