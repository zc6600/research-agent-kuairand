# Gemini 3.7 Flash Heterogeneous-Subagent Baseline

## 1. Scope and headline result

This document records the delegated-subagent `gemini-3.7-flash` experiments for KuaiRand-Pure.
It is separate from the direct single-agent `gemini-3.7-flash` baseline in
[`direct-gemini-3.7-flash-goal-baseline.md`](direct-gemini-3.7-flash-goal-baseline.md): here the main `gemini-3.7-flash` agent delegates candidate
implementation/evaluation to subagents and, when possible, delegates the
comparison to a comparator subagent.

The canonical delegated run is
`gemini-3.7-flash-heterogeneous-subagents-2026-08-31`. It finalized seven
complete rounds and produced candidate results for Round 08 before the `gemini-3.7-flash`
runner hit a model quota error. Its best finalized public-validation checkpoint
was:

| Metric | Best delegated checkpoint | Official FM control | Delta |
|---|---:|---:|---:|
| GAUC | 0.6715 | 0.6671 | +0.0044 |
| nDCG@5 | 0.5379 | 0.5358 | +0.0021 |
| Primary = mean(GAUC, nDCG@5) | **0.6047** | **0.6015** | **+0.0032** |

The best checkpoint is the Round 04 `variant-v2` Log-Duration DCN-FM. The
result is an artifact-backed public-validation result, but the overall `gemini-3.7-flash`
session is incomplete: the process ended with `RESOURCE_EXHAUSTED (429)` and
there is no Round 08 comparator decision.

## 2. Experiment registry

| Experiment | Design | Completion | Best recorded public Primary | Status for later aggregation |
|---|---|---|---:|---|
| [`gemini-3.7-flash-heterogeneous-subagents-baseline`](../research-worlds/gemini-3.7-flash-heterogeneous-subagents-baseline/baseline_runs/run_log.md) | Three heterogeneous candidates per round plus comparator | Rounds 01–07 complete; Round 08 candidates only | **0.6047** | **Canonical partial run** |
| `same-architecture diagnostic` | Three independent realizations of the same DCN architecture brief | Round 01 candidates partial; no comparator | 0.6027 | Context only; raw world not retained in report-scoped archive |
| `earlier superseded diagnostic` | Earlier subagent run | Round 01 incomplete evidence; Round 02 scripts only | 0.6024 | Context only; raw world not retained in report-scoped archive |

The first attempt is retained for provenance, but its comparator report contains
test-split metrics even though the task contract forbids test development or
reporting, and it marks `v2` as missing. It should not be treated as an
independent validated result.

## 3. Task and evaluation protocol

- Dataset: KuaiRand-Pure `long_view` ranking.
- Training split: `log_standard_4_08_to_4_21_pure.csv`.
- Public validation split: `log_public_4_22_to_4_28_pure.csv`.
- Official metrics: within-user GAUC, nDCG@5, and
  `primary = mean(GAUC, nDCG@5)`.
- Control used by the delegated runs: GAUC `0.6671`, nDCG@5 `0.5358`, Primary
  `0.6015`.
- No hidden/test metric is used in the canonical result below.
- Candidate artifacts are stored in isolated `baseline_runs/cycles/` folders;
  the comparator is read-only and selects among completed candidate evidence.

The allowed-data inventory and task prompt are preserved in:

- [`GEMINI_SUBAGENT_PROMPT.txt`](../research-worlds/gemini-3.7-flash-heterogeneous-subagents-baseline/baseline_runs/GEMINI_SUBAGENT_PROMPT.txt)
- [`task.md`](../research-worlds/gemini-3.7-flash-heterogeneous-subagents-baseline/task.md)

## 4. Canonical heterogeneous-subagent trajectory

The following table summarizes the canonical clean run. Values are the best
public-validation Primary for each candidate; a retained row means that all
three candidates were rejected and the previous champion was kept.

