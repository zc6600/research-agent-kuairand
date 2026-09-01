# Research Candidate Report: Round 01 - Variant v1

## 1. Candidate Overview & Metadata
- **Candidate Identifier**: `v1`
- **Cycle**: `cycle-01`
- **Focus Area**: Video Metadata Extension (8 fields)
- **Model Family**: Second-Order Factorization Machine (FM)
- **Implementation File**: `baseline_runs/cycles/cycle-01/v1/run_v1.py`
- **Date/Time**: 2026-08-31T21:08:30+08:00

---

## 2. Hypothesis & Technical Description
### Hypothesis
Incorporating granular video-side metadata (`author_id`, `music_id`, `video_type`, `upload_type`) alongside baseline categorical signals (`user_id`, `video_id`, `tab`, `dur_bucket`) into a Factorization Machine will enrich cross-feature representations (e.g. user-author affinity, music-type matching, format preferences) and improve recommendation ranking performance over the 5-field baseline on KuaiRand-Pure.

### Technical Architecture & Formulation
- **Field Set (8 Fields)**:
  1. `user_id` (from interaction log)
  2. `video_id` (from interaction log)
  3. `author_id` (from `video_features_basic_pure.csv`)
  4. `music_id` (from `video_features_basic_pure.csv`)
  5. `video_type` (from `video_features_basic_pure.csv`)
  6. `upload_type` (from `video_features_basic_pure.csv`)
  7. `tab` (from interaction log)
  8. `dur_bucket` (10-quantile bucketed from interaction `duration_ms`)
- **Total Field Dimension**: 47,440 categories (with 1 UNK category per field).
  - `user_id`: 26,211
  - `video_id`: 7,539
  - `author_id`: 6,483
  - `music_id`: 7,161
  - `video_type`: 4
  - `upload_type`: 15
  - `tab`: 16
  - `dur_bucket`: 11
- **Model Mathematical Formulation**:
  $$\hat{y}(x) = \sigma\left( b + \sum_{i=1}^{F} w_{x_i} + \frac{1}{2} \sum_{f=1}^k \left[ \left( \sum_{i=1}^F v_{x_i, f} \right)^2 - \sum_{i=1}^F v_{x_i, f}^2 \right] \right)$$
  where $F=8$, latent embedding dimension $k=16$, optimized with Adam ($\text{lr}=0.001$, $\beta_1=0.9$, $\beta_2=0.999$, $\epsilon=10^{-8}$) and $L_2$ weight regularization $\lambda=10^{-6}$.
- **Training Constraints**: Batch size $8192$, maximum epochs $25$, early stopping patience $4$ monitoring validation `primary`.

---

## 3. Exact Execution Command
Executed strictly from the target project root using the project virtual environment `.venv`:

```bash
cd /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31
.venv/bin/python baseline_runs/cycles/cycle-01/v1/run_v1.py --data_dir competition_data/data --k 16 --lr 0.001 --batch_size 8192 --max_epochs 25 --patience 4 --seed 0
```

---

