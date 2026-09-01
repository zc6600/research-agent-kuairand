# Baseline, Token, and LLM-Failure Synthesis

**Snapshot:** 2026-09-01  
**Scope:** KuaiRand-Pure public validation only

## Decision summary

The defensible competition claim is not that Research Agent makes weak models
strong. The direct controls already show that capable coding agents can optimize
the task. The stronger result is that Research Agent produced the best retained
public-validation checkpoint while preserving a substantially clearer boundary
between a metric observation and a scientific claim.

The comparison uses measured **non-cache input + output tokens**. Cache-read
context is reported separately in the source ledgers because cache accounting
differs across runners and would otherwise dominate the horizontal axis.

![Primary score versus measured non-cache LLM tokens](../../../docs/figures/token-score-comparison.svg)

| Agent system | Non-cache input + output | Best public-validation Primary | Evidence qualification |
|---|---:|---:|---|
| **`gpt-5.6-luna` 3h direct Goal baseline** | **404,934** | **approximately 0.6046** | Provisional: report/README score with measured Codex telemetry; terminal closed after `task_complete` |
| **AGY `gemini-3.7-flash` 2h direct Goal baseline** | **1,117,370** | **0.6045803** | Artifact-backed corrected rerun; target binding and independent re-score documented |
| `gemini-3.7-flash`-only Research Agent trajectory, through Cycle 2 | 2,070,960–2,898,630* | 0.6052 | Artifact-backed; online-history semantics noted |
| Research Agent submission | 6,833,808 | **0.6059363** | Verified implementation, full ledger, reproduction result, and output check |
| `gemini-3.7-flash` heterogeneous subagents | 7,726,649 | approximately 0.6047 | Artifact-backed separate run; not the submitted result |

\* The `gemini-3.7-flash`-only range is an accounting bound, not score uncertainty. Its META
session spans Cycles 2–4 and exposes only one aggregate token total.

The official validation reference, Primary `0.6016`, is a horizontal benchmark
rather than a token-bearing agent run. The Research Agent submission is `+0.0043363` over that reference,
approximately `+0.00134` over the `gpt-5.6-luna` 3h direct baseline, `+0.0007363` over
the Cycle-2 `gemini-3.7-flash`-only trajectory result, and approximately `+0.00124` over the
delegated `gemini-3.7-flash` result. These are
modest gaps. With one recorded run per condition and
non-identical control protocols, they do not establish statistical significance
or a causal architecture ablation.

## What the controls establish

The direct agents are strong controls, not straw men. `gpt-5.6-luna` reached approximately
`0.6046` through a six-field FM with positive-class weighting and a `tab×hour`
context field, while the corrected AGY `gemini-3.7-flash` run searched deep interaction,
auxiliary-task, and ensemble variants and reached `0.6045803`. The heterogeneous
`gemini-3.7-flash` run searched more broadly again and reached approximately `0.6047`.

This supports two useful conclusions:

1. long-horizon coding agents can perform meaningful model search without the
   Research Agent control plane;
2. more agents or more tokens do not mechanically yield a better retained
   result.

The token plot therefore should not be presented as a conventional efficiency
frontier. It is an outcome-versus-investment view with evidence qualification.
The `gpt-5.6-luna` 3h direct baseline remains the lowest-token strong optimizer in this
updated comparison; the corrected AGY run reaches `0.6045803` with a complete target-bound
rerun; the `gemini-3.7-flash`-only Research Agent reaches a strong `0.6052` by Cycle 2; the Research Agent submission is the
highest-scoring verified research result; heterogeneous delegation consumed
slightly more measured tokens without surpassing the submitted result.

## What score alone hides

The baseline audit found cases in which executable code and plausible metrics
did not support the accompanying mechanism claim:

- the `gemini-3.7-flash` implementation described as within-user BPR paired examples without
  enforcing a shared user;
- one `gemini-3.7-flash` target-statistics branch reused each training row's own or later
  labels when constructing features;
- the Codex pair sampler included a small number of same-user, same-video
  conflicting-label pairs;
- both controls repeatedly selected against the same public-validation set and
  therefore provide search outcomes, not independent generalization checks.

