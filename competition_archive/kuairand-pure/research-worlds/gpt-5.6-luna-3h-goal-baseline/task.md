# Task Contract

## Challenge target

This project targets an offline short-video recommendation ranking task on the KuaiRand family, collected from Kuaishou. The required benchmark is **KuaiRand-Pure**; **KuaiRand-1K** and **KuaiRand-27K** are optional bonus benchmarks. The task is not full production retrieval: assume the candidate pool is available and focus on scoring/ranking candidates for each user and interaction context.

The fixed prediction label is `long_view` (`starter_kit/data.py:LABEL`). Report **GAUC**, **nDCG@5**, and `primary = mean(GAUC, nDCG@5)` using only the organizer's evaluator (`starter_kit/evaluate.py`); report each metric's delta against the official baseline. Do not substitute AUC-style global metrics or other labels. Note: sections of the official Problem Statement still carry stale `NDCG@10 / Recall@50` wording from before the 2026-08-26 18:33 revision; where the Problem Statement and the Starter Kit disagree, the Starter Kit prevails (protocol priority 1). Official baseline (FM k=16, lr=0.001, 5 categorical fields, numpy-only): hidden-test GAUC 0.6610 / nDCG@5 0.5282 / primary 0.5946 (mean over 5 seeds, std 0.0008); validation GAUC 0.6674 / nDCG@5 0.5357 / primary 0.6016; self-check rungs: random primary 0.4753, item popularity 0.5715. Evaluator conventions are pinned in the kit: zero-positive users contribute nDCG = 0 and stay in the average; GAUC counts only users with 0 < positives < impressions, weighted by positive count; nDCG gain = 2^rel − 1. Convergence rule: ε = 0.002, N = 3 consecutive Full evaluations without validation-primary improvement beyond ε. Only a completed Full evaluation with the required public-validation primary metric increments or resets this counter; Smoke and Medium evaluations, including a failed preregistered gate, are neutral and neither increment nor reset it. Budget exhaustion and hard-cycle limits are stopping conditions, not semantic convergence.

## Optimization objective

The terminal development objective is to **maximize the valid public-validation `primary` score**, subject to every data-access, leakage, evaluator, and reproducibility rule in this contract. The final scored checkpoint is the validation-best valid result at convergence; hidden test is never a development signal.

Scientific understanding is instrumental to this task objective. Diagnostics, falsification, bottleneck clarification, and uncertainty reduction are valuable when they improve the ability to discover, evaluate, choose, or rule out interventions that could produce a better valid checkpoint. They are not substitutes for the terminal objective.

When choosing among scientifically valid research directions, prefer directions with larger plausible **addressable impact on `primary`**, all else equal. Before investing heavily in a bottleneck, estimate its score opportunity using evidence appropriate to the mechanism: affected users/items/interactions, evaluator weighting, metric decomposition, controlled ablation, oracle/counterfactual perturbation, or another faithful bound. The estimate may be qualitative when a reliable numeric bound is unavailable, but it must distinguish a potentially material direction from a clearly tiny one. Do not invent precision or discard a direction merely because headroom is initially unknown; use the cheapest faithful diagnostic that can make the opportunity clearer.

A mechanism hypothesis should have an **intervention path**. Once evidence makes the mechanism actionable, ask what concrete model, feature, objective, sampling, representation, training, or ranking change should follow if the hypothesis is true, and why that intervention should affect GAUC, nDCG@5, or both. Do not spend repeated cycles explaining an already-supported mechanism when a faithful score-bearing intervention can now test whether it matters to the task objective.

A candidate is not a frontier improvement merely because it beats its immediate parent. Compare Full candidates against the current **validation-best valid checkpoint** as well as against the scientific control needed for the experiment. Preserve the validation-best checkpoint unless another valid Full evaluation surpasses it; a locally improved descendant that remains below the best-so-far score is useful evidence, not a new score frontier.

