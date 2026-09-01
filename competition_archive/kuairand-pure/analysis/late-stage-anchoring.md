# Late-Stage Anchoring: Sophisticated Exploitation Without Reopening the Search Space

## Observation

In mature runs, some persistent Scientist trajectories remained technically active but increasingly concentrated on local refinements around the current best implementation.

The behavior did **not** look like naive repetition. Later experiments could still be sophisticated: retuning learning rates after changing negative sampling, adjusting schedules, adding specific interactions, controlling confounds inside the same mechanism family, or testing higher-order variants.

The common pattern was that experiment complexity increased faster than hypothesis diversity.

> **The experiments can become more sophisticated without becoming more exploratory.**

## Explore vs exploit

For this analysis:

- **Exploitation** means deepening an already-promising hypothesis family while preserving its core explanation of where gain comes from.
- **Exploration** means reopening the source of gain: a different objective, feature family, model structure, training formulation, or interpretation of the bottleneck.

Exploitation is not a failure. It is often exactly the right scientific behavior. The failure mode appears when the trajectory itself makes exploitation progressively easier to choose even after the scientific value of the direction has declined.

## Salience–value mismatch

A human researcher can decide that a direction has been sufficiently explored and mentally deprioritize it. The experiments remain useful knowledge, but they no longer need to dominate attention.

In a persistent LLM trajectory, the direction's hypotheses, code edits, diagnostics, explanations, and recent successes remain part of the conditioning context. We observed cases where the research direction appeared close to saturation while nearby modifications continued to dominate subsequent proposals.

This suggests a useful distinction:

```text
scientific value of direction A ↓

while

contextual influence of trajectory A remains high
```

> **A direction can lose scientific value without losing contextual influence.**

We treat the mechanism behind this as a hypothesis rather than a proven statement about Transformer attention. The empirical claim is only that accumulated context can function both as scientific memory and as trajectory conditioning.

## Why it matters on KuaiRand

Local exploitation was useful for validating mechanisms and extracting incremental gains. However, the larger improvements in our observed research process tended to come from moves that reopened *where* the system searched for reward rather than only optimizing within the same basin.

This creates a long-horizon risk: an agent may continue producing valid, non-trivial experiments while its effective exploration space becomes narrower.

## Architectural implication

The desired operation is not to forget previous work. It is to preserve what was learned while ending the trajectory-specific momentum that produced it.

```text
useful trajectory
    ↓
evidence / failures / intuition externalized
    ↓
trajectory ends
    ↓
fresh Scientist inherits research experience
    ↓
new reasoning trajectory
```

> **The new Scientist should inherit the experience, not the momentum.**

This observation motivates trajectory-level handoff and fresh Scientist sessions. It does **not** justify resetting after every experiment: within a productive trajectory, continuity remains valuable for diagnostics, confound controls, and precise follow-ups.

## Open questions

This remains a behavioral observation rather than a complete causal study. Useful follow-up experiments include:

- compare the first substantive action of fresh vs persistent Scientists from the same State;
- classify actions by how much they change the hypothesis family;
- compare models under identical research memory and implementation;
- test trajectory-light inheritance where factual memory is visible before compressed trajectory memory;
- measure whether large score improvements disproportionately follow exploratory moves.