| Round | Research direction | v1 | v2 | v3 | Comparator / decision | Active Primary |
|---:|---|---:|---:|---:|---|---:|
| Control | Official 5-field FM | — | — | — | Establish control | 0.6015 |
| 01 | CWM feature exploration | 0.6007 | **0.6020** | 0.6004 | Keep v2: 10-field user-demographic FM | 0.6020 |
| 02 | Factorization rank and capacity | 0.5998 | 0.6009 | 0.6004 | Reject all; retain Round 01 v2 | 0.6020 |
| 03 | DeepFM / Wide&Deep / DCN-FM | 0.6039 | 0.6036 | **0.6041** | Keep v3: DCN-FM | 0.6041 |
| 04 | Duration transformations | 0.6041 | **0.6047** | 0.6034 | Keep v2: 20 log-duration bins | **0.6047** |
| 05 | Hour/day/week temporal context | 0.6044 | 0.6043 | 0.6044 | Reject all; retain Round 04 v2 | 0.6047 |
| 06 | Click/like/tri-task auxiliary losses | 0.6043 | 0.6041 | 0.6041 | Reject all; retain Round 04 v2 | 0.6047 |
| 07 | Popularity, IPS, and user-history priors | 0.6037 | 0.6044 | 0.6032 | Reject all; retain Round 04 v2 | 0.6047 |
| 08 | Causal sequential state features | 0.6019 | 0.6034 | 0.6040 | **No comparator; candidates only** | 0.6047 |

The selected Round 04 checkpoint is a 10-field DCN-FM with `k=16`, 20 uniform
log-duration bins, Adam with learning rate `0.001`, L2 `1e-6`, batch size
`8192`, and pointwise BCE. Its fields are user/video/tab information, the
log-duration bucket, and five user-profile range fields.

### Round 08 candidate evidence

Round 08 did not reach the comparator stage, so these are candidate results,
not an adopted decision:

| Candidate | Added state feature | GAUC | nDCG@5 | Primary | Delta vs Round 04 champion |
|---|---|---:|---:|---:|---:|
| v1 | Causal `last_author_id` | 0.667421 | 0.536312 | 0.601867 | -0.002833 |
| v2 | Cumulative user-interaction count bin | 0.669819 | 0.536983 | 0.603401 | -0.001299 |
| v3 | Causal `last_tab` | 0.670541 | 0.537465 | 0.604003 | -0.000697 |

The candidate-level reports and structured results are preserved under
[`cycle-08`](../research-worlds/gemini-3.7-flash-heterogeneous-subagents-baseline/baseline_runs/cycles/cycle-08/).

## 5. Same-architecture subagent experiment

This follow-up gave all three subagents the same DCN/Cross-Network family brief,
while leaving the concrete dimensions, cross formulation, deep layers,
regularization, optimizer, and schedule to each subagent. It was intended to
test whether independent implementations of one architecture family were more
useful than heterogeneous research directions.

Only Round 01 reached the implementation stage, and the comparator was never
run:

| Candidate | Realization | GAUC | nDCG@5 | Primary | Evidence status |
|---|---|---:|---:|---:|---|
| v1 | DCN implementation | — | — | — | Training artifact exists; formal result/report missing |
| v2 | Parallel DCN-v2 matrix cross + deep MLP | 0.667874 | 0.536847 | 0.602360 | Complete candidate report and JSON |
| v3 | DCN-v2 low-rank multi-head matrix cross | 0.668801 | 0.536521 | **0.602661** | Complete JSON; no comparator |

Both measured candidates improved on the `0.6015` FM control by less than
`0.0012` Primary and were well below the canonical heterogeneous-run champion
`0.6047`. Therefore this experiment is useful as a diagnostic, but not as a
completed 12-round comparison.

## 6. Resource and runner accounting

The `gemini-3.7-flash` `baseline.log` records the root/main agent's usage, but it does not
inline the usage of native subagent conversations. The following audit also
reads the conversation databases referenced by each `subagent_info` event.
The root database sums exactly to the usage envelope in `baseline.log`, which
cross-checks the field mapping. “Reported total” means input + output, matching
the runner's `total_tokens`; thinking tokens are a subset of output and are not added
again. “Including cache” means reported total + cache-read tokens.