Interpret small deltas cautiously. The published `0.0008` standard deviation is an empirical five-seed variability reference for the official baseline hidden-test result, **not** a universal significance threshold for every model or for public validation. When observed improvements are of similar order to plausible run-to-run variability, use fixed comparable splits, paired recipes, repeated seeds or other appropriate uncertainty checks before treating the effect as reliable. The convergence threshold `ε = 0.002` is an organizer protocol rule, not a claim of statistical significance. Record an effect as uncertain when the available evidence cannot distinguish it from noise.

Research-direction priority is therefore:

1. **Validity first** — leakage, hidden-test tuning, evaluator artifacts, unsupported comparisons, or irreproducible gains do not count.
2. **Objective impact** — prefer bottlenecks and interventions with credible potential to improve the validation-best `primary` checkpoint.
3. **Information value** — prefer experiments that can materially change which intervention or direction should receive further compute.
4. **Cost** — among faithful ways to answer the same decision, prefer the cheaper and faster one.

Do not turn these priorities into fabricated numeric utilities such as guessed probabilities of success. Use them as qualitative decision criteria grounded in observed evidence.

## Benchmarks

| Dataset | Required use | Users | Scale and purpose |
|---|---|---:|---|
| KuaiRand-Pure | Required; 100% of primary score | 27,285 | 1,436,609 standard interactions over 7,551 items; compact ranking/multi-task benchmark |
| KuaiRand-1K | Bonus | 1,000 | 11,713,045 standard interactions over roughly 4.37M videos; roughly 4.3 GB unpacked |
| KuaiRand-27K | Bonus | 27,285 | 322,278,385 standard interactions over roughly 32M videos; roughly 46 GB unpacked, intended for long-sequence, debiasing, OPE, and large-scale research |

All versions contain standard recommendation logs, randomized-exposure logs, user features, basic video features, and statistical video features. The random logs contain 1,186,059 interactions for Pure/27K and 43,028 for 1K. The released IDs are re-indexed. Random exposure is the key resource for unbiased/off-policy analysis; it is not a replacement for the challenge’s prescribed ranking split.

## Downloading the data

