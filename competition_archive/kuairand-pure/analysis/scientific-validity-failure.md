# Scientific-Validity Failure: When an Experiment Runs but the Evidence Is Wrong

## Observation

One standalone-agent test exposed a failure that ordinary code-level robustness would miss.

The agent implemented a gate by applying the gate script directly to a sliced dataset. The pipeline executed and returned plausible metrics, but the measurement no longer represented the intended gate faithfully.

Nothing necessarily crashed. The danger was epistemic: a successful execution could have been promoted into an invalid scientific conclusion.

## Why this is different from a coding failure

A coding failure is often visible:

```text
exception
incorrect output format
test failure
process crash
```

A scientific-validity failure can look healthy:

```text
code runs
    ↓
metric appears plausible
    ↓
agent explains the result
    ↓
conclusion is still unsupported
```

The issue is the mapping between the **claim** and the **measurement**, not merely whether the implementation executes.

## Trajectory risk

In a single persistent trajectory, implementation, measurement, and interpretation are often produced by the same agent context.

That creates a correlated-error risk:

```text
agent chooses experimental design
        ↓
agent implements it
        ↓
agent observes plausible metric
        ↓
agent interprets metric through the same framing
```

A mistaken evaluation assumption can therefore survive several stages without triggering an obvious contradiction.

## META audit

META adds a second epistemic boundary after the Scientist trajectory.

Its job is not to re-review every line of code. Instead, it asks whether the experiment as a whole supports the claimed conclusion:

- What comparison was intended?
- What data/evaluator path actually produced the metric?
- Did a slice, proxy, gate, or shortcut change the meaning of the measurement?
- Are there unresolved confounds?
- Is the conclusion broader than the evidence?

In the gate example, this level of audit can detect that the evaluation procedure changed the meaning of the evidence even though the code itself ran successfully.

> **META audits experimental validity, not every line of implementation.**

## Why not universal code review?

Modern coding models can already inspect and modify substantial codebases. Asking META to duplicate the Scientist's line-by-line review would consume a large supervision budget while still not guaranteeing scientific validity.

The architecture therefore spends its second-pass reasoning budget at a higher-leverage boundary:

```text
experiment ran
        ↓
Does the evidence mean what the Scientist says it means?
        ↓
only then persist the scientific conclusion
```

## Architectural implication

Robustness for a research agent has at least two layers:

1. **Engineering robustness** — execution, recovery, reproducibility, and mechanical invariants;
2. **Epistemic robustness** — measurement fidelity, confounds, evaluator correctness, and justified conclusions.

Externalized research memory should contain the result only at the epistemic scope supported by the evidence.

This is one reason META sits at the trajectory handoff: it can prevent a plausible-looking mistake from becoming inherited scientific knowledge.

## Open questions

Useful follow-up analyses include:

- how often META weakens, rejects, or reframes Scientist conclusions;
- which failure classes are caught by tests vs scientific audit;
- whether independent auditors catch more correlated errors than persistent self-review;
- how much audit depth is needed before supervision cost outweighs value;
- whether particular evaluator shortcuts repeatedly create misleading evidence.
