# Round 07 Candidate Variant v1 Report: Empirical Smoothed Item Popularity Prior Field (11-Field DCN-FM)

## 1. Candidate Overview & Hypothesis

- **Candidate Version**: `v1`
- **Cycle**: `cycle-07`
- **Model Architecture**: 11-Field Explicit Cross Layer + Factorization Machine (DCN-FM, $D = 11 \times 16 = 176$)
- **Core Hypothesis**:
  In short-video recommendation, item-level historical engagement reflects intrinsic content attractiveness and broad user appeal. By computing an empirical Bayesian-smoothed long-view probability $p_v = \frac{\text{pos}_v + 20 \cdot \bar{p}}{\text{imp}_v + 20}$ strictly from the standard training split, discretizing $p_v$ into 20 uniform bins on $[0, 1]$, and injecting it as an explicit 11th categorical field (`item_pop_bin`), the model can learn higher-order interactions between item popularity priors and user demographics (activity degree, registration tenure, social graph size) alongside log-duration features, potentially improving within-user ranking calibration.

---

## 2. Technical Formulation & Implementation Details

### 2.1 Feature Field Composition (11 Fields)
1. `user_id`: Categorical user identifier (26,211 vocabulary slots).
2. `video_id`: Categorical item identifier (7,539 vocabulary slots).
3. `author_id`: Categorical content creator identifier (6,483 vocabulary slots).
4. `tab`: Interaction interface context (16 slots).
5. `dur_bucket`: Log-transformed video duration $\ln(1 + \text{duration\_ms})$ partitioned into 20 uniform bins fitted on training set (10 occupied slots).
6. `user_active_degree`: User activity level category (10 slots).
7. `follow_user_num_range`: User following count range (9 slots).
8. `fans_user_num_range`: User follower count range (10 slots).
9. `friend_user_num_range`: User mutual friend count range (8 slots).
10. `register_days_range`: User account tenure range (8 slots).
11. `item_pop_bin`: Discretized empirical smoothed item long-view prior $p_v \in [0, 1]$ into 20 uniform bins (16 occupied slots).

### 2.2 Empirical Popularity Prior Formulation
- Total training impressions: $N_{\text{train}} = 1,141,112$.
- Total training positive long-view instances: $P_{\text{train}} = 384,121$.
- Global prior mean: $\bar{p} = \frac{384,121}{1,141,112} \approx 0.336620$.
- For video $v$ with $\text{imp}_v$ training impressions and $\text{pos}_v$ positive long-views:
  $$p_v = \frac{\text{pos}_v + 20 \cdot \bar{p}}{\text{imp}_v + 20}$$
- For cold/unseen items in validation split: $p_v = \bar{p}$.
- Discretization: 19 internal cutoff thresholds at $[0.05, 0.10, \dots, 0.95]$ partitioning $[0, 1]$ into 20 uniform intervals via `searchsorted`.

### 2.3 Model Architecture & Optimization
- **Embedding Dimension**: $k = 16$ per field.
- **Concatenated Representation**: $x_0 = [e_1, e_2, \dots, e_{11}] \in \mathbb{R}^{176}$.
- **DCN 1st Cross Layer**: $x_1 = x_0 \odot (x_0 W_c + b_c) + x_0$, with $W_c \in \mathbb{R}^{176 \times 176}, b_c \in \mathbb{R}^{176}$.
- **Cross Output Projection**: $z_{\text{cross}} = x_1 w_p$, with $w_p \in \mathbb{R}^{176}$.
- **FM 2nd-Order Interaction**: $z_{\text{FM}} = \frac{1}{2} \sum_{f=1}^{k} \left[ \left( \sum_{i=1}^{11} e_{i, f} \right)^2 - \sum_{i=1}^{11} e_{i, f}^2 \right]$.
- **Linear & Bias**: $z_{\text{lin}} = b + \sum_{i=1}^{11} w_i$.
- **Final Logit**: $z = z_{\text{lin}} + z_{\text{FM}} + z_{\text{cross}}$.
- **Hyperparameters**: $\text{lr} = 0.001$, Adam optimizer ($\beta_1=0.9, \beta_2=0.999$), $L_2 = 1\times 10^{-6}$, batch size $= 8192$, max epochs $= 20$, early stopping patience $= 4$.

---

## 3. Exact Commands Executed

```bash
cd /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31
.venv/bin/python baseline_runs/cycles/cycle-07/v1/run_v1.py
```

---

## 4. Training & Validation Execution Logs

