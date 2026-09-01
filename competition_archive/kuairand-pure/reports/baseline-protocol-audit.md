# Codex / gemini-3.7-flash Baseline Process Audit

Audit date: 2026-08-31. The audit covers the code, run artifacts, data
directories, and narrative for
[`direct-codex-goal-baseline`](../research-worlds/direct-codex-goal-baseline) and
[`direct-gemini-3.7-flash-goal-baseline`](../research-worlds/direct-gemini-3.7-flash-goal-baseline), as well as
the narratives in
[`direct-codex-goal-baseline.md`](direct-codex-goal-baseline.md) and
[`direct-gemini-3.7-flash-goal-baseline.md`](direct-gemini-3.7-flash-goal-baseline.md).

## Executive conclusion

There is currently no direct evidence that hidden-test labels were necessarily
used. Static inspection alone also cannot establish that the public-validation
numbers are incorrect. However, the available material is not sufficient to
support the strong claim that the two baselines were completed under the same
Goal protocol and that their results are reproducible. The gemini-3.7-flash runtime status,
data loaders, and several experiment implementations must be fixed or the
results must be explicitly downgraded to provisional.

## P1: Must be addressed before comparison

### 1. The gemini-3.7-flash run failed, but the launcher recorded it as completed

- Evidence: the archived runner log (kept in private child-run metadata and
  represented in the public report and sanitized result summary) has
  `status: "ERROR"` with a network issue, while the corresponding `run.json`
  and `result.json` both report `completed` with `exit_code` set to `0`.
- Root cause: `src/research_agent/baseline.py:157-178` generates
  `terminal_status` from only the child-process exit code and does not parse the
  runner's structured error result.
- Impact: the claim that all research was completed in 53 minutes is not
  confirmed by the runner; code and scores left manually afterward cannot
  automatically be treated as the output of one successful complete run.
- Fix: make the runner return and validate structured status. Mark runs as
  `failed/partial` when they contain `ERROR`, a timeout, a missing final result,
  or an incomplete result, and require every experiment to record its command,
  stdout/stderr, metrics, and completion status.

### 2. The two baselines did not use the same verifiable budget and launch protocol

- The Codex 50-minute Goal record is in `baseline_runs/` and uses a custom
  `CODEX_GOAL_PROMPT.md`. It specifies 60 minutes/12 cycles, 15 minutes per
  experiment, and `epsilon=0.002`, and explicitly requires reading `AGENTS.md`.
- The gemini-3.7-flash record contains only `.git/.../run.json` and an aggregate log. It does
  not preserve the actual prompt, invocation arguments, or per-experiment output.
- There is also an independent Codex launcher artifact in private child-run
  metadata. It ran for
  about 7 minutes with an older single-turn prompt, and its log states that the
  full data was unavailable. It is not the 50-minute Goal run claimed in
  `baseline_runs/`.
- `baseline.py:158-163` calls `run_invocation` without passing a timeout. The gemini-3.7-flash
  runner even sets the CLI option `--print-timeout 24h`. The 60-minute limit is
  currently only a self-imposed constraint in the model prompt, not a hard
  harness constraint.

The impact is that the claimed "same 50-60 minute control condition" for Codex
and gemini-3.7-flash cannot be strictly verified from the artifacts. A run ending early due
to a network error also cannot be ruled out. The fix is to use one launcher, a
fixed prompt, fixed wall-time/cycle constraints, and an archive containing the
command, prompt hash, version, start and end times, and final status. Otherwise,
the two records should be explicitly labeled as exploratory runs under
different protocols.

### 3. The blank control was contaminated by research-project scaffolding

The baseline specification recommends a clean checkout so that `AGENTS.md` and
project research instructions do not enter the control (`references/baseline.md:28-33`).
However, both target directories contain `AGENTS.md`, `CLAUDE.md`, `PERSONAL.md`,
and `research_record/**`; the Codex Goal prompt also explicitly requires reading
`AGENTS.md`. This brings META/Scientist/State rules into a control that was
supposed to be a direct coding-agent baseline.

