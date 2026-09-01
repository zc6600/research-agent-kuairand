# Trajectory Analyses

Trajectory analyses study **how research agents actually behave over time**.

They are empirical post-hoc analyses, not instructions that Scientist must follow during research. Their purpose is to make failure modes, search dynamics, recovery patterns, and model-specific behavior inspectable without turning those observations into mandatory methodology.

## Why analyze trajectories?

A final metric cannot show whether an agent:

- discovered a genuinely new research direction or repeatedly refined one basin;
- correctly abandoned a low-potential direction or remained anchored to it;
- interpreted a failed experiment at the right epistemic scope;
- produced a plausible but scientifically invalid measurement;
- recovered because of its own reasoning, META audit, or externalized research state;
- learned reusable research knowledge rather than only finding a better candidate.

Trajectory analysis treats the research process itself as evidence.

## Current analyses

| Analysis | Question |
|---|---|
| [`late-stage-anchoring.md`](../../competition_archive/kuairand-pure/analysis/late-stage-anchoring.md) | How can a technically sophisticated agent become progressively less exploratory? |
| [`scientific-validity-failure.md`](../../competition_archive/kuairand-pure/analysis/scientific-validity-failure.md) | How can an experiment run successfully while failing to support the claimed scientific conclusion? |
| [`model-search-behavior.md`](../../competition_archive/kuairand-pure/analysis/model-search-behavior.md) | How can a mature research context shape model-specific search behavior? |

## Trajectory records

| Record | Scope |
|---|---|
| [`gemini-3.7-flash-medium-baseline-2026-08-31.md`](gemini-3.7-flash-medium-baseline-2026-08-31.md) | `gemini-3.7-flash` medium-baseline negative control and its evidence boundary |
| [`agy-medium-baseline-2h-2026-09-01.md`](agy-medium-baseline-2h-2026-09-01.md) | Corrected `gemini-3.7-flash` medium goal baseline with a 2h maximum |
| [`parallel-synthesis.md`](parallel-synthesis.md) | Narrative of a parallel Scientist search and synthesis |

Competition-specific observations are indexed in the
[`KuaiRand-Pure archive`](../../competition_archive/kuairand-pure/INDEX.md);
generic dated observations remain in [`../reports/`](../reports/).

## Analysis lens

A useful post-hoc analysis may inspect:

```text
research state entering a trajectory
        ↓
what the agent considered worth trying
        ↓
experiments and evidence produced
        ↓
how beliefs / priorities changed
        ↓
what was retained or discarded
        ↓
what the next trajectory inherited
```

When useful, analyses distinguish:

- **exploration** — reopening where improvement might come from;
- **exploitation** — deepening an already-promising hypothesis family;
- **scientific value** — how promising a direction appears from evidence;
- **contextual influence** — how strongly prior trajectory material continues to shape later reasoning;
- **evidence scope** — exactly what a result supports, rather than a broader story inferred from it;
- **handoff quality** — whether useful experience survives without unnecessarily preserving trajectory momentum.

These are analysis concepts, not runtime states or required prompt fields.

## Evidence discipline

Trajectory analyses should separate:

1. **Observed behavior** — what the agent actually did or wrote;
2. **Supported interpretation** — what the available evidence reasonably suggests;
3. **Hypothesis** — a possible mechanism that has not been causally established;
4. **Design implication** — what system change, if any, the observation motivates.

In particular, we avoid claiming a specific Transformer attention mechanism unless supported by a dedicated experiment. It is enough to observe that accumulated context can act both as scientific memory and as trajectory conditioning.

## Future analyses

Useful additional studies include:

- where the largest metric jumps came from: exploratory vs exploitative moves;
- first substantive action of fresh Scientists under the same inherited research world;
- whether negative evidence is later recalled at the correct scope;
- whether a fresh Scientist reopens directions a persistent agent ignored;
- how different Scientist models allocate effort across research basins;
- how often META changes the epistemic status of a Scientist conclusion;
- recovery trajectories after process failure or interrupted sessions;
- repeated-failure analysis: what knowledge failed to survive a handoff;
- branch convergence: when nominally independent branches become conceptually similar.

The goal is not to build a larger process framework. The goal is to let observed trajectories reveal which mechanisms the system actually needs.
