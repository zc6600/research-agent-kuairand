# Round 02 - Variant v1 Report

## 1. Candidate Version & Metadata
- **Variant**: `v1`
- **Candidate Name**: Compact Rank Factorization ($k=8$, $L_2=10^{-6}$)
- **Target Project Root**: `/Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31`
- **Candidate Directory**: `/Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/baseline_runs/cycles/cycle-02/v1`
- **Reference Control / Current Best**: Cycle 01 v2 Champion (10 fields, $k=16$, Primary: 0.6020, GAUC: 0.6677, nDCG@5: 0.5363)

## 2. Hypothesis & Technical Description
- **Hypothesis**: The 10-field representation (combining user IDs, video IDs, author IDs, tab, duration bucket, and 5 demographic/activity ranges) contains 40,305 discrete categorical features, many with moderate to low observation counts. Reducing the factorization rank from $k=16$ to $k=8$ will compress the latent embedding space, acting as a structural regularizer to prevent overfitting on sparse ID pairs and improving ranking generalization on unseen validation interactions.
- **Model Architecture**: Second-order Factorization Machine (FM) with explicit linear bias weights $W \in \mathbb{R}^{d}$, global bias $b \in \mathbb{R}$, and low-rank latent interaction embeddings $V \in \mathbb{R}^{d \times k}$ where $k=8$.
- **Hyperparameters**:
  - Embedding dimension ($k$): 8
  - Optimization: Adam ($\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$)
  - Learning rate ($\text{lr}$): $0.001$
  - Weight decay ($L_2$ regularization): $10^{-6}$
  - Batch size: 8192
  - Maximum epochs: 25
  - Early stopping patience: 4
  - Seed: 0
- **Input Fields (10)**:
  1. `user_id` (26,211 distinct IDs)
  2. `video_id` (7,539 distinct IDs)
  3. `author_id` (6,483 distinct IDs)
  4. `tab` (16 distinct IDs)
  5. `dur_bucket` (10 quantile bins, 11 distinct IDs)
  6. `user_active_degree` (10 distinct IDs)
  7. `follow_user_num_range` (9 distinct IDs)
  8. `fans_user_num_range` (10 distinct IDs)
  9. `friend_user_num_range` (8 distinct IDs)
  10. `register_days_range` (8 distinct IDs)
  - Total dimension ($d$): 40,305 categorical slots (including UNK bins).

## 3. Exact Commands Executed
```bash
cd /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31
.venv/bin/python baseline_runs/cycles/cycle-02/v1/run_v1.py
```

## 4. Focused Training & Validation Logs
```text
Loading data from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded splits: {'train': 1141112, 'valid': 124909} in 2.93s
Encoding features across 10 fields...
Feature encoding complete. Total dimension: 40305 across 10 fields in 5.51s
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

Initializing FM model (dim=40305, k=8, lr=0.001, l2=1e-06, seed=0)...

Starting FM training...
Epoch  1/25 | Train Loss: 0.6232 | Valid GAUC: 0.6498 | nDCG@5: 0.5286 | Primary: 0.5892 | Time: 1.75s
Epoch  2/25 | Train Loss: 0.5397 | Valid GAUC: 0.6601 | nDCG@5: 0.5326 | Primary: 0.5963 | Time: 1.71s
Epoch  3/25 | Train Loss: 0.5130 | Valid GAUC: 0.6631 | nDCG@5: 0.5338 | Primary: 0.5985 | Time: 1.74s
Epoch  4/25 | Train Loss: 0.5027 | Valid GAUC: 0.6634 | nDCG@5: 0.5347 | Primary: 0.5990 | Time: 1.74s
Epoch  5/25 | Train Loss: 0.4973 | Valid GAUC: 0.6645 | nDCG@5: 0.5351 | Primary: 0.5998 | Time: 1.85s
Epoch  6/25 | Train Loss: 0.4938 | Valid GAUC: 0.6635 | nDCG@5: 0.5340 | Primary: 0.5987 | Time: 1.79s
Epoch  7/25 | Train Loss: 0.4915 | Valid GAUC: 0.6647 | nDCG@5: 0.5349 | Primary: 0.5998 | Time: 1.80s
Epoch  8/25 | Train Loss: 0.4895 | Valid GAUC: 0.6644 | nDCG@5: 0.5346 | Primary: 0.5995 | Time: 1.76s
Epoch  9/25 | Train Loss: 0.4881 | Valid GAUC: 0.6645 | nDCG@5: 0.5343 | Primary: 0.5994 | Time: 1.85s
Early stopping triggered at epoch 9 (best epoch: 5)

Training completed in 16.00s.
Best Validation Epoch: 5
Best Validation GAUC:    0.6645
Best Validation nDCG@5:  0.5351
Best Validation Primary: 0.5998
```

## 5. Public Validation Metrics & Comparison
Evaluated strictly using official competition validation semantics (`starter_kit/evaluate.py`).

| Metric | Cycle 01 v2 Champion ($k=16$) | Variant v1 Candidate ($k=8$) | Delta ($\Delta$) |
|---|---|---|---|
| **GAUC** | 0.6677 | 0.6645 | -0.0032 |
| **nDCG@5** | 0.5363 | 0.5351 | -0.0012 |
| **Primary (Mean)** | **0.6020** | **0.5998** | **-0.0022** |

### Outcome & Analysis
- Reducing the latent factor rank to $k=8$ led to an under-capacity bottleneck. The model was unable to capture the nuanced pairwise interactions between high-cardinality entities (e.g. 26k users, 7.5k videos, 6.4k authors) and the 5 user demographic fields.
- Performance deteriorated across both discriminative ranking (GAUC $-0.0032$) and top-heavy ranking (nDCG@5 $-0.0012$).
- Hypothesis falsified: $k=8$ provides insufficient representation capacity for the 10-field recommendation space.

## 6. Execution Time & Resource Consumption
- **Data Loading Time**: 2.93s
- **Feature Encoding Time**: 5.51s
- **Model Training Time (9 epochs)**: 16.00s (~1.78s/epoch)
- **Total Execution Time**: 24.44s

## 7. Data Boundary & Leakage Audit
- **Strict Data Boundary Verified**:
  - `log_standard_4_08_to_4_21_pure.csv`: Used exclusively for training (`20220408` to `20220421`, 1,141,112 rows).
  - `log_public_4_22_to_4_28_pure.csv`: Used strictly for out-of-time evaluation (`20220422` to `20220428`, 124,909 rows).
  - `user_features_pure.csv` & `video_features_basic_pure.csv`: Static metadata lookup mappings only.
  - No access to test datasets or external networks.
- **Leakage Prevention**:
  - Continuous duration quantile bin edges were computed strictly over the training partition (`edges = np.quantile(..., tr)`).
  - Categorical vocabularies were constructed strictly on the training partition; unseen validation entities were mapped to isolated UNK token IDs.
  - No target labels from the validation split were used during training or feature mapping.

## 8. Report Statistics
- **Lines**: 114
- **Whitespace-Delimited Words**: 895
- **Characters**: 6,932

