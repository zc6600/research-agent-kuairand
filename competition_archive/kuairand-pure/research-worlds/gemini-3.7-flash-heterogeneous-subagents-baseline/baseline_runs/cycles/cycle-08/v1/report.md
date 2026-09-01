# Round 08 Candidate Variant v1 Report: Causal Last-Interacted Author Feature (11-Field DCN-FM)

## 1. Candidate Overview & Hypothesis

- **Candidate Version**: `v1`
- **Cycle**: `cycle-08`
- **Model Architecture**: 11-Field Explicit Cross Layer + Factorization Machine (DCN-FM, $D = 11 \times 16 = 176$)
- **Core Hypothesis**:
  In short-video recommendation, users frequently develop short-term content creator or topical affinity during an active browsing session. By tracking each user's most recently interacted author (`last_author_id`) strictly in causal chronological order, the model can capture dynamic sequential context. Incorporating `last_author_id` as the 11th categorical embedding field into the champion Log-Duration DCN-FM allows 2nd-order FM and explicit DCN cross layers to learn creator-continuity interactions (e.g. cross interactions between current item `author_id` and previous `last_author_id`), potentially enhancing within-user ranking calibration.

---

## 2. Technical Formulation & Implementation Details

### 2.1 Feature Field Composition (11 Fields)
1. `user_id`: Categorical user identifier (26,211 vocabulary slots).
2. `video_id`: Categorical item identifier (7,539 vocabulary slots).
3. `author_id`: Categorical content creator identifier (6,483 vocabulary slots).
4. `tab`: Interaction interface context (16 slots).
5. `dur_bucket`: Log-transformed video duration $\\ln(1 + \\text{duration\\_ms})$ partitioned into 20 uniform bins fitted on training set (10 occupied slots).
6. `user_active_degree`: User activity level category (10 slots).
7. `follow_user_num_range`: User following count range (9 slots).
8. `fans_user_num_range`: User follower count range (10 slots).
9. `friend_user_num_range`: User mutual friend count range (8 slots).
10. `register_days_range`: User account tenure range (8 slots).
11. `last_author_id`: Causal previous interacted `author_id` strictly prior to the current timestamp (6,482 vocabulary slots, initialized to `UNK` on each user's first observed interaction).

### 2.2 Causal Sequential State Construction
- All interaction rows from `log_standard_4_08_to_4_21_pure.csv` ($N_{\\text{train}} = 1,141,112$) and `log_public_4_22_to_4_28_pure.csv` ($N_{\\text{valid}} = 124,909$) were indexed and sorted globally by exact millisecond timestamp `time_ms` (with deterministic tie-breakers preserving original file ordering).
- A running dictionary `user_last_author[user_id]` was maintained during the forward temporal pass:
  - For interaction $t$, feature `last_author_id` is read from `user_last_author.get(user_id, 'UNK')`.
  - The state is subsequently updated with the current candidate's `author_id`: `user_last_author[user_id] = current_author`.
- Resulting statistics:
  - Training UNK count: 26,210 (2.30% of training interactions, corresponding to the very first interaction of each user).
  - Validation UNK count: 422 (0.34% of validation interactions, corresponding to users with no prior training activity).
- Field vocabularies and embedding offsets were constructed strictly from the training split.

### 2.3 Model Architecture & Optimization
- **Embedding Dimension**: $k = 16$ per field.
- **Concatenated Representation**: $x_0 = [e_1, e_2, \\dots, e_{11}] \in \\mathbb{R}^{176}$.
- **DCN 1st Cross Layer**: $x_1 = x_0 \\odot (x_0 W_c + b_c) + x_0$, with $W_c \in \\mathbb{R}^{176 \times 176}, b_c \in \\mathbb{R}^{176}$.
- **Cross Output Projection**: $z_{\\text{cross}} = x_1 w_p$, with $w_p \in \\mathbb{R}^{176}$.
- **FM 2nd-Order Interaction**: $z_{\\text{FM}} = \\frac{1}{2} \\sum_{f=1}^{k} \\left[ \\left( \\sum_{i=1}^{11} e_{i, f} \\right)^2 - \\sum_{i=1}^{11} e_{i, f}^2 \\right]$.
- **Linear & Bias**: $z_{\\text{lin}} = b + \\sum_{i=1}^{11} w_i$.
- **Final Logit**: $z = z_{\\text{lin}} + z_{\\text{FM}} + z_{\\text{cross}}$.
- **Hyperparameters**: $\\text{lr} = 0.001$, Adam optimizer ($\\beta_1=0.9, \\beta_2=0.999$), $L_2 = 1\\times 10^{-6}$, batch size $= 8192$, max epochs $= 20$, early stopping patience $= 4$.

---

## 3. Exact Commands Executed

```bash
cd /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31
.venv/bin/python baseline_runs/cycles/cycle-08/v1/run_v1.py
```

---

## 4. Training & Validation Execution Logs

```text
Loading data from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Read 1141112 train rows and 124909 valid rows.
Causal last_author assigned. UNK in train: 26210 (2.30%), UNK in valid: 422 (0.34%)
Loaded splits: {train: 1141112, valid: 124909} in 25.94s
Encoding features across 11 fields (including 20 Logarithmic Duration Bins and Causal Last-Interacted Author)...
Train log(1 + duration_ms) range: [0.0000, 13.9791]
Created 19 internal cutoffs for 20 log duration bins:
  Cutoffs: [0.699, 1.3979, 2.0969, 2.7958, 3.4948, 4.1937, 4.8927, 5.5916, 6.2906, 6.9895, 7.6885, 8.3875, 9.0864, 9.7854, 10.4843, 11.1833, 11.8822, 12.5812, 13.2801]
Feature encoding complete. Total dimension: 46786 across 11 fields in 14.00s
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
  Field 10 (last_author_id        ): 6482 distinct IDs (including UNK)

Initializing DCN_FM model (dim=46786, fields=11, k=16, D=176, lr=0.001, l2=1e-06, seed=0)...

Starting DCN_FM training with Causal Last-Interacted Author Feature (11 fields)...
Epoch  1/20 | Train Loss: 0.5862 | Valid GAUC: 0.6603 | nDCG@5: 0.5328 | Primary: 0.5965 | Time: 11.09s
Epoch  2/20 | Train Loss: 0.5067 | Valid GAUC: 0.6666 | nDCG@5: 0.5357 | Primary: 0.6011 | Time: 8.08s
Epoch  3/20 | Train Loss: 0.4979 | Valid GAUC: 0.6671 | nDCG@5: 0.5362 | Primary: 0.6017 | Time: 7.93s
Epoch  4/20 | Train Loss: 0.4935 | Valid GAUC: 0.6674 | nDCG@5: 0.5363 | Primary: 0.6019 | Time: 7.82s
Epoch  5/20 | Train Loss: 0.4878 | Valid GAUC: 0.6663 | nDCG@5: 0.5358 | Primary: 0.6011 | Time: 6.07s
Epoch  6/20 | Train Loss: 0.4796 | Valid GAUC: 0.6589 | nDCG@5: 0.5318 | Primary: 0.5953 | Time: 6.07s
Epoch  7/20 | Train Loss: 0.4704 | Valid GAUC: 0.6519 | nDCG@5: 0.5288 | Primary: 0.5903 | Time: 5.08s
Epoch  8/20 | Train Loss: 0.4616 | Valid GAUC: 0.6457 | nDCG@5: 0.5261 | Primary: 0.5859 | Time: 6.05s
Early stopping triggered at epoch 8 (best epoch: 4)

Training completed in 58.19s.
Best Validation Epoch: 4
Best Validation GAUC:    0.6674
Best Validation nDCG@5:  0.5363
Best Validation Primary: 0.6019
```

---

## 5. Public Validation Metrics & Comparison

| Metric | Cycle 04 v2 Champion (10-Field Log-Dur DCN-FM) | Cycle 08 v1 (11-Field Causal Last-Author DCN-FM) | Delta ($\\Delta$) |
| :--- | :---: | :---: | :---: |
| **GAUC** | **0.6715** | 0.6674 | -0.0041 |
| **nDCG@5** | **0.5379** | 0.5363 | -0.0016 |
| **Primary (Mean)** | **0.6047** | 0.6019 | -0.0028 |
| **Best Epoch** | 5 | 4 | -1 |

### In-Depth Findings:
1. **Performance Analysis**: Introducing the causal last-interacted author feature (`last_author_id`) as an 11th categorical embedding field resulted in a primary validation score of 0.6019 (GAUC: 0.6674, nDCG@5: 0.5363), falling short of the 10-field champion by -0.0028.
2. **Sparsity & Over-parameterization in Sequential Creator Space**: The `last_author_id` field adds 6,482 sparse category slots. Because user-author interaction matrices in feed recommendations are highly sparse (most users rarely encounter the same author twice in immediate succession), the model allocates substantial capacity ($D = 176 \times 176$ cross layer matrix) fitting high-variance author transitions.
3. **Overfitting Dynamics**: The model peaked early at epoch 4 (train loss 0.4935) and rapidly overfitted on subsequent epochs (by epoch 8, train loss dropped sharply to 0.4616 while validation primary dropped to 0.5859), indicating that point-in-time single author states suffer from high variance without dense aggregation or pooling.

---

## 6. Elapsed Time & Resource Profiling

- **Data Loading & Causal Stream Sorting**: 25.94s
- **Feature Extraction & Vocabulary Encoding**: 14.00s
- **Model Training & Evaluation Time**: 58.19s (8 epochs with early stopping)
- **Total Pipeline Wall Time**: 98.13s (~1.6 minutes)

---

## 7. Data Boundary & Leakage Audit

- [x] **Strict File Inventory Adherence**: Only the authorized files were accessed:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv`
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv`
  - `competition_data/data/video_features_basic_pure.csv`
  - `competition_data/data/user_features_pure.csv`
- [x] **Strict Temporal Boundary & Causal Integrity**:
  - `last_author_id` is strictly causal: for any interaction at timestamp $t$, only interactions with timestamps $< t$ determine the running state. No future labels, future items, or backward leakage occurred.
  - Duration bin edges and categorical vocabularies were computed exclusively on the standard training split (`2022-04-08` to `2022-04-21`). Unseen valid author IDs are mapped to `UNK`.
- [x] **Evaluation Integrity**: Evaluated using the official `starter_kit/evaluate.py` semantics with exact user-level GAUC and nDCG@5 calculation.

---

## 8. Report Statistics Verification

- **Report Path**: `baseline_runs/cycles/cycle-08/v1/report.md`
- **Line Count**: 149
- **Word Count**: 1318
- **Character Count**: 10011
