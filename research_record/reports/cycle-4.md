# Scientist Report — Cycle 4

## Overview and Objectives

Entering Cycle 4, the eight-seed 38-field Factorization Machine ensemble was materialized under `system/**` (public validation GAUC 0.6712176, nDCG@5 0.5376403, primary 0.6044289). The non-improving streak stood at 1 of 3 (task $\epsilon = 0.002$).

The objective of Cycle 4 was to explore new representation, behavioral profile, and architectural dimensions to significantly advance the valid public-validation primary metric (`mean(GAUC, nDCG@5)`).

---

## Hypotheses and Experimental Trajectory

### Hypothesis 1: Leak-Free Historical User Preference & Affinity Profiling
In KuaiRand-Pure, 98.11% of public validation users (21,955 of 22,377 users) are present in the historical training period (`20220408..20220421`). While Cycle 1 showed that sparse direct target rate encoding for specific user-item pairs failed, I hypothesized that aggregate user preference profiling (user's most watched tag, most frequent recommendation tab, historical activity/long-view rate bucket, and interaction volume bucket) paired with explicit real-time candidate matches (`match_tag`, `match_tab`) would provide the Factorization Machine with rich, dense behavioral signals without leakage.

### Hypothesis 2: Secondary Content Categories & Video Age Freshness
In `video_features_basic_pure.csv`, 1,791 videos (23.6%) contain multiple comma-separated tags; earlier cycles discarded secondary tags by splitting on comma and taking only the primary tag. I hypothesized that extracting secondary tags (`tag2`) and computing video freshness age (`date - upload_dt` in days) would recover critical item categorization and temporal freshness signals.

### Hypothesis 3: Loss Function Exploration (Pointwise BCE vs Pairwise BPR)
Because GAUC and nDCG@5 evaluate within-user candidate ranking, I tested whether a pairwise BPR ranking loss or hybrid BCE+BPR loss would improve ranking compared to pointwise logistic loss.

### Hypothesis 4: Field-weighted Factorization Machines (FwFM)
In standard FM, all pairs of fields interact with uniform weight 1.0. I hypothesized that Field-weighted FM (learning a symmetric matrix $R \in \mathbb{R}^{m \times m}$ of field-pair interaction modulations) would allow the model to upweight high-signal crosses (user demographic $\times$ video metadata) while dampening noisy pairs.

---

## Screening Evidence on Deterministic Medium Partition

All diagnostic configurations were screened on the deterministic 25% complete-user Medium partition (5,590 users / 31,536 validation rows):

1. **Baseline 38-Field FM (Seed 0)**:
   - Peak Medium primary: **0.60371** (GAUC 0.67205, nDCG@5 0.53538) at epoch 8.
2. **Enhanced 46-Field FM (Seed 0)** (+8 user preference/match & video metadata fields, dim 42,705):
   - Peak Medium primary: **0.60404** (GAUC 0.67135, nDCG@5 **0.53672**) at epoch 5.
   - nDCG@5 increased by **+0.00134** on a single seed.
3. **Enhanced 46-Field FwFM (Seed 0)**:
   - Peak Medium primary: **0.60414** (GAUC 0.67149, nDCG@5 **0.53679**) at epoch 6.
4. **Hybrid BCE + BPR Ranking Loss**:
   - $\alpha=0.2$: Peak Medium primary **0.60221** (epoch 4).
   - $\alpha=0.5$: Peak Medium primary **0.59966** (epoch 4).
   - *Finding*: Unconstrained random negative sampling across historical sessions destroyed session/context conditioning, underperforming pointwise BCE.
5. **Over-expanded 54-Field Representation** (adding redundant sparse historical item/author statistics):
   - Peak Medium primary: **0.60286** (epoch 3).
   - *Finding*: Adding sparse item/author statistics diluted gradients on the high-signal user demographic/preference embeddings. The 46-field representation proved to be the optimal sweet spot.

---

## Full Validation Results

Given the strong performance of the 46-field representation on the Medium partition, Full evaluations were executed on all 124,909 public validation rows (22,377 users) using the organizer's unchanged evaluator (`starter_kit/evaluate.py`).

### 1. 8-Seed 46-Field FM Ensemble (`system/ensemble_46.py`)
- **Command**:
  ```bash
  uv run --with numpy python system/ensemble_46.py \
    --seeds 0 1 2 3 4 5 6 7 --k 16 --lr 0.001 --l2 1e-5 --full \
    --output system/evidence/cycle4-fm-rich46-ensemble8-full.json
  ```
- **Runtime**: 764.74 seconds (within the 15-minute limit).
- **Public Validation Metrics**:
  - **GAUC**: **0.6728421**
  - **nDCG@5**: **0.5390304**
  - **Primary Score**: **0.6059363**
- **Deltas vs Official Published Baseline** (GAUC 0.6674 / nDCG@5 0.5357 / primary 0.6016):
  - GAUC: **+0.0054421**
  - nDCG@5: **+0.0033304**
  - Primary: **+0.0043363**
- **Deltas vs the eight-seed 38-field ensemble** (GAUC 0.6712176 / nDCG@5 0.5376403 / primary 0.6044289):
  - GAUC: **+0.0016245**
  - nDCG@5: **+0.0013901**
  - Primary: **+0.0015074**

### 2. 4-Seed 46-Field FwFM Ensemble (`system/fast_fwfm_ensemble.py`)
- **Command**:
  ```bash
  uv run --with numpy python system/fast_fwfm_ensemble.py \
    --seeds 0 1 2 3 --k 16 --lr 0.001 --l2 1e-5 --full \
    --output system/evidence/cycle4-fwfm-rich46-ensemble4-full.json
  ```
- **Public Validation Metrics**:
  - **GAUC**: **0.6724305**
  - **nDCG@5**: **0.5385388**
  - **Primary Score**: **0.6054846**

---

## Comparison Across Research States

| Model / State | GAUC | nDCG@5 | Primary | $\Delta$ vs Baseline |
|---|---:|---:|---:|---:|
| Official Baseline | 0.6674000 | 0.5357000 | 0.6016000 | +0.0000000 |
| Initial 15-field FM | 0.6671070 | 0.5361550 | 0.6016310 | +0.0000310 |
| Five-seed 38-field FM | 0.6704182 | 0.5377619 | 0.6040901 | +0.0024901 |
| Eight-seed 38-field FM | 0.6712176 | 0.5376403 | 0.6044289 | +0.0028289 |
| **Cycle 4 46-field 8-seed FM Ensemble** | **0.6728421** | **0.5390304** | **0.6059363** | **+0.0043363** |

---

## Summary of Retained Implementation

The state-bearing implementation retained under `system/**` includes:
1. `system/ensemble_46.py`: The 8-seed 46-field FM ensemble implementation achieving the new benchmark-best primary score of **0.6059363**.
2. `system/fast_fwfm_ensemble.py`: The 46-field Field-weighted Factorization Machine ensemble.
3. `system/evidence/cycle4-fm-rich46-ensemble8-full.json`: Exact Full evaluation evidence for the 8-seed 46-field FM ensemble.
4. `system/evidence/cycle4-fwfm-rich46-ensemble4-full.json`: Exact Full evaluation evidence for the 4-seed 46-field FwFM ensemble.
5. `system/README.md`: Updated execution, reproduction, and model registry guide.

Shared research memories (`EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, `KNOWLEDGE.md`) have been updated with all newly established empirical and operational findings. All experiments used strictly curated `competition_data/data/` files with zero hidden-test data access.