## 4. Execution & Training Logs
```text
======================================================================
KuaiRand-Pure Research: Round 01 - Variant v1
Focus: Video Metadata Extension (8 fields: user_id, video_id, author_id, music_id, video_type, upload_type, tab, dur_bucket)
Hyperparameters: k=16, lr=0.001, batch_size=8192, max_epochs=25, patience=4, seed=0
======================================================================
Loading video features from competition_data/data/video_features_basic_pure.csv...
Loaded metadata for 7583 videos.
Loading log file competition_data/data/log_standard_4_08_to_4_21_pure.csv...
Loaded 1141112 interactions from log_standard_4_08_to_4_21_pure.csv.
Loading log file competition_data/data/log_public_4_22_to_4_28_pure.csv...
Loaded 124909 interactions from log_public_4_22_to_4_28_pure.csv.
Computing duration quantile buckets strictly on training split...
Building field vocabularies strictly on training split...
Field summary (8 fields):
  Field 'user_id': 26211 unique categories (including UNK at slot 26210)
  Field 'video_id': 7539 unique categories (including UNK at slot 7538)
  Field 'author_id': 6483 unique categories (including UNK at slot 6482)
  Field 'music_id': 7161 unique categories (including UNK at slot 7160)
  Field 'video_type': 4 unique categories (including UNK at slot 3)
  Field 'upload_type': 15 unique categories (including UNK at slot 14)
  Field 'tab': 16 unique categories (including UNK at slot 15)
  Field 'dur_bucket': 11 unique categories (including UNK at slot 10)
Total vocabulary dimension: 47440
Transforming training dataset...
Transforming validation dataset...

Initializing FM model (dim=47440, k=16, lr=0.001, batch_size=8192, seed=0)...
Beginning training (max_epochs=25, patience=4)...

Epoch  1/25 | Train Loss: 0.6204 | Val GAUC: 0.6546 | Val nDCG@5: 0.5307 | Val Primary: 0.5926 | Time: 2.59s
Epoch  2/25 | Train Loss: 0.5323 | Val GAUC: 0.6619 | Val nDCG@5: 0.5336 | Val Primary: 0.5977 | Time: 2.56s
Epoch  3/25 | Train Loss: 0.5082 | Val GAUC: 0.6639 | Val nDCG@5: 0.5342 | Val Primary: 0.5990 | Time: 2.56s
Epoch  4/25 | Train Loss: 0.4996 | Val GAUC: 0.6649 | Val nDCG@5: 0.5347 | Val Primary: 0.5998 | Time: 2.35s
Epoch  5/25 | Train Loss: 0.4948 | Val GAUC: 0.6651 | Val nDCG@5: 0.5353 | Val Primary: 0.6002 | Time: 2.31s
Epoch  6/25 | Train Loss: 0.4910 | Val GAUC: 0.6655 | Val nDCG@5: 0.5347 | Val Primary: 0.6001 | Time: 2.31s
Epoch  7/25 | Train Loss: 0.4876 | Val GAUC: 0.6658 | Val nDCG@5: 0.5347 | Val Primary: 0.6002 | Time: 2.32s
Epoch  8/25 | Train Loss: 0.4840 | Val GAUC: 0.6661 | Val nDCG@5: 0.5354 | Val Primary: 0.6007 | Time: 2.22s
Epoch  9/25 | Train Loss: 0.4804 | Val GAUC: 0.6650 | Val nDCG@5: 0.5338 | Val Primary: 0.5994 | Time: 2.07s
Epoch 10/25 | Train Loss: 0.4765 | Val GAUC: 0.6631 | Val nDCG@5: 0.5336 | Val Primary: 0.5984 | Time: 2.07s
Epoch 11/25 | Train Loss: 0.4725 | Val GAUC: 0.6612 | Val nDCG@5: 0.5325 | Val Primary: 0.5969 | Time: 2.06s
Epoch 12/25 | Train Loss: 0.4685 | Val GAUC: 0.6612 | Val nDCG@5: 0.5327 | Val Primary: 0.5970 | Time: 2.06s

Early stopping triggered after 12 epochs (no primary improvement for 4 consecutive epochs).

Training completed in 27.47s.
Restoring best checkpoint from Epoch 8 with Primary = 0.6007...

======================================================================
FINAL OFFICIAL PUBLIC VALIDATION METRICS (Variant v1 - 8 fields)
======================================================================
Validation Users : 22377
Validation Rows  : 124909
Best Epoch       : 8
Validation GAUC  : 0.666062 (0.6661)
Validation nDCG@5: 0.535374 (0.5354)
Validation Primary: 0.600718 (0.6007)
Training Time    : 27.47 s
Total Run Time   : 36.01 s
======================================================================

DELTA VS CONTROL (Official 5-field FM Baseline):
  GAUC    : 0.6661 vs 0.6671 (Delta: -0.0010)
  nDCG@5  : 0.5354 vs 0.5358 (Delta: -0.0004)
  Primary : 0.6007 vs 0.6015 (Delta: -0.0008)
======================================================================
```

---

## 5. Quantitative Results & Comparison

| Metric | Control Baseline (5 Fields) | Candidate v1 (8 Fields) | Absolute Delta | Relative Change |
|---|---|---|---|---|
| **Validation GAUC** | 0.6671 | **0.6661** (0.666062) | -0.0010 | -0.15% |
| **Validation nDCG@5** | 0.5358 | **0.5354** (0.535374) | -0.0004 | -0.07% |
| **Primary (Mean)** | 0.6015 | **0.6007** (0.600718) | -0.0008 | -0.13% |
| **Best Epoch** | - | Epoch 8 | - | - |
| **Training Time** | ~25 s | 27.47 s | +2.47 s | - |
| **Total Runtime** | - | 36.01 s | - | - |

### Key Observations & Diagnostic Findings
1. **Slight Performance Regression**: Extending video metadata to 8 fields (`author_id`, `music_id`, `video_type`, `upload_type`) yielded a slight degradation in validation Primary (-0.0008, from 0.6015 to 0.6007).
2. **High Sparsity & Parameter Dilution**: `music_id` contains 7,161 categories, nearly as many as `video_id` (7,539), creating high parameter cardinality with limited interaction occurrences per music token.
3. **Overfitting Dynamics**: As shown in the epoch progression, training loss continuously fell from 0.6204 to 0.4685, while validation GAUC and nDCG peaked at Epoch 8 before declining noticeably, confirming mild overfitting due to increased embedding parameters without stronger regularization.

---

## 6. Data Boundary & Leakage Audit
- [x] **Strict File Inventory Adherence**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Used for training: 1,141,112 rows)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Used strictly for validation: 124,909 rows)
  - `competition_data/data/video_features_basic_pure.csv` (Used for video metadata lookup: 7,583 items)
  - No external downloads, web access, or forbidden files (`log_random_4_22_to_4_28_pure.csv` / test splits) were touched.
- [x] **Split Isolation & Temporal Integrity**:
  - Duration quantile boundaries (`edges`) were derived solely from the training split `log_standard_4_08_to_4_21_pure.csv`.
  - Vocabularies and category offsets were built strictly from the training split. Unseen validation categories safely fall into the field UNK index.
  - Zero target leakage from future validation dates into training representations.

---

## 7. Report File Statistics
- **Character Count**: 8,991
- **Whitespace-delimited Word Count**: 1,154
- **Line Count**: 159