Use the official [KuaiRand repository](https://github.com/chongminggao/KuaiRand) and [Zenodo record 10439422](https://zenodo.org/records/10439422) when an experiment actually requires data. Do not download or extract a dataset merely because it is listed here. Verify archives before extraction when possible: Pure MD5 `0820331067a3784d9691136f772b35a7`, 1K MD5 `6b0b9c8222d67fcd4c676218edca3f1f`, and 27K MD5 `3e3c799a24e2d23a4d2c757fbf9adf59`. The official archive sizes are approximately 194 MB, 4.3 GB, and 46 GB after extraction respectively.

The Pure layout is `KuaiRand-Pure/data/` containing `log_random_4_22_to_5_08_pure.csv`, `log_standard_4_08_to_4_21_pure.csv`, `log_standard_4_22_to_5_08_pure.csv`, `user_features_pure.csv`, `video_features_basic_pure.csv`, and `video_features_statistic_pure.csv`. The 1K and 27K layouts follow the same names with `_1k`/`_27k` suffixes; 27K log and statistic files are split into parts. Optional official video captions and hierarchical categories are available from [Zenodo record 18159199](https://zenodo.org/records/18159199), joined by `final_video_id`; use them only when the challenge kit permits them and record the feature source.

In managed competition projects, that raw layout is a control-plane input and is not available to the research agent. Use only the files materialized under `competition_data/`; do not locate the raw root, recreate the hidden/public split, or fall back to a loader that materializes hidden test. Evaluation code is part of the Scientist's research implementation: use the organizer's `starter_kit/evaluate.py` semantics, but build and run evaluation against the curated public-validation data directly.

## Data semantics and challenge split

The standard log from 2022-04-08 through 2022-04-21 is historical training data. The standard log from 2022-04-22 through 2022-05-08 is the evaluation window. The official challenge split is by date, not by row count: 2022-04-22..28 is public validation and 2022-04-29..05-08 is hidden test. This date-based definition replaced an earlier first-50%/last-50% wording and avoids timestamp tie-breaking ambiguity; use the starter-kit splitter (`data.py`) as the authority. Never create a random split or tune on hidden-test rows.

Important log fields include `user_id`, `video_id`, `date`, `hourmin`, `time_ms`, `is_click`, `is_like`, `is_follow`, `is_comment`, `is_forward`, `is_hate`, `long_view`, `play_time_ms`, `duration_ms`, `profile_stay_time`, `comment_stay_time`, `is_profile_enter`, `is_rand`, and `tab`. `is_click` is click in the two-column UI and valid play in the single-column UI; valid play is defined from `play_time_ms` and video duration by the official dataset rules. `tab` identifies one of 15 recommendation scenarios. Do not discard `tab` or timestamps without checking their effect.

User features include activity/status, social-count ranges, registration age, and encrypted categorical one-hot fields. Basic video features include author, type, upload date/type, visibility, duration, dimensions, music, and tags. Statistical video features contain monthly/day-and-scenario averages such as shows, plays, completion, likes, follows, shares, reports, and collection. Audit their observation time before using them: aggregate statistics can leak information from the evaluation period.

## Research-relevant recommendation knowledge

KuaiRand supports ID embeddings, user/item/author/category crosses, context and temporal features, sequential user-history encoders, factorization/DeepFM-style interaction models, and ranking-specific losses or negative sampling. Its 12 feedback signals also support multi-task learning: auxiliary signals such as like, follow, long-view, and play time may improve long-view ranking, but shared and task-specific capacity must be balanced to avoid task conflict. Random-exposure rows enable exposure-bias correction and counterfactual/off-policy evaluation, especially on 1K/27K. The challenge objective remains the prescribed **GAUC + nDCG@5 primary ranking score**, not an OPE metric.

Use the [KuaiRand paper](https://arxiv.org/abs/2208.08696) for dataset assumptions and the [CWM reference repository](https://github.com/hyz20/CWM) for a published KuaiRand-Pure recommendation baseline/reference implementation. Treat both as research references; the organizer-provided baseline and evaluator remain authoritative for scoring.

## Rules that affect every experiment

Training may use only KuaiRand data. Open-source libraries, papers, public solutions, and generic pretrained weights are allowed, but external training datasets and weights trained on these benchmarks’ test labels are prohibited. Development may use training data and public validation feedback only. The final submission is evaluated once on hidden test, and the scored checkpoint is the validation-best result at convergence. Record GAUC, nDCG@5, and primary = mean(GAUC, nDCG@5), and compare each against the official baseline using `delta(m) = agent(m) - baseline(m)`.

## Starter kit and evaluation contract

The organizer starter kit ships inside this repository at `starter_kit/` (unpacked at project initialization from `kuairand-starter-kit.zip`). It contains the official splitter (`data.py`), evaluator (`evaluate.py`), baseline (`baseline.py`, FM k=16, lr=0.001, 5 categorical fields, numpy-only, about 40 s on one CPU core), published scores (`baseline_scores.json`), submission tooling (`submit.py`), and an ablation/direction analysis (`ablation_features.py`). Use these files as the authoritative contract; do not invent replacements. Record the kit version and discovered paths in the engineering or research record.

The official split is by date window with deterministic row order (files read in documented order, filtered by date, original order preserved): train = standard log 2022-04-08..2022-04-21 (1,141,112 rows); public validation = 2022-04-22..2022-04-28 (124,909 rows); hidden test = 2022-04-29..05-08 (170,588 rows). Do not reorder rows by user, date, or `time_ms`; do not substitute a positional or random split.

Use public validation only for evaluation, tuning, and model selection; do not train on it unless the starter kit explicitly permits that procedure. Never use hidden-test rows for development or tuning.

The prediction file format (`submit.py --make/--check/--score`), candidate handling, missing-value behavior, score direction, and metric calculation are defined by the official kit and must not be inferred from a different implementation. Record the kit version, prediction schema, GAUC, nDCG@5, primary score, validation-best checkpoint, and deltas against the official baseline when these are available. Do not hardcode baseline values without recording their source.

Treat statistical or aggregate features with an unknown observation cutoff as unavailable by default. Use them only after confirming that their source data does not include the evaluation window, and record the permitted columns and cutoff evidence.
