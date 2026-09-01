# `gemini-3.7-flash` Goal Baseline

## Executive summary

This document is the report-ready record of the direct `gemini-3.7-flash` Goal
control run for KuaiRand-Pure. It measures one direct `gemini-3.7-flash` agent powered by
`gemini-3.7-flash` working autonomously inside the task project for a bounded
long-horizon run. It is an agent-system baseline measuring the raw optimization
capability of the underlying coding model without the Research Agent
control plane.

The run systematically progressed through baseline reproduction, feature
engineering, FM hyperparameter grid search, pairwise ranking loss formulation,
compact high-signal DeepFM exploration, and finally Multi-Task DeepFM with
auxiliary click supervision, Exponential Moving Average (EMA) weight tracking,
and multi-seed ensembling. The single best checkpoint reached a
public-validation primary of 0.6045 (GAUC=0.6712, nDCG@5=0.5377), which is
+0.0029 above the published validation reference of 0.6016. The 5-seed
ensemble achieved a validation primary of 0.6042 (GAUC=0.6708, nDCG@5=0.5376).
No hidden-test score was used for selection or reported as the result of this run.

> Report-ready summary: A single direct `gemini-3.7-flash` Goal agent,
> operating without META, Scientist, subagents, or the Research Agent control
> plane, executed comprehensive feature engineering, FM tuning, and DeepFM
> multi-task architectures in approximately 53.5 minutes. It discovered that
> combining 8 high-signal fields with a compact DeepFM architecture (k=16, MLP [64],
> dropout 0.2) and auxiliary click supervision with EMA produced significant
> gains over the standard pointwise FM. Its best public-validation result was
> GAUC=0.6712, nDCG@5=0.5377, and primary=0.6045 (+0.00285 primary over the
> published reference of 0.6016).

> Audit note: The independent process and implementation audit is recorded in
> [`baseline-protocol-audit.md`](baseline-protocol-audit.md). Because the archived runner log ends
> with a structured `ERROR` despite an exit code of 0, and several trajectory
> paths need correction, these headline numbers should currently be treated as
> provisional public-validation results.

## 1. What this baseline measures

The measured system is one direct `gemini-3.7-flash` agent operating in Goal mode (`/goal`).
The baseline deliberately excludes the multi-agent mechanisms of Research Agent:

- no META layer or audit;
- no Scientist layer or episodic resets;
- no delegation, subagents, or peer agents;
- no Research Agent control-plane invocation;
- no access to hidden-test data or parent workspaces.

The KuaiRand recommendation task provides the benchmark environment to observe
autonomous agent optimization behaviors.

## 2. Headline result

| Metric | `gemini-3.7-flash` Goal best single seed (Seed 3) | `gemini-3.7-flash` Goal 5-Seed Ensemble | Published validation reference | Best single Delta |
| --- | ---: | ---: | ---: | ---: |
| GAUC | 0.6712 | 0.6708 | 0.6674 | +0.0038 |
| nDCG@5 | 0.5377 | 0.5376 | 0.5357 | +0.0020 |
| Primary = mean(GAUC, nDCG@5) | 0.6045 | 0.6042 | 0.6016 | +0.0029 |

Direct comparison with reproduced baseline controls:

| Comparison | GAUC | nDCG@5 | Primary |
| --- | ---: | ---: | ---: |
| Item popularity control | 0.6387 | 0.5227 | 0.5807 |
| Reproduced pointwise FM | 0.6674 | 0.5357 | 0.6015 |
| `gemini-3.7-flash` Best DeepFM (Seed 3) | 0.6712 | 0.5377 | 0.6045 |
| Best minus pointwise FM | +0.0038 | +0.0020 | +0.0030 |

## 3. Run identity and experimental boundary

