# Round 05 Candidate Report: Variant v2 (Day-of-Week + Hour-of-Day Dual Context in Log-Duration DCN-FM)

## 1. Candidate Version & Metadata
- **Candidate Identifier**: `cycle-05/v2`
- **Model Family**: Log-Duration DCN-FM (12 Categorical & Discretized Fields with Explicit 1-Layer Cross + Factorization Machine)
- **Field Count**: 12 fields
- **Embedding Dimension per Field ($k$)**: 16
- **Concatenated Feature Vector Dimension ($D$)**: $12 \times 16 = 192$
- **Total Model Dimension (Vocabularies + UNK across 12 fields)**: 40,337
- **Target Metric**: `primary` = $\frac{1}{2} (\text{GAUC} + \text{nDCG@5})$ on `long_view` label

---

## 2. Hypothesis & Technical Description

### Hypothesis
User engagement behavior (such as `long_view`) exhibits diurnal and weekly periodicity; users consume content differently during morning commutes, evening leisure hours, and weekend vs. weekday sessions. By incorporating both Day-of-Week (`dow` $\in [0, 6]$) derived from the interaction `date` and Hour-of-Day (`hour` $\in [0, 23]$) derived from `hourmin`, the model can capture temporal preference shifts and time-conditioned video/author affinities through both 2nd-order FM inner products and high-order explicit feature crosses ($D=192$).

### Technical Architecture & Field Specification
The model comprises 12 distinct categorical fields:
1. `user_id` (26,211 distinct tokens including UNK)
2. `video_id` (7,539 distinct tokens including UNK)
3. `author_id` (6,483 distinct tokens including UNK)
4. `tab` (16 distinct tokens including UNK)
5. `dur_bucket` (10 distinct active tokens out of 20 uniform bins in $\ln(1 + \text{duration\_ms})$ space fitted on train split)
6. `user_active_degree` (10 distinct tokens including UNK)
7. `follow_user_num_range` (9 distinct tokens including UNK)
8. `fans_user_num_range` (10 distinct tokens including UNK)
9. `friend_user_num_range` (8 distinct tokens including UNK)
10. `register_days_range` (8 distinct tokens including UNK)
11. `dow` (8 distinct tokens: 7 days $[0, 6]$ + UNK)
12. `hour` (25 distinct tokens: 24 hours $[0, 23]$ + UNK)

The forward formulation:
$$\mathbf{x}_0 = \text{concat}(\mathbf{v}_1, \dots, \mathbf{v}_{12}) \in \mathbb{R}^{192}$$
$$\mathbf{u} = \mathbf{x}_0 \mathbf{W}_c + \mathbf{b}_c \in \mathbb{R}^{192}, \quad \mathbf{x}_1 = \mathbf{x}_0 \odot \mathbf{u} + \mathbf{x}_0 \in \mathbb{R}^{192}$$
$$z = b + \sum_{i=1}^{12} w_i(x_i) + \frac{1}{2} \left[ \left(\sum_{i=1}^{12} \mathbf{v}_i\right)^2 - \sum_{i=1}^{12} \mathbf{v}_i^2 \right] + \mathbf{x}_1^\top \mathbf{w}_p$$

Hyperparameters:
- Learning rate $\eta = 0.001$, Adam optimizer ($\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$)
- Weight decay $L_2 = 10^{-6}$
- Batch size $B = 8192$
- Max epochs: 20, Early stopping patience: 4 epochs on public validation primary score
- Random seed: 0

---

## 3. Exact Command Line Executed

```bash
.venv/bin/python baseline_runs/cycles/cycle-05/v2/run_v2.py
```

---

## 4. Training & Validation Execution Logs