| Experiment | Wall time | Main input / output / thinking | Main reported total | Native subagent sessions | Subagent input / output / thinking | Subagent reported total | Combined reported total | Combined cache-read | Combined including cache | Runner result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Clean heterogeneous | 2,274.27 s (37m 54s) | 927,868 / 69,508 / 16,339 | 997,376 | 32 | 6,007,482 / 721,791 / 182,641 | 6,729,273 | **7,726,649** | 31,880,628 | **39,607,277** | `ERROR`, quota 429 |
| Same architecture | 1,038.08 s (17m 18s) | 197,464 / 20,902 / 8,993 | 218,366 | 3 | 1,023,287 / 137,971 / 29,046 | 1,161,258 | **1,379,624** | 7,457,956 | **8,837,580** | `ERROR`, quota 429 |
| Earlier attempt | 577.02 s (9m 37s) | 379,622 / 22,464 / 9,369 | 402,086 | 7 | 1,875,381 / 142,840 / 39,463 | 2,018,221 | **2,420,307** | 12,924,468 | **15,344,775** | `ERROR`, timeout |

For the canonical clean heterogeneous run, the 32 native sessions are eight
each of `variant-v1`, `variant-v2`, `variant-v3`, and `comparator`. Thus the
previously reported `997,376` was the main-agent subtotal, not the experiment
total. The corrected all-agent figure is `7,726,649` before cache-read context,
or `39,607,277` when cache-read context is included.

The raw runner logs were stored under the child repository's private `.git/`
metadata and are intentionally not part of the public archive. The public
boundary for this comparison is the retained `run_log.md`, per-cycle candidate
reports, structured results, and the token ledger above; the missing private
logs do not change the provisional status of the run.

## 7. Important audit qualifications

1. **Incomplete final round.** Round 08 of the clean run has no comparator
   report or decision. The active champion therefore remains the Round 04
   checkpoint by the last completed decision, not by a Round 08 vote.
2. **Sequential-feature protocol risk.** The Round 08 implementations sorted
   train and validation rows by `time_ms` to construct causal state. The task
   contract requires preserving official row order. Even though the reported
   state construction is causal, the Round 08 negative results should be
   treated as provisional until row-order compliance is independently checked.
3. **Runner status.** Both recent delegated sessions ended with a structured
   `ERROR` and `RESOURCE_EXHAUSTED (429)`, despite an exit code of zero. The
   persisted candidate artifacts are usable, but the sessions are not complete
   12-round runs.
4. **Metric scope.** Only public-validation metrics from the clean run and the
   same-architecture candidate JSON files are eligible for the later summary.
   The earlier comparator's test numbers are explicitly excluded.
5. **No universal architecture claim.** The result supports the claim that the
   heterogeneous delegated search found a strong public-validation checkpoint
   under this run, not that subagents are intrinsically better than a single
   agent. The direct `gemini-3.7-flash` and Codex baselines remain the appropriate controls.

## 8. Recommended aggregation record

For a later comparison table, use the following single canonical row and keep
the partial experiments as separate notes:

| System | Search mechanism | Completed research scope | Best eligible public Primary | Status |
|---|---|---|---:|---|
| `gemini-3.7-flash` subagent-assisted (heterogeneous) | 3 candidate subagents + comparator per round | 7 finalized rounds; Round 08 candidates only | **0.6047** | Partial run; eligible with caveats |
| `gemini-3.7-flash` subagent-assisted (same architecture) | 3 independent same-brief candidates | Round 01 partial | 0.602661 | Diagnostic only |

This keeps the `.6047` result available for aggregation while preserving enough
provenance to avoid counting incomplete candidates or invalid test metrics.

## 9. Document statistics

Measured with `wc` on this file:

- Character count: 11,855
- Whitespace-delimited word count: 1,599
- Line count: 189
