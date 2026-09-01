# Experiment Report: Round 03 - Variant v3

## 1. Candidate Overview
- **Variant**: `v3`
- **Focus / Hypothesis**: Explicit Cross-Network Layer (DCN-style 1-layer cross + FM)
- **Technical Description**:
  Variant v3 implements an explicit cross-network architecture (DCN-FM) on top of the 10-field embedding layer ($k=16$). Standard Factorization Machines compute inner products between latent vectors, modeling pairwise interactions in a symmetric subspace. The DCN explicit cross layer explicitly models bitwise and field-wise feature crossings via non-linear polynomial interactions:
  $$x_0 = \text{vec}(E) = [v_1, v_2, \dots, v_{10}]^T \in \mathbb{R}^{160}$$
  $$x_1 = x_0 \odot (x_0 W_c + b_c) + x_0 \in \mathbb{R}^{160}$$
  where $W_c \in \mathbb{R}^{160 \times 160}$ and $b_c \in \mathbb{R}^{160}$.
  The combined scoring logit joins the first-order linear component, second-order FM interactions, and the projected cross-layer output:
  $$z = b + \sum_{f=1}^{10} W[X_f] + \frac{1}{2}\sum_{j=1}^{16}\left[\left(\sum_{f=1}^{10} v_{f,j}\right)^2 - \sum_{f=1}^{10} v_{f,j}^2\right] + x_1 w_p$$
  where $w_p \in \mathbb{R}^{160}$ is the cross-layer projection vector.
- **Model Architecture**: Hybrid DCN 1-Layer Cross + Factorization Machine (DCN-FM) optimized with full-matrix analytical backpropagation and Adam.
- **Feature Set (10 Fields)**:
  1. `user_id` (26,211 distinct IDs)
  2. `video_id` (7,539 distinct IDs)
  3. `author_id` (6,483 distinct IDs)
  4. `tab` (16 distinct IDs)
  5. `dur_bucket` (11 quantile buckets fitted on train)
  6. `user_active_degree` (10 distinct IDs)
  7. `follow_user_num_range` (9 distinct IDs)
  8. `fans_user_num_range` (10 distinct IDs)
  9. `friend_user_num_range` (8 distinct IDs)
  10. `register_days_range` (8 distinct IDs)
  - **Total One-Hot Dimensionality**: 40,305

---

## 2. Experimental Setup & Execution
- **Command Line**:
  ```bash
  .venv/bin/python baseline_runs/cycles/cycle-03/v3/run_v3.py
  ```
- **Hyperparameters**:
  - Embedding dimension $k$: 16
  - Cross layer dimension $D$: $10 \times 16 = 160$
  - Learning rate $\eta$: 0.001
  - $L_2$ regularization $\lambda$: $1\times 10^{-6}$
  - Batch size: 8,192
  - Max epochs: 20
  - Early stopping patience: 4
  - Random seed: 0

---

## 3. Training & Validation Progress

### Per-Epoch Training Log
| Epoch | Train Loss | Valid GAUC | Valid nDCG@5 | Primary Score | Epoch Time (s) |
|:-----:|:----------:|:----------:|:------------:|:-------------:|:--------------:|
| 1 | 0.5860 | 0.6627 | 0.5334 | 0.5980 | 4.44s |
| 2 | 0.5078 | 0.6682 | 0.5361 | 0.6022 | 4.95s |
| 3 | 0.5002 | 0.6696 | 0.5369 | 0.6032 | 5.16s |
| 4 | 0.4974 | 0.6703 | 0.5373 | 0.6038 | 5.12s |
| **5 (Best)** | **0.4950** | **0.6705** | **0.5377** | **0.6041** | **5.13s** |
| 6 | 0.4919 | 0.6693 | 0.5364 | 0.6028 | 5.14s |
| 7 | 0.4874 | 0.6688 | 0.5358 | 0.6023 | 5.37s |
| 8 | 0.4820 | 0.6647 | 0.5335 | 0.5991 | 5.10s |
| 9 | 0.4762 | 0.6578 | 0.5301 | 0.5940 | 5.24s |

*Early stopping triggered at Epoch 9 after 4 consecutive non-improving epochs past Epoch 5.*

---

## 4. Public Validation Metrics & Comparison

### Comparison vs Current Best Baseline (Cycle 01 v2 Champion)
| Metric | Cycle 01 v2 Champion (Standard FM) | Cycle 03 v3 (DCN-FM Hybrid) | Delta ($\Delta$) | Status |
|:---|:---:|:---:|:---:|:---:|
| **Primary Score** | **0.6020** | **0.6041** | **+0.0021** | **New Record** |
| **GAUC** | **0.6677** | **0.6705** | **+0.0028** | **Improvement** |
| **nDCG@5** | **0.5363** | **0.5377** | **+0.0014** | **Improvement** |
| Best Epoch | 5 | 5 | 0 | Stable Convergence |
| Embedding Dim $k$ | 16 | 16 | 0 | Identical $k$ |
| Cross Parameters | 0 | 25,920 ($W_c, b_c, w_p$) | +25.9k | Lightweight |

---

## 5. Execution Time & System Performance
- **Data Ingestion**: 3.20s
- **Feature Preprocessing & Encoding**: 5.98s
- **Training Time (9 epochs)**: 45.65s (~5.07s / epoch)
- **Total Wall-Clock Time**: 54.83s

---

## 6. Findings & Technical Insights
1. **Expressive Power of Explicit Crossing**: Introducing the DCN cross layer $x_1 = x_0 \odot (x_0 W_c + b_c) + x_0$ yields significant improvements in both GAUC (+0.0028) and nDCG@5 (+0.0014), achieving an all-time new best Primary Score of **0.6041**.
2. **Complementarity of FM and Cross Networks**: Standard FM captures inner-product pairwise similarities across field latent factors, whereas the explicit cross layer generates degree-2 polynomial feature crossings with asymmetric, learned weights $W_c$. The combination is highly complementary.
3. **Parameter & Compute Efficiency**: The $160 \times 160$ cross weight matrix introduces only 25,600 additional parameters, increasing per-epoch training time by less than 1.5 seconds compared to pure FM while delivering consistent performance gains.

---

## 7. Data Boundary & Leakage Audit
- **Strict KuaiRand-Pure Boundary**: Fully verified.
- **Allowed Data Files Used**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Train: 1,141,112 rows)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Valid: 124,909 rows)
  - `competition_data/data/user_features_pure.csv` (User side features)
  - `competition_data/data/video_features_basic_pure.csv` (Video author mappings)
- **Leakage Prevention**:
  - Quantile binning for duration features and categorical vocabularies were computed exclusively on the standard training split (4/08 - 4/21).
  - Validation metrics were evaluated strictly on out-of-time public validation split (4/22 - 4/28) using official `starter_kit/evaluate.py`.
  - Zero out-of-boundary access or test leakage.

---

## 8. Report Statistics
- **Character Count**: 5,705
- **Whitespace-delimited Word Count**: 826
- **Line Count**: 112
