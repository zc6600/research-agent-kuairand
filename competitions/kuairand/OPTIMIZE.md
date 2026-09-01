# KuaiRand Task Optimization

These are reusable **task-specific optimization implications** derived from the KuaiRand challenge contract and evaluator. They help the Scientist spend benchmark opportunities intelligently; they are not a prescribed research plan and do not choose the next model, feature, loss, or experiment.

## Optimize the actual score

The development objective is the valid public-validation `primary = mean(GAUC, nDCG@5)` score. Scientific understanding, diagnostics, falsification, and uncertainty reduction are useful when they improve the ability to discover, evaluate, choose, or rule out interventions that could produce a better valid checkpoint. They are not substitute objectives.

When several scientifically reasonable directions are available, prefer ones with larger plausible addressable impact on `primary`, while keeping uncertainty explicit. Useful evidence can include the affected users/items/interactions, evaluator weighting, metric decomposition, controlled ablation, oracle/counterfactual perturbation, or another faithful bound. Do not invent numeric precision when the headroom is unknown.

A supported mechanism becomes more useful when it has an intervention path: once an explanation is actionable, ask what concrete implementation change would follow if it is true and why that change could affect GAUC, nDCG@5, or both. Do not spend repeated compute only refining an explanation when a faithful score-bearing intervention can test whether it matters.

## Protect Full evaluations

The task declares convergence after `N = 3` consecutive **Full** evaluations without validation-primary improvement beyond `ε = 0.002`. Smoke and Medium evaluations are neutral to that counter.

Therefore treat Full evaluations as scarce decision points rather than routine debugging runs. Before spending one, ask whether a cheaper **faithful** experiment can reject the idea or resolve the uncertainty that determines whether Full evaluation is worthwhile. Prefer that smaller test when it preserves the relevant mechanism. Skip the gate and use the fidelity required when a reduced experiment would distort grouping, temporal structure, statistical power, or evaluator behavior.

This is a task-specific resource strategy, not a universal rule that every Full evaluation must have a gate.

When a valid gate gives clear negative evidence for the current candidate, **fail fast on that candidate** rather than spending a Full evaluation merely to rescue it. A failed gate is not by itself a reason to end the Scientist session: while useful session budget remains, use scientific judgment to try another worthwhile direction. The gate informs the decision; it does not prescribe how the next direction must be chosen.

## Control seed expansion

Seed expansion is a variance/robustness check, not a substitute for evidence that the underlying mechanism improves the score. Do not expand from one seed to 4 or 8 seeds merely because the absolute primary has crossed `0.605`, or because a weak Medium result is inconclusive. Use a predeclared `+0.0008` primary improvement as the operational threshold for escalating seed count.

For a new hypothesis, use a predeclared escalation rule: begin with one faithful Medium screen; expand to 2–4 seeds only when the candidate improves primary by at least `0.0008` against a matched control at the same fidelity; spend a Full confirmation only when that evidence resolves a decision that matters; and do not escalate to 8 seeds unless the 4-seed Full result improves primary by at least `0.0008` over the current frontier or a predeclared variance question requires it. If a Full candidate does not meet the threshold against the incumbent, stop that candidate instead of adding seeds to search for a favorable outcome.

This is a resource-control heuristic, not a statistical-significance threshold. Keep seed counts comparable when interpreting deltas, and remember that averaging independently learned models can over-smooth a candidate rather than improve it.

## Track the real frontier

A candidate is not the score frontier merely because it beats its immediate parent. Compare Full candidates against the current validation-best valid checkpoint as well as against whatever scientific control is needed to interpret the experiment.

A descendant that improves on its parent but remains below the best-so-far score is useful evidence, not a new score frontier. Preserve the validation-best checkpoint until another valid Full result surpasses it.

## Treat small deltas carefully

The published `0.0008` standard deviation is a five-seed variability reference for the organizer's baseline hidden-test result. It is **not** a universal significance threshold for other models or for public validation. Likewise, the convergence threshold `ε = 0.002` is a competition accounting rule, not a statistical-significance claim.

When a claimed improvement is of similar order to plausible run-to-run variability, use an appropriate robustness check before treating it as reliable: fixed comparable splits, paired recipes, repeated seeds, or another task-faithful uncertainty check. Keep the effect uncertain when the evidence cannot separate it from noise.

## Decision priorities

Use these as qualitative priorities, not a scoring rubric:

1. **Validity** — leakage, hidden-test tuning, evaluator artifacts, unsupported comparisons, and irreproducible gains do not count.
2. **Objective impact** — prefer interventions with credible potential to improve the validation-best `primary` checkpoint.
3. **Information value** — prefer experiments that can materially change what deserves further compute.
4. **Cost** — among faithful ways to answer the same decision, prefer the cheaper and faster one.

Do not turn these priorities into fabricated probabilities or utilities. Do not use this file to write "try X next"; the fresh Scientist still chooses the scientific direction.
