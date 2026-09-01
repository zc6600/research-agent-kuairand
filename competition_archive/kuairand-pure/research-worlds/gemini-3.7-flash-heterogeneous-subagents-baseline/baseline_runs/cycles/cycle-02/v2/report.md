# Candidate Experiment Report: Round 02 - Variant v2

## 1. Candidate Overview
- **Variant Version**: `v2`
- **Focus / Hypothesis**: Expanded Rank Factorization ($k=32$, $L_2=10^{-6}$) on 10 Feature Fields
- **Technical Description**:
  Investigates whether expanding the latent factor embedding dimension from $k=16$ to $k=32$ in the 10-field Factorization Machine (FM) architecture improves representation capacity and expressive multi-field pairwise interactions.
  The 10 feature fields include:
  1. `user_id` (User identity)
  2. `video_id` (Item identity)
  3. `author_id` (Content creator identity)
  4. `tab` (User browsing interface tab)
  5. `dur_bucket` (Discretized video duration quantile bucket)
  6. `user_active_degree` (User activity degree bucket)
  7. `follow_user_num_range` (User follow count bucket)
  8. `fans_user_num_range` (User fan/follower count bucket)
  9. `friend_user_num_range` (User friend count bucket)
  10. `register_days_range` (Account registration tenure bucket)

  The model computes all $\binom{10}{2} = 45$ second-order pairwise interactions via $k=32$ inner products:
  $$\hat{y}(\mathbf{x}) = w_0 + \sum_{i=1}^{10} w_i + \frac{1}{2}\sum_{f=1}^{32} \left[ \left(\sum_{i=1}^{10} v_{i,f}\right)^2 - \sum_{i=1}^{10} v_{i,f}^2 \right]$$
  Optimized with Adam ($\beta_1=0.9, \beta_2=0.999$, $\text{lr}=0.001$, $L_2=10^{-6}$) and batch size 8192.

## 2. Experimental Setup & Exact Command
- **Working Directory**: `/Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31`
- **Command Executed**:
  ```bash
  .venv/bin/python baseline_runs/cycles/cycle-02/v2/run_v2.py
  ```
- **Interpreter**: Python 3.12.12 (`.venv/bin/python`)
- **Hyperparameters**:
  - Latent Embedding Dimension ($k$): 32 (expanded from 16)
  - Learning Rate: 0.001 (Adam optimizer)
  - $L_2$ Regularization: $10^{-6}$
  - Batch Size: 8192
  - Max Epochs: 25
  - Early Stopping Patience: 4 epochs on validation primary score
  - Random Seed: 0

## 3. Training & Validation Execution Logs
```text
Loading data from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded splits: {'train': 1141112, 'valid': 124909} in 3.24s
Encoding features across 10 fields...
Feature encoding complete. Total dimension: 40305 across 10 fields in 6.05s
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

Initializing FM model (dim=40305, k=32, lr=0.001, l2=1e-06, seed=0)...

Starting FM training...
Epoch  1/25 | Train Loss: 0.6005 | Valid GAUC: 0.6592 | nDCG@5: 0.5316 | Primary: 0.5954 | Time: 4.64s
Epoch  2/25 | Train Loss: 0.5158 | Valid GAUC: 0.6649 | nDCG@5: 0.5345 | Primary: 0.5997 | Time: 4.59s
Epoch  3/25 | Train Loss: 0.4997 | Valid GAUC: 0.6664 | nDCG@5: 0.5352 | Primary: 0.6008 | Time: 4.62s
Epoch  4/25 | Train Loss: 0.4924 | Valid GAUC: 0.6664 | nDCG@5: 0.5353 | Primary: 0.6009 | Time: 4.62s
Epoch  5/25 | Train Loss: 0.4865 | Valid GAUC: 0.6646 | nDCG@5: 0.5348 | Primary: 0.5997 | Time: 4.68s
Epoch  6/25 | Train Loss: 0.4809 | Valid GAUC: 0.6635 | nDCG@5: 0.5345 | Primary: 0.5990 | Time: 4.63s
Epoch  7/25 | Train Loss: 0.4750 | Valid GAUC: 0.6624 | nDCG@5: 0.5336 | Primary: 0.5980 | Time: 4.68s
Epoch  8/25 | Train Loss: 0.4688 | Valid GAUC: 0.6605 | nDCG@5: 0.5330 | Primary: 0.5968 | Time: 4.64s
Early stopping triggered at epoch 8 (best epoch: 4)

Training completed in 37.08s.
Best Validation Epoch: 4
Best Validation GAUC:    0.6664
Best Validation nDCG@5:  0.5353
Best Validation Primary: 0.6009
Saved results to /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/baseline_runs/cycles/cycle-02/v2/results.json
```

## 4. Public Validation Metrics & Comparison
Evaluated on the official public validation split (2022-04-22 to 2022-04-28, 124,909 impressions across 22,377 users) using `starter_kit/evaluate.py` semantics:

| Metric | Cycle 01 v2 Champion ($k=16$) | Variant v2 ($k=32$, Best @ Epoch 4) | Delta vs Current Best |
|---|---|---|---|
| **Validation GAUC** | **0.6677** (0.667687) | 0.6664 (0.666402) | **-0.0013** |
| **Validation nDCG@5** | **0.5363** (0.536347) | 0.5353 (0.535325) | **-0.0010** |
| **Validation Primary** | **0.6020** (0.602017) | 0.6009 (0.600863) | **-0.0011** |

### Analysis of Results
1. **Capacity vs Generalization Trade-off**: Doubling the embedding rank from $k=16$ to $k=32$ increased model parameters from 644,880 to 1,289,760. With minimal $L_2$ regularization ($10^{-6}$), the model rapidly fitted the training interactions (training loss reduced to 0.4688 at epoch 8 vs 0.4772 for $k=16$).
2. **Premature Overfitting**: Validation metrics peaked earlier at Epoch 4 (Primary = 0.6009) compared to Epoch 7 (Primary = 0.6020) for $k=16$. Performance steadily degraded on validation data after Epoch 4.
3. **Conclusion**: Higher latent rank $k=32$ without stronger regularization leads to over-parameterization and worse out-of-sample ranking performance. $k=16$ remains a more effective inductive bias for this feature density.

## 5. Execution Time & Resource Telemetry
- **Data Loading Time**: 3.24s
- **Feature Encoding Time**: 6.05s
- **Model Training Time**: 37.08s (8 epochs @ ~4.63s/epoch)
- **Total Execution Elapsed Time**: 46.37s
- **Hardware / Memory Footprint**: Minimal NumPy memory footprint (< 600 MB RAM)

## 6. Data Boundary & Leakage Audit
- **Permitted Data Sources Used**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Train set: 1,141,112 rows)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Validation set: 124,909 rows)
  - `competition_data/data/user_features_pure.csv` (User demographic features)
  - `competition_data/data/video_features_basic_pure.csv` (Video author mapping)
- **Leakage Prevention Measures**:
  - Duration quantile discretization edges were calculated strictly on the training partition (`log_standard_4_08_to_4_21_pure.csv`).
  - Feature vocabularies and dimension offsets were constructed solely on the training partition. Unseen categorical values in the validation set safely mapped to field-specific UNK tokens.
  - No external downloads, hidden test sets, or disallowed files were accessed.

## 7. Report Statistics
- **Character Count**: 7100
- **Word Count (whitespace-delimited)**: 893
- **Line Count**: 113