```
Loading data from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded splits: {'train': 1141112, 'valid': 124909} in 3.17s
Encoding features across 12 fields with 20 Logarithmic Duration Bins and DOW + Hour Context...
Train log(1 + duration_ms) range: [0.0000, 13.9791]
Created 19 internal cutoffs for 20 log duration bins:
  Cutoffs: [0.699, 1.3979, 2.0969, 2.7958, 3.4948, 4.1937, 4.8927, 5.5916, 6.2906, 6.9895, 7.6885, 8.3875, 9.0864, 9.7854, 10.4843, 11.1833, 11.8822, 12.5812, 13.2801]
Feature encoding complete. Total dimension: 40337 across 12 fields in 6.51s
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
  Field 10 (dow                   ): 8 distinct IDs (including UNK)
  Field 11 (hour                  ): 25 distinct IDs (including UNK)

Initializing DCN_FM model (dim=40337, fields=12, k=16, D=192, lr=0.001, l2=1e-06, seed=0)...

Starting DCN_FM training with 12 fields (Dual Context: DOW + Hour)...
Epoch  1/20 | Train Loss: 0.5851 | Valid GAUC: 0.6629 | nDCG@5: 0.5339 | Primary: 0.5984 | Time: 4.87s
Epoch  2/20 | Train Loss: 0.5079 | Valid GAUC: 0.6679 | nDCG@5: 0.5360 | Primary: 0.6019 | Time: 5.77s
Epoch  3/20 | Train Loss: 0.4997 | Valid GAUC: 0.6704 | nDCG@5: 0.5373 | Primary: 0.6039 | Time: 6.16s
Epoch  4/20 | Train Loss: 0.4962 | Valid GAUC: 0.6710 | nDCG@5: 0.5377 | Primary: 0.6043 | Time: 6.15s
Epoch  5/20 | Train Loss: 0.4919 | Valid GAUC: 0.6708 | nDCG@5: 0.5375 | Primary: 0.6041 | Time: 6.13s
Epoch  6/20 | Train Loss: 0.4865 | Valid GAUC: 0.6684 | nDCG@5: 0.5359 | Primary: 0.6022 | Time: 6.18s
Epoch  7/20 | Train Loss: 0.4810 | Valid GAUC: 0.6628 | nDCG@5: 0.5339 | Primary: 0.5984 | Time: 6.33s
Epoch  8/20 | Train Loss: 0.4746 | Valid GAUC: 0.6550 | nDCG@5: 0.5304 | Primary: 0.5927 | Time: 6.08s
Early stopping triggered at epoch 8 (best epoch: 4)

Training completed in 47.68s.
Best Validation Epoch: 4
Best Validation GAUC:    0.6710
Best Validation nDCG@5:  0.5377
Best Validation Primary: 0.6043
Saved results to baseline_runs/cycles/cycle-05/v2/results.json
```

---

## 5. Public Validation Metrics & Comparison

| Metric | Cycle 04 Champion (`v2`) | Cycle 05 Candidate (`v2`) | Delta ($\Delta$) |
|---|---|---|---|
| **GAUC** | 0.6715 | **0.6710** | -0.0005 |
| **nDCG@5** | 0.5379 | **0.5377** | -0.0002 |
| **Primary Score** | **0.6047** | **0.6043** | **-0.0004** |
| **Best Epoch** | Epoch 4 | Epoch 4 | - |
| **Training Time** | ~40.2s | 47.68s | +7.5s |

### Analysis & Interpretation
1. **Performance Comparison**: Adding `dow` and `hour` features directly as additional categorical fields yields a peak primary score of 0.6043 at epoch 4, which is slightly lower than the 10-field champion baseline (0.6047, $\Delta = -0.0004$).
2. **Overfitting Dynamics**: While epochs 1-4 steadily improved performance, overfitting began from epoch 5 onward as the training loss dropped from 0.4962 to 0.4746 while validation GAUC decayed from 0.6710 to 0.6550. The higher cross-layer parameter dimensionality ($D=192$ vs $D=160$, matrix size $192 \times 192 = 36,864$ vs $160 \times 160 = 25,600$) introduces additional degrees of freedom that slightly diluted the user-author and user-duration signal representations without contributing enough temporal generalizability on the public validation test period (which is shifted by one week).

---

## 6. Execution Time
- **Data Loading**: 3.17s
- **Feature Extraction & Encoding**: 6.51s
- **Model Training (8 epochs)**: 47.68s
- **Total Pipeline Runtime**: ~57.4s

---

## 7. Data Boundary & Leakage Audit
- **Authorized Files Accessed**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Train log: 1,141,112 rows)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Valid log: 124,909 rows)
  - `competition_data/data/user_features_pure.csv` (Demographics table)
  - `competition_data/data/video_features_basic_pure.csv` (Video metadata table)
- **Leakage Prevention Verification**:
  - Duration log-bin edges $\min$ and $\max$ were computed strictly on the training partition (`log_standard_4_08_to_4_21_pure.csv`).
  - Vocabulary mapping and entity offset indices were constructed exclusively from training split rows.
  - Public validation interactions were held strictly for offline evaluation and never used for moment estimation, gradient calculation, or vocabulary discovery.
  - Evaluation utilized the exact official `starter_kit/evaluate.py` ranking routine without modification.

---

## 8. Report Statistics
- **Character count**: 8,291
- **Whitespace-delimited word count**: 1,125
- **Line count**: 143
