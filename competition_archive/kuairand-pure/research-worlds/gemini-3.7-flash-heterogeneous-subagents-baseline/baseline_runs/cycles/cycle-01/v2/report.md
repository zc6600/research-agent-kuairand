# Candidate Experiment Report: Round 01 - Variant v2

## 1. Candidate Overview
- **Variant Version**: `v2`
- **Focus / Hypothesis**: User Demographic Extension (10 fields)
- **Technical Description**:
  Extends the 5-field Factorization Machine (FM) baseline by incorporating 5 key user demographic and profile features from `user_features_pure.csv`:
  1. `user_active_degree` (activity level)
  2. `follow_user_num_range` (following count bucket)
  3. `fans_user_num_range` (follower/fan count bucket)
  4. `friend_user_num_range` (friend count bucket)
  5. `register_days_range` (account tenure bucket)
  
  These are combined with the 5 baseline fields (`user_id`, `video_id`, `author_id`, `tab`, `dur_bucket`) for a total of 10 feature fields. The Factorization Machine models pairwise second-order interactions across all 10 fields, capturing how user activity and account maturity interact with video content and viewing context.

## 2. Experimental Setup & Exact Command
- **Working Directory**: `/Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31`
- **Command Executed**:
  ```bash
  .venv/bin/python baseline_runs/cycles/cycle-01/v2/run_v2.py
  ```
- **Interpreter**: Python 3.12.12 (`.venv/bin/python`)
- **Hyperparameters**:
  - Embedding Dimension ($k$): 16
  - Learning Rate: 0.001 (Adam optimizer with $\beta_1=0.9, \beta_2=0.999$)
  - $L_2$ Regularization: $10^{-6}$
  - Batch Size: 8192
  - Max Epochs: 25
  - Early Stopping Patience: 4 epochs on validation primary score
  - Random Seed: 0

## 3. Training & Validation Execution Logs
```text
Loading data from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded splits: {'train': 1141112, 'valid': 124909} in 2.89s
Encoding features across 10 fields...
Feature encoding complete. Total dimension: 40305 across 10 fields in 5.41s
  Field  0 (user_id               ): 26211 distinct IDs (including UNK)
  Field  1 (video_id              ): 7539 distinct IDs (including UNK)
  Field  2 (author_id             ): 6483 distinct IDs (including UNK)
  Field  3 (tab                   ): 16 distinct IDs (including UNK)
  Field  4 (dur_bucket            ): 11 distinct IDs (including UNK)
  Field  5 (user_active_degree    ): 10 distinct IDs (including UNK)
  Field  6 (follow_user_num_range ): 9 distinct IDs (including UNK)
  Field  7 (fans_user_num_range   ): 10 distinct IDs (including UNK)
  Field  8 (friend_user_num_range ): 8 distinct IDs (including UNK)
  Field  9 (register_days_range   ): 8 distinct IDs (including UNK)

Initializing FM model (dim=40305, k=16, lr=0.001, seed=0)...

Starting FM training...
Epoch  1/25 | Train Loss: 0.6133 | Valid GAUC: 0.6558 | nDCG@5: 0.5305 | Primary: 0.5931 | Time: 2.39s
Epoch  2/25 | Train Loss: 0.5256 | Valid GAUC: 0.6640 | nDCG@5: 0.5341 | Primary: 0.5990 | Time: 2.36s
Epoch  3/25 | Train Loss: 0.5051 | Valid GAUC: 0.6664 | nDCG@5: 0.5353 | Primary: 0.6009 | Time: 2.37s
Epoch  4/25 | Train Loss: 0.4979 | Valid GAUC: 0.6665 | nDCG@5: 0.5356 | Primary: 0.6011 | Time: 2.35s
Epoch  5/25 | Train Loss: 0.4937 | Valid GAUC: 0.6667 | nDCG@5: 0.5359 | Primary: 0.6013 | Time: 2.43s
Epoch  6/25 | Train Loss: 0.4907 | Valid GAUC: 0.6673 | nDCG@5: 0.5358 | Primary: 0.6015 | Time: 2.36s
Epoch  7/25 | Train Loss: 0.4880 | Valid GAUC: 0.6677 | nDCG@5: 0.5363 | Primary: 0.6020 | Time: 2.38s
Epoch  8/25 | Train Loss: 0.4854 | Valid GAUC: 0.6667 | nDCG@5: 0.5355 | Primary: 0.6011 | Time: 2.37s
Epoch  9/25 | Train Loss: 0.4829 | Valid GAUC: 0.6661 | nDCG@5: 0.5348 | Primary: 0.6005 | Time: 2.37s
Epoch 10/25 | Train Loss: 0.4801 | Valid GAUC: 0.6650 | nDCG@5: 0.5347 | Primary: 0.5999 | Time: 2.38s
Epoch 11/25 | Train Loss: 0.4772 | Valid GAUC: 0.6638 | nDCG@5: 0.5339 | Primary: 0.5988 | Time: 2.35s
Early stopping triggered at epoch 11 (best epoch: 7)

Training completed in 26.11s.
Best Validation Epoch: 7
Best Validation GAUC:    0.6677
Best Validation nDCG@5:  0.5363
Best Validation Primary: 0.6020
```

## 4. Public Validation Metrics & Comparison
Evaluated on the official public validation split (2022-04-22 to 2022-04-28, 124,909 impressions across 22,377 users) using `starter_kit/evaluate.py` semantics:

| Metric | Control (Official Baseline) | Variant v2 (Best @ Epoch 7) | Delta vs Control |
|---|---|---|---|
| **Validation GAUC** | 0.6671 | **0.6677** (0.667687) | **+0.0006** |
| **Validation nDCG@5** | 0.5358 | **0.5363** (0.536347) | **+0.0005** |
| **Validation Primary** | 0.6015 | **0.6020** (0.602017) | **+0.0005** |

- **Early Stopping Convergence**: Peak performance reached at Epoch 7, followed by controlled early stopping after 4 consecutive non-improving epochs at Epoch 11.
- **Outcome**: Variant v2 outperforms the Control baseline across all three official evaluation metrics (GAUC +0.0006, nDCG@5 +0.0005, Primary +0.0005).

## 5. Execution Time & Resource Telemetry
- **Data Loading Time**: 2.89s
- **Feature Encoding Time**: 5.41s
- **Model Training Time**: 26.11s (11 epochs)
- **Total Execution Elapsed Time**: 34.41s
- **Peak Memory**: Minimal numpy array footprint (< 500 MB RAM)

## 6. Data Boundary & Leakage Audit
- **Permitted Data Sources Used**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Train set: 1,141,112 rows)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Validation set: 124,909 rows)
  - `competition_data/data/user_features_pure.csv` (User features)
  - `competition_data/data/video_features_basic_pure.csv` (Video author mapping)
- **Leakage Prevention Measures**:
  - Duration quantile discretization edges were calculated strictly on the training partition (`log_standard_4_08_to_4_21_pure.csv`).
  - Feature vocabularies and dimension offsets were constructed solely on the training partition. Unseen categorical values in the validation set safely mapped to field-specific UNK tokens.
  - No external downloads, hidden test sets, or disallowed files were accessed.


## 7. Report Statistics
- **Character Count**: 6208
- **Word Count (whitespace-delimited)**: 823
- **Line Count**: 106
