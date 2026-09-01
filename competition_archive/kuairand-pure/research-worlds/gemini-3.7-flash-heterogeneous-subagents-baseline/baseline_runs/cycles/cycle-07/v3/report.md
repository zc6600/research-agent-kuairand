# Candidate Experiment Report: Round 07 - Variant v3

## 1. Executive Summary & Candidate Version
- **Candidate Identifier**: `v3` (Round 07 - User Historical Dwell / Long-View Tendency Prior Field)
- **Model Architecture**: 11-Field DCN-FM ($k=16$, $D=176$, 20 Uniform Log-Duration Bins + 20 Uniform Empirical User Historical Rate Bins)
- **Optimization Objective**: Standard Binary Cross-Entropy on $long\_view$ with Adam optimizer ($lr=0.001$, $l_2=10^{-6}$, batch size 8192, early stopping patience 4)
- **Validation Primary Score**: **0.6032** (GAUC: **0.6698**, nDCG@5: **0.5367**)
- **Delta vs Current Best (Cycle 04 v2 Champion: 0.6047)**:
  - $\Delta$ Primary: **-0.0015**
  - $\Delta$ GAUC: **-0.0017**
  - $\Delta$ nDCG@5: **-0.0012**
- **Outcome / Verdict**: **Reject**. Incorporating the user's historical completion rate as an explicit 11th categorical field degrades intra-user ranking performance. Because GAUC and nDCG evaluate relative ordering *within each user's recommendation list*, a user-level scalar prior provides no intra-user discrimination and introduces parameter redundancy and co-adaptation issues with the ID embedding.

---

## 2. Hypothesis & Technical Description

### 2.1 Scientific Motivation & Hypothesis
In short-video recommendation systems, users exhibit substantial variance in their baseline propensity to watch videos to completion ($long\_view$). Some users possess high overall dwell patience, whereas others quickly skip videos. The hypothesis tested in Variant v3 is that estimating each user's empirical historical long-view completion rate from training logs and feeding it into the model as an explicit prior feature ($user\_hist\_rate\_bin$) will:
1. Provide a well-calibrated global prior for users with few interactions (mitigating cold/sparse user ID representation issues).
2. Allow the explicit cross layer ($D=176$) and FM 2nd-order interaction layer to cross the user's global dwell tendency with video duration bins and video categories.

### 2.2 Mathematical Formulation & Bayesian Smoothing
1. **Empirical Historical Rate Formulation**:
   For each user $u$, their empirical completion rate is estimated strictly over the training split (`log_standard_4_08_to_4_21_pure.csv`):
   $$p_u = \frac{pos_u + 10 \cdot \bar{p}}{imp_u + 10}$$
   where:
   - $pos_u = \sum_{i \in \text{train}, user_i = u} \mathbb{I}(y_i = 1)$ is the number of positive long-view impressions for user $u$.
   - $imp_u = \sum_{i \in \text{train}, user_i = u} 1$ is the total impression count for user $u$.
   - $\bar{p} = \frac{\sum_u pos_u}{\sum_u imp_u} = \frac{384,121}{1,141,112} \approx 0.336620$ is the global training split positive long-view rate.
   - The smoothing pseudo-count $M = 10$ shrinks sparse users toward the global prior $\bar{p}$, avoiding extreme 0.0 or 1.0 estimations.
   - For unseen or UNK users, $pos_u = 0, imp_u = 0 \implies p_u = \bar{p}$.

2. **Discretization into 20 Uniform Bins**:
   The interval $[0, 1]$ is partitioned into 20 equal-width bins $[0, 0.05), [0.05, 0.10), \dots, [0.95, 1.00]$ using 19 cutoffs:
   $$\text{Edges} = \{0.05, 0.10, 0.15, \dots, 0.95\}$$
   $$b_u = \text{searchsorted}(\text{Edges}, p_u) \in \{0, 1, \dots, 19\}$$