| Field | Recorded value |
| --- | --- |
| Benchmark ID | `gemini-3.7-flash-goal-2026-08-30-v1` |
| Run ID | 470dd2789a16446eb023ff1bff15e112 |
| Archived target project | `competition_archive/kuairand-pure/research-worlds/direct-gemini-3.7-flash-goal-baseline` |
| Run mode | Autonomous `gemini-3.7-flash` Goal mode (/goal) |
| Measured runner | One direct `gemini-3.7-flash` agent |
| Model | gemini-3.7-flash |
| Reasoning effort | high |
| Runner CLI | 1.1.22 |
| Starting point | clean public-validation baseline |
| Permissions mode | accept-edits (--dangerously-skip-permissions) |
| Hidden-test data | Not used |
| Subagents / delegation | Not used |
| Research Agent invocation | Not used |
| Wall-clock budget | 60 minutes |
| Actual execution time | 3,209.96 s (53m 30s) |

The launch used direct Goal mode with edits enabled, public validation only,
and a 60-minute wall-clock budget.

## 4. Time and token ledger

The run completed on 2026-08-30 from 08:01:34 UTC to 08:55:08 UTC.

| Quantity | Tokens / Value | Interpretation |
| --- | ---: | --- |
| Total elapsed time | 3,209.96 s (53m 30s) | Autonomous end-to-end run |
| Non-cache input tokens | 1,286,768 | Direct prompt and trajectory context |
| Cache-read tokens | 9,779,617 | Context caching across tool cycles |
| Output tokens | 74,779 | Generated model plans and source code |
| Reasoning / Thinking tokens | 21,116 | Internal chain-of-thought tokens |
| Total tokens (excluding cache) | 1,361,547 | Official reported session total |

## 5. Complete experiment trajectory

The `gemini-3.7-flash` agent explored 8 distinct research directions in sequence:

| Phase | Description | Architecture / Config | GAUC | nDCG@5 | Primary | Delta vs 0.6016 |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Baseline verification | Item Popularity Baseline | 0.6387 | 0.5227 | 0.5807 | -0.0209 |
| 1 | Baseline verification | Official Pointwise FM (5 fields, k=16) | 0.6674 | 0.5357 | 0.6015 | -0.0001 |
| 2 | Feature engineering | Full dataset extraction (37 cat + 14 dense) | — | — | — | Data pipeline |
| 3 | Feature selection | High-signal compact subset (8 fields) | — | — | — | Reduced dimensionality |
| 4 | FM grid search | k=16, lr=1e-3, L2=1e-5 | 0.6695 | 0.5369 | 0.6032 | +0.0016 |
| 4 | FM grid search | k=32, lr=5e-4, L2=1e-5 | 0.6674 | 0.5360 | 0.6017 | +0.0001 |
| 4 | FM grid search | k=64, lr=8e-4, L2=1e-5 | 0.6663 | 0.5354 | 0.6008 | -0.0008 |
| 5 | Regularization search | Fine-grained L2=3e-5 (Seed 0) | 0.6694 | 0.5372 | 0.6033 | +0.0017 |
| 5 | Statistical fusion | Prior & User Affinity Blend (w=0.05..0.50) | 0.6695 | 0.5366 | 0.6030 | +0.0014 |
| 5 | Multi-seed FM | 5-Seed Ensemble FM | 0.6692 | 0.5367 | 0.6029 | +0.0013 |
| 6 | Pairwise BPR loss | BCE + Pairwise BPR (pair_w=0.1) | 0.6681 | 0.5358 | 0.6019 | +0.0003 |
| 6 | Pairwise BPR loss | BCE + Pairwise BPR (pair_w=0.5) | 0.6685 | 0.5355 | 0.6020 | +0.0004 |
| 6 | Pairwise BPR loss | Ranking focused (bce_w=0.5, pair_w=1.0) | 0.6684 | 0.5358 | 0.6021 | +0.0005 |
| 7 | Compact DeepFM | DeepFM (k=16, MLP [64], dropout=0.2) | 0.6704 | 0.5376 | **0.6040** | +0.0024 |
| 7 | Compact DeepFM | DeepFM (k=16, MLP [128, 64], drop=0.2) | 0.6692 | 0.5369 | 0.6030 | +0.0014 |
| 7 | Compact DeepFM | DeepFM (k=24, MLP [128, 64], drop=0.3) | 0.6705 | 0.5373 | **0.6039** | +0.0023 |
| 8 | Multi-Task DeepFM | MT-DeepFM + EMA (Single Seed) | 0.6702 | 0.5373 | 0.6037 | +0.0021 |
| 8 | Multi-Task DeepFM | MT-DeepFM + EMA (Seed 1) | 0.6704 | 0.5374 | 0.6039 | +0.0023 |
| 8 | Multi-Task DeepFM | MT-DeepFM + EMA (Seed 2) | 0.6705 | 0.5372 | 0.6039 | +0.0023 |
| 8 | Multi-Task DeepFM | MT-DeepFM + EMA (Seed 3) | **0.6712** | **0.5377** | **0.6045** | **+0.0029** |
| 8 | Multi-Task DeepFM | MT-DeepFM + EMA (Seed 4) | 0.6705 | 0.5374 | 0.6040 | +0.0024 |
| 8 | Multi-Task DeepFM | **5-Seed Ensemble MT-DeepFM** | **0.6708** | **0.5376** | **0.6042** | **+0.0026** |

