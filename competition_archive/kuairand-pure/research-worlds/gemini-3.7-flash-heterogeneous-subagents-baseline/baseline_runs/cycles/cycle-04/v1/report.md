# Experiment Report: Round 04 - Variant v1

## 1. Candidate Overview
- **Variant**: `v1`
- **Focus / Hypothesis**: Fine-Grained 30-Quantile Duration Bucketing in DCN-FM
- **Technical Description**:
  Variant v1 investigates whether increasing the granularity of continuous video duration discretization from 10 quantiles to 30 quantiles improves representation learning and ranking accuracy in the DCN-FM architecture.
  In previous cycles (01-03), `duration_ms` was discretized into 10 quantile bins using 9 interior cut points. In Variant v1:
  - 29 quantile cut points are calculated strictly on the training partition: $q_i = \text{Quantile}(D_{\text{train}}, \frac{i}{30})$ for $i \in \{1, \dots, 29\}$.
  - Video durations are mapped into 30 distinct buckets ($0 \dots 29$).
  - The model retains the full DCN-FM architecture with 10 fields, embedding dimension $k=16$, 1-layer explicit cross network ($D=160$), second-order FM interactions, and linear terms:
    $$x_0 = \text{vec}(E) \in \mathbb{R}^{160}$$
    $$x_1 = x_0 \odot (x_0 W_c + b_c) + x_0 \in \mathbb{R}^{160}$$
    $$z = b + \sum_{f=1}^{10} W[X_f] + \frac{1}{2}\sum_{j=1}^{16}\left[\left(\sum_{f=1}^{10} v_{f,j}\right)^2 - \sum_{f=1}^{10} v_{f,j}^2\right] + x_1 w_p$$
- **Model Architecture**: Hybrid DCN 1-Layer Cross + Factorization Machine (DCN-FM) optimized with Adam.
- **Feature Set (10 Fields)**:
  1. `user_id` (26,211 distinct IDs)
  2. `video_id` (7,539 distinct IDs)
  3. `author_id` (6,483 distinct IDs)
  4. `tab` (16 distinct IDs)
  5. `dur_bucket` (31 distinct IDs: 30 quantile buckets fitted on train + 1 UNK)
  6. `user_active_degree` (10 distinct IDs)
  7. `follow_user_num_range` (9 distinct IDs)
  8. `fans_user_num_range` (10 distinct IDs)
  9. `friend_user_num_range` (8 distinct IDs)
  10. `register_days_range` (8 distinct IDs)
  - **Total One-Hot Dimensionality**: 40,325 (vs 40,305 in 10-bucket baseline)

---

## 2. Experimental Setup & Execution
- **Command Line**:
  ```bash
  .venv/bin/python baseline_runs/cycles/cycle-04/v1/run_v1.py
  ```
- **Hyperparameters**:
  - Duration quantiles: 30
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
| 1 | 0.5872 | 0.6627 | 0.5334 | 0.5980 | 5.08s |
| 2 | 0.5078 | 0.6681 | 0.5358 | 0.6020 | 5.10s |
| 3 | 0.5002 | 0.6702 | 0.5372 | 0.6037 | 5.02s |
| 4 | 0.4974 | 0.6707 | 0.5373 | 0.6040 | 4.99s |
| **5 (Best)** | **0.4946** | **0.6707** | **0.5374** | **0.6041** | **5.03s** |
| 6 | 0.4907 | 0.6691 | 0.5366 | 0.6028 | 4.96s |
| 7 | 0.4860 | 0.6669 | 0.5351 | 0.6010 | 4.88s |
| 8 | 0.4816 | 0.6611 | 0.5324 | 0.5967 | 4.20s |
| 9 | 0.4779 | 0.6577 | 0.5304 | 0.5940 | 4.04s |

*Early stopping triggered at Epoch 9 after 4 consecutive non-improving epochs past Epoch 5.*

---

## 4. Public Validation Metrics & Comparison

### Comparison vs Current Best Baseline (Cycle 03 v3 Champion - DCN-FM 10-Bucket)
| Metric | Cycle 03 v3 Champion (10-Quantile Buckets) | Cycle 04 v1 (30-Quantile Buckets) | Delta ($\Delta$) | Status |
|:---|:---:|:---:|:---:|:---:|
| **Primary Score** | **0.6041** (0.604118) | **0.6041** (0.604070) | **-0.00005** | **Tied** |
| **GAUC** | **0.6705** (0.670535) | **0.6707** (0.670695) | **+0.0002** | **Slight Gain** |
| **nDCG@5** | **0.5377** (0.537701) | **0.5374** (0.537446) | **-0.0003** | **Slight Drop** |
| Best Epoch | 5 | 5 | 0 | Identical Convergence |
| Total Dim | 40,305 | 40,325 | +20 | Minimal Overhead |

---

## 5. Execution Time & System Performance
- **Data Ingestion**: 3.05s
- **Feature Preprocessing & Encoding**: 6.01s
- **Training Time (9 epochs)**: 43.31s (~4.81s / epoch)
- **Total Wall-Clock Time**: 52.37s

---

## 6. Findings & Technical Insights
1. **Impact on GAUC**: 30-quantile duration discretization provides finer resolution into short vs medium vs long video lengths, leading to a small improvement in pairwise discrimination across all user impressions (GAUC increased from 0.6705 to 0.6707).
2. **Impact on Top-5 Ranking**: The finer partitioning slightly disperses gradient signals across more duration embeddings, causing a minor dip in nDCG@5 from 0.5377 to 0.5374.
3. **Overall Assessment**: 30-quantile bucketing matches the champion Primary Score of 0.6041 while slightly shifting the metric balance toward GAUC. The additional 20 embedding parameters add zero measurable computational overhead.

---

## 7. Data Boundary & Leakage Audit
- **Strict KuaiRand-Pure Boundary**: Fully verified.
- **Allowed Data Files Used**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Train: 1,141,112 rows)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Valid: 124,909 rows)
  - `competition_data/data/user_features_pure.csv` (User side features)
  - `competition_data/data/video_features_basic_pure.csv` (Video author mappings)
- **Leakage Prevention**:
  - All 29 quantile cut points for duration binning were computed strictly on the training partition (`log_standard_4_08_to_4_21_pure.csv`).
  - Feature vocabularies and offsets were constructed exclusively from training split data.
  - Public validation logs (`log_public_4_22_to_4_28_pure.csv`) were strictly used for out-of-time evaluation via `starter_kit/evaluate.py`.
  - Zero out-of-boundary access, zero data leakage.

---

## 8. Report Statistics
- **Character Count**: 5,792
- **Whitespace-delimited Word Count**: 831
- **Line Count**: 114