```text
Loading data from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded splits: {'train': 1141112, 'valid': 124909} in 8.92s
Encoding features across 11 fields (including 20 Log Duration Bins and 20 Item Popularity Bins)...
Train log(1 + duration_ms) range: [0.0000, 13.9791]
Created 19 internal cutoffs for 20 log duration bins:
  Cutoffs: [0.699, 1.3979, 2.0969, 2.7958, 3.4948, 4.1937, 4.8927, 5.5916, 6.2906, 6.9895, 7.6885, 8.3875, 9.0864, 9.7854, 10.4843, 11.1833, 11.8822, 12.5812, 13.2801]
Train split statistics: Total Imp=1141112, Total Pos=384121, Global Mean p_bar=0.336620
Distinct videos in train: 7538
Created 19 internal cutoffs for 20 item popularity prior bins on [0, 1]:
  Cutoffs: [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
Feature encoding complete. Total dimension: 40320 across 11 fields in 22.87s
  Field  0 (user_id               ): 26211 distinct IDs (including UNK)
  Field  1 (video_id              ): 7539 distinct IDs (including UNK)
  Field  2 (author_id             ): 6483 distinct IDs (including UNK)
  Field  3 (tab                   ): 16 distinct IDs (including UNK)
  Field  4 (dur_bucket            ): 10 distinct IDs (including UNK)
  Field  5 (user_active_degree    ): 10 distinct IDs (including UNK)
  Field  6 (follow_user_num_range ): 9 distinct IDs (including UNK)
  Field  7 (fans_user_num_range   ): 10 distinct IDs (including UNK)
  Field  8 (friend_user_num_range ): 8 distinct IDs (including UNK)
  Field  9 (register_days_range   ): 8 distinct IDs (including UNK)
  Field 10 (item_pop_bin          ): 16 distinct IDs (including UNK)

Initializing DCN_FM model (dim=40320, fields=11, k=16, D=176, lr=0.001, l2=1e-06, seed=0)...

Starting DCN_FM training with 11 Fields (including Item Popularity Prior Field)...
Epoch  1/20 | Train Loss: 0.5804 | Valid GAUC: 0.6628 | nDCG@5: 0.5336 | Primary: 0.5982 | Time: 13.08s
Epoch  2/20 | Train Loss: 0.5075 | Valid GAUC: 0.6686 | nDCG@5: 0.5360 | Primary: 0.6023 | Time: 15.72s
Epoch  3/20 | Train Loss: 0.5001 | Valid GAUC: 0.6694 | nDCG@5: 0.5368 | Primary: 0.6031 | Time: 15.80s
Epoch  4/20 | Train Loss: 0.4968 | Valid GAUC: 0.6693 | nDCG@5: 0.5368 | Primary: 0.6031 | Time: 14.60s
Epoch  5/20 | Train Loss: 0.4929 | Valid GAUC: 0.6701 | nDCG@5: 0.5373 | Primary: 0.6037 | Time: 11.90s
Epoch  6/20 | Train Loss: 0.4878 | Valid GAUC: 0.6657 | nDCG@5: 0.5347 | Primary: 0.6002 | Time: 9.37s
Epoch  7/20 | Train Loss: 0.4834 | Valid GAUC: 0.6637 | nDCG@5: 0.5338 | Primary: 0.5987 | Time: 10.71s
Epoch  8/20 | Train Loss: 0.4795 | Valid GAUC: 0.6600 | nDCG@5: 0.5320 | Primary: 0.5960 | Time: 8.45s
Epoch  9/20 | Train Loss: 0.4757 | Valid GAUC: 0.6547 | nDCG@5: 0.5295 | Primary: 0.5921 | Time: 7.71s
Early stopping triggered at epoch 9 (best epoch: 5)

Training completed in 107.33s.
Best Validation Epoch: 5
Best Validation GAUC:    0.6701
Best Validation nDCG@5:  0.5373
Best Validation Primary: 0.6037
```

---

## 5. Public Validation Metrics & Comparison

| Metric | Cycle 04 v2 Champion (10-Field Log-Dur DCN-FM) | Cycle 07 v1 (11-Field Item Pop Prior DCN-FM) | Delta ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **GAUC** | **0.6715** | 0.6701 | -0.0014 |
| **nDCG@5** | **0.5379** | 0.5373 | -0.0006 |
| **Primary (Mean)** | **0.6047** | 0.6037 | -0.0010 |
| **Best Epoch** | 5 | 5 | 0 |

### In-Depth Findings:
1. **Performance Analysis**: Introducing the empirical smoothed item popularity prior field (`item_pop_bin`) achieved a strong primary score of 0.6037 (GAUC 0.6701, nDCG@5 0.5373), which remains competitive but marginally trails the 10-field champion by -0.0010.
2. **Redundancy & Over-smoothing**: The item embedding (`video_id`) already memorizes historical item-level long-view rates during gradient descent. Adding a discrete 20-bin item prior introduces a 176-dimensional embedding cross-space where the model spends capacity interacting with a coarse 20-bin histogram of what `video_id` already captures with higher resolution.
3. **Generalization**: The model reached its peak performance at epoch 5 and began overfitting earlier in epochs 6-9 as train loss decreased from 0.4929 down to 0.4757 while validation metrics deteriorated.

---

## 6. Elapsed Time & Resource Profiling

- **Data Loading Time**: 8.92s
- **Feature Extraction & Prior Calculation**: 22.87s
- **Model Training & Evaluation Time**: 107.33s (9 epochs with early stopping)
- **Total Pipeline Wall Time**: 139.12s (~2.3 minutes)

---

## 7. Data Boundary & Leakage Audit

- [x] **Strict File Inventory Adherence**: Only the 5 authorized files were accessed:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv`
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv`
  - `competition_data/data/video_features_basic_pure.csv`
  - `competition_data/data/user_features_pure.csv`
- [x] **Strict Temporal Boundary**:
  - Global average $\bar{p}$, item counts $\text{imp}_v$, positive counts $\text{pos}_v$, duration min/max cutoffs, and categorical vocabularies were computed exclusively on standard training dates (`2022-04-08` to `2022-04-21`).
  - Validation log (`2022-04-22` to `2022-04-28`) was strictly evaluated without contributing to any feature statistics or vocabulary indices.
- [x] **Evaluation Integrity**: Evaluated using the official `starter_kit/evaluate.py` semantics with exact user-level GAUC and nDCG@5 calculation.

---

## 8. Report Statistics Verification

- **Report Path**: `baseline_runs/cycles/cycle-07/v1/report.md`
- **Line Count**: 151
- **Word Count**: 1282
- **Character Count**: 9570