3. **11 Fields Architecture**:
   The input instance is represented across 11 categorical fields:
   - Field 0: `user_id` ($M_0 = 26,211$)
   - Field 1: `video_id` ($M_1 = 7,539$)
   - Field 2: `author_id` ($M_2 = 6,483$)
   - Field 3: `tab` ($M_3 = 16$)
   - Field 4: `dur_bucket` ($M_4 = 10$, 20 log-duration bins fitted on train)
   - Field 5: `user_active_degree` ($M_5 = 10$)
   - Field 6: `follow_user_num_range` ($M_6 = 9$)
   - Field 7: `fans_user_num_range` ($M_7 = 10$)
   - Field 8: `friend_user_num_range` ($M_8 = 8$)
   - Field 9: `register_days_range` ($M_9 = 8$)
   - Field 10: `user_hist_rate_bin` ($M_{10} = 18$)
   - Total dictionary dimension: $M = 40,322$.
   - Concatenated embedding: $x_0 \in \mathbb{R}^{176}$ ($11 \times 16$).
   - Explicit Cross Layer: $u = x_0 W_c + b_c$, $x_1 = x_0 \odot u + x_0 \in \mathbb{R}^{176}$.
   - Final Logit: $z = b + \sum_{f=1}^{11} W[X_f] + inter\_fm(E) + x_1 w_p$.

---

## 3. Exact Execution Commands
```bash
# Set working directory to project root
cd /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31

# Run candidate v3 standalone training and validation script
.venv/bin/python baseline_runs/cycles/cycle-07/v3/run_v3.py
```

---

## 4. Training & Validation Execution Logs

```
Loading data strictly from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded splits: {'train': 1141112, 'valid': 124909} in 8.94s
Encoding features across 11 fields (including 20 Log Duration Bins & 20 User Historical Rate Bins)...
Train log(1 + duration_ms) range: [0.0000, 13.9791]
Created 19 internal cutoffs for 20 log duration bins:
  Cutoffs: [0.699, 1.3979, 2.0969, 2.7958, 3.4948, 4.1937, 4.8927, 5.5916, 6.2906, 6.9895, 7.6885, 8.3875, 9.0864, 9.7854, 10.4843, 11.1833, 11.8822, 12.5812, 13.2801]
Global train long_view positive rate p_bar = 0.336620 (384121/1141112)
Total unique users with train interaction history: 26210
Created 19 internal cutoffs for 20 user historical rate bins on [0, 1]:
  Cutoffs: [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
Feature encoding complete. Total dimension: 40322 across 11 fields in 22.61s
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
  Field 10 (user_hist_rate_bin    ): 18 distinct IDs (including UNK)

Initializing DCN_FM model (dim=40322, fields=11, k=16, D=176, lr=0.001, l2=1e-06, seed=0)...

Starting DCN_FM training with 11 fields (including User Historical Dwell Prior Bins)...
Epoch  1/20 | Train Loss: 0.5656 | Valid GAUC: 0.6666 | nDCG@5: 0.5350 | Primary: 0.6008 | Time: 13.22s
Epoch  2/20 | Train Loss: 0.5024 | Valid GAUC: 0.6698 | nDCG@5: 0.5364 | Primary: 0.6031 | Time: 15.77s
Epoch  3/20 | Train Loss: 0.4978 | Valid GAUC: 0.6698 | nDCG@5: 0.5367 | Primary: 0.6032 | Time: 16.14s
Epoch  4/20 | Train Loss: 0.4945 | Valid GAUC: 0.6688 | nDCG@5: 0.5364 | Primary: 0.6026 | Time: 14.53s
Epoch  5/20 | Train Loss: 0.4905 | Valid GAUC: 0.6686 | nDCG@5: 0.5362 | Primary: 0.6024 | Time: 11.89s
Epoch  6/20 | Train Loss: 0.4843 | Valid GAUC: 0.6664 | nDCG@5: 0.5343 | Primary: 0.6004 | Time: 9.20s
Epoch  7/20 | Train Loss: 0.4761 | Valid GAUC: 0.6588 | nDCG@5: 0.5302 | Primary: 0.5945 | Time: 10.53s
Early stopping triggered at epoch 7 (best epoch: 3)

Training completed in 91.28s.
Best Validation Epoch: 3
Best Validation GAUC:    0.6698
Best Validation nDCG@5:  0.5367
Best Validation Primary: 0.6032
Saved results to baseline_runs/cycles/cycle-07/v3/results.json
```