Fix: create two clean sibling checkouts from the same starting commit, keeping
only the task, starter, evaluator, and curated data required by the task. If
these files must remain, list them as control inputs in the report rather than
calling the control a pure blank control.

### 4. The official starter data loader is incompatible with the current curated data package

The current `competition_data/data` contains the train files and
`log_public_4_22_to_4_28_pure.csv`, but not
`log_standard_4_22_to_5_08_pure.csv`. The Codex
`starter_kit/data.py:20-22` opens the latter unconditionally, producing:

```text
FileNotFoundError: .../log_standard_4_22_to_5_08_pure.csv
```

Codex's `system/baseline_api.py` and part of the gemini-3.7-flash loader already bypass this
problem by using the public file. gemini-3.7-flash's `starter_kit/data.py:20-24` also has a
public fallback, but Codex's `starter_kit/baseline.py`, `submit.py`, and
`ablation_features.py` still cannot be reproduced from the documentation. This
is not an evaluator-formula error; the Codex "official baseline/data entry"
is broken, so the reproduction experiments in the two reports do not share one
entry point.

Fix: provide an explicit curated loader for hidden-free data, or make the
starter loader accept the public file and fail closed when it is missing. Each
report should record the actual loader and file manifest. The fallback in gemini-3.7-flash
scripts from a missing public file to
`log_standard_4_22_to_5_08_pure.csv` should also be removed, so that a mixed file
containing hidden-window rows cannot be read accidentally.

### 5. gemini-3.7-flash dense target statistics leak labels from the training samples themselves

`system/features.py:146-178` uses all training-row `long_view`, click, and play
statistics to construct item/author/user/history rates. Then
`system/run_experiment.py:34-35` calls `extract_features` on the same
`data.train_logs`, while `features.py:281-315` places those statistics directly
back into the input for each training row. As a result, the labels of the
training row itself, as well as labels from later rows in the training window,
can enter its features.

This is not "reading valid labels", but it is target-encoding self/future
leakage. It makes the training distribution of the 37-field plus 14-statistics
branch differ from the distribution at inference time, so its gain cannot be
interpreted as a leak-free research result. The final 8-field MT-DeepFM path in
`deepfm_advanced.py` does not call these dense statistics, so this finding does
not directly invalidate its final score.

Fix: use leave-one-out or strictly time-prefix statistics for training features;
for valid/test, use complete training statistics cut off before the split. Add
an assertion that constructing a row's features never uses that row's label.

### 6. gemini-3.7-flash's claimed within-user BPR is actually cross-user pairing

`system/trainer.py:29-41` only separates positive and negative labels within a
batch, then pairs the first `n_pairs` positive samples with negative samples.
Although `system/ranking_trainer.py:171-207` passes `u_idx` through the
DataLoader, it does not use `bu` when computing pair loss. The official evaluator
sorts within user groups (`starter_kit/evaluate.py:43-60`).

Therefore, the default `pair_weight=.2` in `run_experiment.py` and the BPR results
in the ranking trajectory do not optimize the claimed within-user preference.
They mix samples from different users, so the experiments cannot support the
claim that "within-user BPR" is effective. Fix this by explicitly constructing
same-user `(positive, negative)` pairs or sampling by user, and add a hard
`user(pos)==user(neg)` assertion and test.

## P2: Issues that can contaminate results or reduce reproducibility

### 7. The Codex pairwise sampler does not exclude conflicting labels for the same item

`system/baseline_api.py:368-383` buckets only by `user_id` and does not exclude
the same `video_id`. An inspection of the current training data found 9,295
duplicate `(user_id, video_id)` keys with conflicting labels. Among 382,579 pairs
sampled with seed 0, 323 were positive/negative conflicts for the same user and
video (about 0.084%). This gives the model a meaningless gradient that requires
the same item to be both higher and lower, contaminating the final pairwise
score, even though the proportion is small.

Fix: exclude the same video when constructing negative samples, or define an
explicit rule for repeated exposures and conflicting labels. The report should
record the number of valid pairs, discarded conflicts, and the sampling seed.

