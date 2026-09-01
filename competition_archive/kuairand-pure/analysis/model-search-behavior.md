# Model Search Behavior in Mature Research Runs

**Date:** 2026-08-31  
**Status:** Preliminary observational report  
**Scope:** Research Agent Scientist behavior in a mature KuaiRand research trajectory

## Summary

A recurring late-stage behavior has been observed when using **Luna** as the Scientist: once a strong implementation and a substantial research history exist, the model tends to remain close to the current best State and propose incremental modifications rather than qualitatively different research directions.

Under the same Research Agent architecture, **Gemini 3.7 Flash** has not shown the same tendency as strongly. It appears more willing to reconsider the framing, introduce a different mechanism, or move farther away from the current implementation.

This is currently an **observed model-behavior difference**, not a proven general property of either model.

## Observed Pattern

The late-stage Luna trajectory often looks like:

```text
mature current best State
        ↓
identify a small unresolved weakness
        ↓
make a local feature / loss / parameter / implementation change
        ↓
measure
        ↓
make another nearby change
```

The concern is not that incremental optimization is inherently bad. Local exploitation is useful when a promising mechanism has clear remaining headroom. The problem is that repeated local improvements can become the default even when the return from the current basin is diminishing.

The contrasting Gemini 3.7 Flash behavior has been qualitatively broader:

```text
mature current best State
        ↓
reconsider what may still matter
        ↓
consider a different mechanism or framing
        ↓
run a more structurally distinct experiment
```

## Is the Prompt Explicitly Encouraging Small Tweaks?

No strong instruction currently tells the Scientist to make only small or conservative changes.

The Scientist is explicitly allowed to:

- decide what matters;
- choose its own hypothesis or exploratory direction;
- pivot when evidence warrants it;
- reconsider the framing;
- run as many useful experiments as the session budget allows.

However, the mature research environment naturally contains strong anchors:

- the current validation-best State;
- a concise Research Brief centered on what has already worked;
- accumulated negative results;
- optimization guidance to protect scarce Full evaluations;
- an instruction to retain the strongest valid implementation.

For a model with a strong preserve-and-improve prior, these ingredients can form a local-search basin even without any explicit local-search policy.

## Working Interpretation

The current hypothesis is that this behavior has a substantial **model-specific component**.

A plausible mechanism is:

```text
working implementation exists
        ↓
model assigns high value to preserving it
        ↓
large changes appear to carry regression risk
        ↓
small reversible changes appear high expected value
        ↓
local improvement reinforces confidence in the current basin
        ↓
continued local exploitation
```

This prior is often desirable in software engineering. A production coding agent should usually avoid unnecessary rewrites and prefer targeted, testable changes.

Research is different: the current implementation is an experimental object, not necessarily a production design that deserves preservation as the center of future search.

The distinction is:

> The best State should be a safe fallback and reference point, not necessarily the center of the search space.

## Architectural Implication

The current evidence does **not** justify changing the generic Scientist prompt aggressively.

Because Gemini 3.7 Flash can use the same research environment without showing the same degree of late-stage local fixation, a strong generic instruction such as “be more radical” or “try a new architecture every N cycles” could damage models that already explore appropriately.

The lightweight response is to exploit heterogeneous model behavior rather than force all models into one search style.

A useful configuration is therefore:

```text
META      → model strong at audit, compression, and environment maintenance
Scientist → model strong at independent scientific exploration
```

The existing support for separate META and Scientist CLI / model / effort settings is important for this reason.

## Memory and Anchoring

A second possible contributor is trajectory memory.

The Scientist currently inherits both:

### Factual memory

- task and evaluator semantics;
- data properties;
- leakage boundaries;
- reliable execution knowledge;
- verified external knowledge.

### Trajectory memory

- current best result;
- compressed interpretation of prior experiments;
- negative-result summaries;
- accumulated intuition;
- process lessons.

Factual memory prevents wasteful rediscovery and should normally be inherited.

Trajectory memory is useful, but it can also anchor a conservative model to the current research basin.

If late-stage stagnation appears across multiple Scientist models, a future experiment could compare normal cold start with a **trajectory-light / trajectory-blind cold start** in which the Scientist first forms an independent view from task facts, implementation, and factual memory before reading the compressed research trajectory.

This should be treated as an experiment, not as a new default architecture.

## What Not to Do Yet

The current observation does not justify:

- letting META directly perform the science;
- deleting research history entirely;
- forcing every Scientist to make a large architectural change;
- imposing exploration quotas;
- adding a fixed exploration/exploitation state machine;
- rewriting the generic research method around one model's behavior.

These responses would turn one observed model tendency into system-wide research policy.

## Suggested Next Evaluation

A clean behavioral comparison would hold the research world fixed and vary only the Scientist model:

```text
same State
same Research Brief
same factual memory
same task
same resource budget
```

For each fresh Scientist session, record the first substantive research decision and classify its distance from the current implementation, for example:

```text
L0 — parameter / threshold tweak
L1 — small feature, loss, or local component change
L2 — component-level redesign
L3 — model- or mechanism-level change
L4 — problem / evaluator / causal reframing
```

The purpose is not to create a permanent scoring rubric. It is a temporary diagnostic to test whether the observed search-style difference is stable across fresh sessions.

## Current Conclusion

The current Research Agent prompt does not explicitly demand late-stage incrementalism. The stronger evidence points toward an interaction between a mature, highly informative research environment and Luna's apparent preference for low-risk exploitation of an existing working implementation.

Gemini 3.7 Flash provides an important counterexample: broader search remains possible under the current architecture.

Therefore the preferred response is currently **model selection and observation**, not architectural intervention.