The `gemini-3.7-flash`-only comparison is frozen after Cycle 2 and was run separately with
`gemini-3.7-flash` High for both META and Scientist. E008 trained a single Seed-42 DIN and
reached GAUC `0.6725`, nDCG@5 `0.5380`, and Primary `0.6052` at 02:00:48
Singapore time, about 14 minutes after the resume began. The Cycle-2 Scientist
session used 802,865 non-cache tokens. Together with the complete Cycle-1 cost,
2,070,960 tokens are directly attributable through Cycle 2. Because the
persistent META session reports only one aggregate across Cycles 2–4, the exact
Cycle-2 META slice is unavailable; assigning the entire 827,670-token aggregate
produces a conservative upper bound of 2,898,630.

The shared validation sequence builder uses earlier validation labels when it
constructs engaged/negative-history facets. E008, however, uses only the `vid`
facet and therefore does not consume those label-conditioned histories. The
remaining qualification is narrower: it uses earlier validation impression IDs
as online history, whose compatibility with the organizer's intended offline
protocol should be stated explicitly.

The submitted Research Agent run used a different, heterogeneous runner allocation.
`gemini-3.7-flash` served as META in all four cycles; Scientist used `gpt-5.6-sol`
in cycle 1, `gemini-3.7-flash` in cycles 2 and 4, and `gpt-5.6-luna` in cycle 3.
This distinction matters when interpreting the plot: the `gemini-3.7-flash`-only trajectory is
evidence for what a `gemini-3.7-flash`-only research trajectory explored, while the submission is the
outcome of a mixed-model research process.

## The LLM-failure story

The report should focus on two failure classes, not process interruption:

### Scientific-validity failure

An LLM can produce code that runs and a metric that improves while the
measurement does not support the stated conclusion. This includes leakage,
incorrect sample semantics, evaluator mismatches, and a mismatch between the
reported best configuration and the saved artifact. These failures are more
dangerous than visible runtime errors because they resemble successful science.

META is best described as an experiment-level evidence auditor, not a formal
verifier. It can prevent unsupported claims from becoming inherited research
memory, but it cannot guarantee that every implementation defect is detected.
The `gemini-3.7-flash`-only audit is an explicit boundary case and should be disclosed rather than
hidden.

### Cognitive or trajectory failure

A persistent LLM trajectory can continue producing sophisticated experiments
while exploring an increasingly narrow neighborhood of the incumbent. The
scientific value of a direction may decline even while its contextual salience
remains high. Research Agent's handoff is designed to preserve externalized
facts, negative evidence, and the best implementation while allowing a fresh
Scientist to reconsider the search direction.

The concise formulation is: **inherit the evidence, not the momentum**.

This is an observed behavioral hypothesis, not a universal claim about any one
model family. The current records suggest `gpt-5.6-luna` was more locally exploitative in
a mature research world, while `gemini-3.7-flash` explored broader architectural
changes under the same general framework.

## Report-ready claim and boundary

> Single agents were already capable of finding strong recommendation models.
> The harder problem was deciding which improvements were scientifically valid
> and preventing one trajectory's unsupported interpretation or search momentum
> from becoming the next trajectory's ground truth. Research Agent produced the
> highest verified public-validation checkpoint in our recorded comparison and
> preserved the evidence required to inspect why it was retained.

The `gpt-5.6-luna` 3h baseline's raw snapshot contains 28,069,574 total tokens,
including 27,664,640 cache-read tokens. Under the figure's non-cache convention
it contributes 335,122 input plus 69,812 output tokens, or 404,934 comparison
tokens; reasoning tokens are a subset of output and are not added again. The
run's three-hour budget was not fully consumed: its measured wall time was about
1h 55m, and the interactive terminal was closed after `task_complete`.

Do not claim that the submission is token-efficient, statistically significant, or a
fully controlled causal proof of the architecture. Do claim that it is the
best verified retained result in the recorded comparison and that its evidence
chain is materially stronger than the provisional direct controls.

## Ongoing-result admission rule

The comparison keeps provisional and qualified results visible, but they are
not promoted to verified claims. A result may enter the comparison table when
all of these conditions hold:

1. the run has a closed result and measured whole-system token total;
2. the score uses the official public-validation evaluator;
3. the claimed best model matches the retained prediction artifact;
4. protocol concerns are either resolved or stated next to the result.

An unresolved protocol concern keeps a result **provisional** and disqualifies
causal or leakage-free interpretations; it does not justify silently deleting a
useful observed checkpoint. The Cycle-2 E008 qualification and token boundary
are preserved in the [evidence snapshot](../evidence/gemini-3.7-flash-only-cycle2-e008.md).
