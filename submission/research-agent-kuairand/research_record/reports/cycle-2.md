# Cycle 2 Scientist Report

## Overview and Objectives

Entering Cycle 2, the initial 15-field Factorization Machine implementation was materialized under `system/**` (primary score 0.6016310, tying the official validation baseline of 0.6016). The consecutive Full non-improving streak stood at 2 of 3.

The goal of this cycle was to break the 0.6016 plateau and achieve a statistically and practically significant improvement on the valid public validation primary metric (`mean(GAUC, nDCG@5)`).

## Hypotheses and Experimental Trajectory

### Hypothesis 1: Demographic & Behavioral User-Profile Expansion
In Cycle 1, the FM model only utilized 5 user profile ranges and 10 video/context fields (15 fields total), completely omitting the 18 user demographic and preference one-hot fields (`onehot_feat0` through `onehot_feat17`) as well as user activity flags (`is_lowactive_period`, `is_live_streamer`, `is_video_author`) and video aspect ratios.

I hypothesized that incorporating all 18 one-hot user profile features along with user activity indicators and video presentation aspect ratios into an expanded 38-field FM (`rich_all`) would provide the model with critical user preference signals and improve within-user ranking without creating parameter explosion.

**Medium Screening Evidence:**
- On the deterministic 25% complete-user Medium partition (5,590 users / 31,536 rows):
  - 15-field baseline FM (Cycle 1): peak Medium primary 0.6024866 (epoch 3).
  - 38-field `rich_all` FM (seed 0, k=16, lr=0.001, l2=1e-5): peak Medium primary **0.6037128** (epoch 8), with Medium GAUC jumping from 0.6694859 to **0.6720485** and nDCG@5 at 0.5353771.
- Explicit combinatorial crosses (`rich_cross`, adding `user_tab`, `author_tab`, `tag_tab`, `hour_weekday`, `active_dur`): expanded dimension to 91,511 and degraded Medium primary to 0.5996391 due to extreme feature sparsity.
- Including high-cardinality `music_id` (7,202 sparse IDs, 39 fields, dim 49,749): peak Medium primary was 0.6025280, underperforming the 38-field `rich_all` model.

### Hypothesis 2: Model Architecture & Inductive Bias Exploration
I explored alternative ranking architectures:
1. **Tree-based GBDT (CatBoost)** (`system/catboost_ranker.py`): Trained with native categorical target statistics on all features. Best iteration was 189, achieving Medium GAUC 0.6611881, nDCG@5 0.5315237, primary 0.5963559. Decision trees without dense latent embedding dot products struggled to model the high-cardinality interaction matrix between 27,285 users and 7,583 items.
2. **DeepFM & Multi-Task DeepFM** (`system/deep_ranker.py`, `system/neural_ranker.py`): Implemented 3-layer deep MLP trunks with GELU/LayerNorm, auxiliary completion-rate and click BCE supervision, and sampled pairwise BPR loss. While DeepFM achieved 0.6016–0.6018 at epoch 1–2, the high parameter count in the deep layers caused rapid overfitting on subsequent epochs compared to low-rank regularized FM.
3. **Embedding Dimension Ablation**: On `rich_all`, rank $k=16$ (Medium primary 0.6037128 at epoch 8) outperformed $k=32$ (Medium primary 0.6016157 at epoch 3).

### Hypothesis 3: Multi-Seed Logit Ensembling
Because FM models with random Gaussian initialization $V \sim \mathcal{N}(0, 0.01)$ and SGD batch ordering converge to diverse local optima in the 42,588-dimensional embedding space, I hypothesized that ensembling predicted logits across multiple seeds (with per-seed early stopping on the Medium partition) would smooth ranking variance and systematically elevate top-$k$ ranking metrics (nDCG@5 and GAUC).

**Medium Screening Evidence:**
- Individual seed Medium primary scores:
  - Seed 0: GAUC 0.67205, nDCG@5 0.53538, primary 0.60371
  - Seed 1: GAUC 0.66848, nDCG@5 0.53607, primary 0.60228
  - Seed 2: GAUC 0.66855, nDCG@5 0.53551, primary 0.60203
  - Seed 3: GAUC 0.67026, nDCG@5 0.53567, primary 0.60297
  - Seed 4: GAUC 0.66999, nDCG@5 0.53494, primary 0.60246
- 5-Seed Ensemble on Medium: GAUC **0.6709463**, nDCG@5 **0.5367206**, primary **0.6038334**.
  Ensembling pushed nDCG@5 past every individual seed score.

## Full Validation Results

Given the strong, consistent gains observed on the Medium screening rung, I executed Full evaluations on the entire public validation set (124,909 rows / 22,377 users) using the unchanged organizer evaluator (`starter_kit/evaluate.py`).

### 1. Single-Seed 38-Field Rich FM (Seed 0)
- Command: `uv run --with numpy python system/fast_fm.py --preset rich_all --k 16 --lr 0.001 --seed 0 --full --output system/evidence/cycle2-fm-rich38-seed0-full.json`
- **Validation GAUC**: **0.6694661**
- **Validation nDCG@5**: **0.5367117**
- **Validation Primary**: **0.6030889**
- **Deltas vs Official Baseline** (0.6674 / 0.5357 / 0.6016):
  - GAUC: +0.0020661
  - nDCG@5: +0.0010117
  - Primary: +0.0014889

### 2. 5-Seed 38-Field Rich FM Ensemble (Seeds 0, 1, 2, 3, 4)
- Command: `uv run --with numpy python system/ensemble_fm.py --seeds 0 1 2 3 4 --k 16 --lr 0.001 --l2 1e-5 --full --output system/evidence/cycle2-fm-rich38-ensemble5-full.json`
- **Validation GAUC**: **0.6704182**
- **Validation nDCG@5**: **0.5377619**
- **Validation Primary**: **0.6040901**
- **Deltas vs Official Published Baseline** (0.6674 / 0.5357 / 0.6016):
  - GAUC: **+0.0030182**
  - nDCG@5: **+0.0020619**
  - Primary: **+0.0024901**
- **Delta vs the initial 15-field implementation** (0.6016310):
  - Primary: **+0.0024591** (> task $\epsilon = 0.002$ convergence threshold).

## Summary of Retained Implementation

The coherent, state-bearing implementation retained under `system/**` is:
1. `system/ensemble_fm.py`: The 5-seed 38-field FM ensemble orchestrator that achieves the new benchmark-best primary score of **0.6040901**.
2. `system/fast_fm.py`: The fast NumPy-accelerated 38-field FM model implementation with early stopping and configurable field presets.
3. `system/evidence/cycle2-fm-rich38-ensemble5-full.json`: Full validation evidence for the 5-seed ensemble.
4. `system/evidence/cycle2-fm-rich38-seed0-full.json`: Full validation evidence for the single-seed baseline.
5. `system/README.md`: Updated execution and reproduction guide.

All experiments strictly respected the data boundaries (using only `competition_data/data/` development files with zero access to hidden-test data) and finished well within the 15-minute runtime constraint (~7.2s/epoch, total 5-seed run ~430s). Shared research memories `EXPLORE.md` and `ENGINEERING.md` have been updated with all newly established operational and empirical facts.