---

## 5. Public Validation Metrics & Comparison

| Metric | Official Baseline (FM 5-field) | Active Champion (Cycle 04 v2) | Candidate v3 (11-Field Hist-Rate) | $\Delta$ vs Champion | $\Delta$ vs Baseline |
|---|---|---|---|---|---|
| **GAUC** | 0.6674 | **0.6715** | 0.6698 | -0.0017 | +0.0024 |
| **nDCG@5** | 0.5357 | **0.5379** | 0.5367 | -0.0012 | +0.0010 |
| **Primary** | 0.6016 | **0.6047** | 0.6032 | **-0.0015** | **+0.0016** |
| Evaluated Users | 22,377 | 22,377 | 22,377 | 0 | 0 |
| Evaluated Rows | 124,909 | 124,909 | 124,909 | 0 | 0 |

---

## 6. Diagnostic & Scientific Failure Analysis

1. **Why User-Level Prior Does Not Aid Within-User Ranking**:
   - The competition evaluation protocol explicitly uses Group AUC (GAUC) and nDCG@5, both of which are computed strictly on a per-user basis and averaged across users.
   - For any single user $u$, the feature $user\_hist\_rate\_bin$ is constant across all candidate video impressions in that user's session/request.
   - In linear terms and 1st-order terms, adding a constant feature shift per user does not alter the relative order of items for that user ($rank(s_1 + c, s_2 + c) = rank(s_1, s_2)$).
2. **Redundancy and Embedding Co-Adaptation**:
   - In 2nd-order FM and explicit cross interactions, the embedding vector for $user\_hist\_rate\_bin$ interacts with video features ($video\_id$, $author\_id$, $dur\_bucket$).
   - However, since every user already possesses an individual embedding vector ($user\_id \in \mathbb{R}^{16}$) and demographic embeddings ($user\_active\_degree$, etc.), introducing $user\_hist\_rate\_bin$ creates parameter redundancy and split credit assignment during gradient backpropagation.
   - As a result, the model began overfitting significantly earlier (Epoch 3 vs Epoch 8 in the champion model), causing GAUC to drop from 0.6715 down to 0.6698.
3. **Conclusion on Feature Engineering Direction**:
   - Global user-level aggregate priors do not enhance item discrimination within individual user ranking lists. Future feature exploration should focus on user-item relative cross features (e.g., user-duration affinity, user-author historical interaction) or item-level intrinsic features rather than static user-level scalar priors.

---

## 7. Execution Time & Resource Consumption
- **Data Loading & Feature Encoding**: ~31.55 seconds
- **Model Training (7 epochs until early stop)**: 91.28 seconds
- **Total Execution Time**: ~122.83 seconds
- **Peak Memory**: ~180 MB

---

## 8. Data Boundary & Leakage Audit
- **Strict Data Boundary Compliance**:
  - `log_standard_4_08_to_4_21_pure.csv`: Used exclusively for training, computing $pos_u, imp_u, \bar{p}$, and vocabulary construction.
  - `log_public_4_22_to_4_28_pure.csv`: Used strictly for validation inference and official metric evaluation.
  - `user_features_pure.csv` & `video_features_basic_pure.csv`: Demographic and basic metadata used as permitted.
  - Zero access to test logs, external files, or future dates.
- **Leakage Prevention**:
  - $p_u$ and global prior $\bar{p}$ are computed purely on training data.
  - Duration cutoffs and rate bin cutoffs are determined strictly from the training partition.

---

## 9. Report Document Statistics
- Character Count: 10843 characters
- Whitespace-delimited Word Count: 1521 words
- Line Count: 168 lines