### 8. gemini-3.7-flash's `day_of_week` is not a weekday

`features.py:125-134`, `deep_high_signal.py:44-47`, and
`deepfm_advanced.py:217-220` all use `(date % 100) % 7`. This is only the day of
the month modulo 7, not the calendar weekday; the field is nevertheless named
`day_of_week`/`dow`. If the hypothesis is a weekday effect, the experiment uses
the wrong encoding.

Fix: use `datetime.strptime(str(date), "%Y%m%d").weekday()` and add a unit test
with a known date, such as 2022-04-08 being Friday. If a day-of-month bucket is
intended, rename it to avoid a misleading interpretation.

### 9. The evaluator API does not check score length

`system/baseline_api.py:612-617` passes scores directly to the official
evaluator, while `starter_kit/evaluate.py:43-47` uses ordinary `zip`. A short or
long score array can therefore be silently truncated. An audit reproduction on
four smoke rows passed one score or five scores and still returned a result; the
reported `rows` can differ from the number of scores actually evaluated.

Fix: require `len(scores) == len(rows)` at the `evaluate_scores` entry point and
add tests for short/long/NaN/non-finite scores. The existing
`score_rows(..., zip(..., strict=True))` does not replace this check at the
evaluator boundary.

### 10. The public validation set was repeatedly used for selection and cannot be called generalization confirmation

gemini-3.7-flash selected Seed 3 and a 5-seed ensemble on the same validation set. The first
MT-DeepFM training script also does not set a seed at function entry; only the
ensemble loop in `deepfm_advanced.py:283-293` sets a seed. The Codex final report
is a single-seed frontier. This is acceptable for competition tuning, but it
creates validation selection bias. The `0.6045` result cannot be presented as
independent generalization evidence, and the two different seed/search protocols
cannot be treated as equivalent comparisons.

Fix: fix and preregister the final recipe, report the mean and standard deviation
over all confirmation seeds, and distinguish the "best public-validation result
found during search" from "independent confirmation". If there is no additional
holdout, state explicitly that no independent confirmation was performed.

## P2/P3: Record and narrative issues

1. Both `research_record/EXPLORE.md` files remain empty `pending` templates.
   This may be intentional for blank controls, but the baseline record must
   explicitly say that `research_record` was not used; otherwise the templates
   and `STATE.yaml` can look like completed research evidence.
2. Both `STATE.yaml` files still describe the `S001` smoothed popularity
   baseline; the gemini-3.7-flash summary even calls it `earlier-direct-codex-baseline`. They cannot
   reproduce the final FM/DeepFM tree described in the reports. Record the base
   commit and final tree/diff hash, and mark the final code as unversioned run
   output, or create a matching snapshot.
3. Gemini has no per-experiment `baseline_runs/` record like Codex. The current
   `direct-gemini-3.7-flash-goal-baseline.md` values of 0.6045/0.6042 lack a
   corresponding command and raw output index; each stage should have its
   artifact record. The report now uses the exact field name `tag` and the
   phrase "best public-validation checkpoint" rather than implying independent
   generalization.
4. The FM API lacks unified validation for `factors`, learning rate, epochs,
   batch size, patience, and related parameters. Invalid parameters can produce
   empty training or low-level NumPy errors. Add entry-point validation and
   parameter-boundary tests so that research scripts do not treat exceptions as
   experiment results.

## Recommended fix order

1. Fix launcher status, timeout handling, and evidence archiving, then rerun Codex
   and gemini-3.7-flash from clean checkouts with the same starting point. Until then, label
   the gemini-3.7-flash headline `unverified` and the Codex result `provisional`.
2. Fix the curated loader and hidden-safe fallback so that the starter baseline,
   official evaluator, and two custom systems use the same file and split.
3. Fix gemini-3.7-flash training-statistics leakage, user-aware pair sampling, and weekday
   encoding, as well as the Codex conflict-pair and score-length guard; rerun
   the affected experiments.
4. Finally, update both baseline reports to distinguish the best public-validation
   result found during search from independent confirmation, and provide a
   complete artifact index.
