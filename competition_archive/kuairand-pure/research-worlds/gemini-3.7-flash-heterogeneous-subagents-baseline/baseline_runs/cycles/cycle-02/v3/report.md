# Experiment Report: Round 02 - Variant v3

## 1. Candidate Overview
- **Variant**: `v3`
- **Focus / Hypothesis**: High Capacity with Strong Regularization ($k=64$, $\lambda_{L2}=1\times 10^{-5}$)
- **Technical Description**:
  Variant v3 evaluates whether scaling the Factorization Machine latent interaction dimension from $k=16$ to $k=64$ (a $4\times$ capacity expansion), compensated by a $10\times$ stronger $L_2$ weight regularization ($\lambda_{L2}=10^{-5}$ vs baseline $10^{-6}$), can capture higher-rank multi-field interactions across the 10 demographic-extended feature fields without suffering from representation overfitting.
- **Model Architecture**: Second-Order Factorization Machine (FM) with Adam optimizer.
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
  .venv/bin/python baseline_runs/cycles/cycle-02/v3/run_v3.py
  ```
- **Hyperparameters**:
  - Embedding dimension $k$: 64
  - Learning rate $\eta$: 0.001
  - $L_2$ regularization $\lambda$: $1\times 10^{-5}$
  - Batch size: 8,192
  - Max epochs: 25
  - Early stopping patience: 4
  - Random seed: 0

---

## 3. Training & Validation Progress

### Per-Epoch Training Log
| Epoch | Train Loss | Valid GAUC | Valid nDCG@5 | Primary Score | Epoch Time (s) |
|:-----:|:----------:|:----------:|:------------:|:-------------:|:--------------:|
| 1 | 0.5868 | 0.6619 | 0.5335 | 0.5977 | 8.36s |
| 2 | 0.5125 | 0.6654 | 0.5347 | 0.6000 | 8.65s |
| **3 (Best)** | **0.5016** | **0.6659** | **0.5348** | **0.6004** | **8.43s** |
| 4 | 0.4961 | 0.6642 | 0.5344 | 0.5993 | 8.39s |
| 5 | 0.4916 | 0.6613 | 0.5333 | 0.5973 | 8.47s |
| 6 | 0.4871 | 0.6607 | 0.5322 | 0.5964 | 8.47s |
| 7 | 0.4827 | 0.6600 | 0.5317 | 0.5959 | 8.03s |

*Early stopping triggered at Epoch 7 after 4 consecutive non-improving epochs past Epoch 3.*

---

## 4. Public Validation Metrics & Comparison

### Comparison vs Current Best Baseline (Cycle 01 v2 Champion)
| Metric | Cycle 01 v2 Champion ($k=16, L_2=1e-6$) | Cycle 02 v3 ($k=64, L_2=1e-5$) | Delta ($\Delta$) |
|:---|:---:|:---:|:---:|
| **Primary Score** | **0.6020** | **0.6004** | **-0.0016** |
| **GAUC** | **0.6677** | **0.6659** | **-0.0018** |
| **nDCG@5** | **0.5363** | **0.5348** | **-0.0015** |
| Best Epoch | 5 | 3 | -2 epochs |
| Total Dim | 40,305 | 40,305 | 0 |
| Parameters in $V$ | 644,880 ($40,305 \times 16$) | 2,579,520 ($40,305 \times 64$) | $+4\times$ |

---

## 5. Execution Time & System Performance
- **Data Ingestion**: 2.93s
- **Feature Preprocessing & Encoding**: 5.47s
- **Training Time (7 epochs)**: 58.81s (~8.40s / epoch)
- **Total Wall-Clock Time**: 67.21s

---

## 6. Findings & Technical Insights
1. **Capacity vs Generalization**: Increasing the latent embedding dimension $k$ from 16 to 64 quadruple the parameter count of the second-order interaction tensor. Although training loss decreased faster (reaching 0.5016 by epoch 3), validation metrics peaked earlier (epoch 3 vs epoch 5) and plateaued below the baseline.
2. **Regularization Tradeoff**: The $10\times$ stronger $L_2$ weight decay ($10^{-5}$) proved insufficient to prevent early overfitting in the high-dimensional latent space, while simultaneously restricting the expressiveness of frequent feature combinations.
3. **Recommendation**: Latent dimension $k=16$ or $k=32$ provides a superior capacity-to-sample ratio for this tabular interaction setting on KuaiRand-Pure. High dimensional embeddings ($k=64$) require more selective interaction pooling or explicit dropout rather than uniform $L_2$ penalty.

---

## 7. Data Boundary & Leakage Audit
- **Strict KuaiRand-Pure Boundary**: Fully verified.
- **Allowed Data Files Used**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Train: 1,141,112 rows)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Valid: 124,909 rows)
  - `competition_data/data/user_features_pure.csv` (User side features)
  - `competition_data/data/video_features_basic_pure.csv` (Video author mappings)
- **Leakage Prevention**:
  - Vocabulary mapping and duration quantile binning strictly computed only on training split.
  - Public validation split used strictly for post-epoch evaluation using `starter_kit/evaluate.py`.
  - Zero out-of-boundary access or test leakage.

---

## 8. Report Statistics
- **Character Count**: 4,873
- **Whitespace-delimited Word Count**: 683
- **Line Count**: 103