## 6. Analysis and scientific interpretation

### 6.1 Feature selection outperformed raw feature expansion

When expanding to all 37 categorical fields and 14 dense statistics, vocabulary explosion and noise slowed convergence. The agent designed a targeted 8-field high-signal representation (`user_id`, `video_id`, `author_id`, `tab`, `dur_bucket`, `video_type`, `upload_type`, `tag`), which constrained vocabulary dimensions while capturing content category and interaction modalities.

### 6.2 Deep non-linear interactions boosted ranking beyond standard FM

Unlike pure FM which only models 2nd-order factorized interactions, adding a compact MLP tower (MLP [64] or [128, 64]) with LayerNorm and Dropout (0.2~0.3) on top of the 8 high-signal embeddings increased primary from 0.6033 (best FM) to 0.6040 (Compact DeepFM).

### 6.3 Multi-task auxiliary supervision provided effective regularization

Incorporating click prediction as an auxiliary binary classification objective alongside long-view prediction, paired with Exponential Moving Average (EMA) parameter smoothing, yielded the best public-validation checkpoint in this run: individual seeds reached 0.6045 primary and the 5-seed ensemble reached 0.6042. This is not independent generalization confirmation.

## 7. Comparative summary: Codex Goal vs `gemini-3.7-flash` Goal

The following short-run Codex/`gemini-3.7-flash` comparison is retained as historical context;
it is not the three-hour `gpt-5.6-luna` control used in the current headline comparison.
Both runs demonstrated strong autonomous optimization behavior within a ~50–60
minute window:

| Dimension | Earlier Codex Goal Baseline | Direct `gemini-3.7-flash` Goal Baseline |
| :--- | :--- | :--- |
| **Model** | `gpt-5.6-luna` | `gemini-3.7-flash` |
| **Primary Mechanism** | Sampled within-user pairwise BPR FM (factors=8, lr=0.00025) | Multi-Task Compact DeepFM + 8 High-Signal Fields + Click Aux + EMA |
| **Best Single Primary** | **0.60445** (GAUC 0.6712, nDCG 0.5377) | **0.60447 / 0.6045** (GAUC 0.6712, nDCG 0.5377) |
| **Ensemble Primary** | N/A (single model frontier) | **0.6042** (5-Seed MT-DeepFM) |
| **Elapsed Time** | 50m 45s (interactive goal) | 53m 30s |
| **Total Tokens** | ~275K (excl. cache) / 11.2M (incl. cache) | 1.36M (excl. cache) / 11.1M (incl. cache) |
| **Core Strategy** | Deep tuning of ranking objective & sampling density | Architecture exploration (DeepFM, auxiliary tasks, EMA, ensembling) |

Both baselines arrived at nearly identical top-tier public-validation primary scores (~0.6045), confirming that long-horizon single-agent optimizers are strong controls that must be measured against multi-agent research architectures under identical budgets and evaluation boundaries.
