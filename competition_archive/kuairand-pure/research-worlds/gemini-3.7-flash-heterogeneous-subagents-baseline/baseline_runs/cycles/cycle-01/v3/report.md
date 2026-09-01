# Experiment Report: Candidate v3 - Full CWM-13 Joint Feature Representation

## 1. Candidate Overview
- **Candidate Version:** `v3`
- **Cycle:** `cycle-01`
- **Model Architecture:** Factorization Machine (FM) with 2nd-order feature interactions
- **Feature Set:** Full CWM-13 Joint Feature Representation (13 fields)
  - Log / Interaction Fields (4): `user_id`, `video_id`, `tab`, `dur_bucket` (10 quantile buckets)
  - Video Metadata Fields (4): `author_id`, `music_id`, `video_type`, `upload_type`
  - User Profile Fields (5): `user_active_degree`, `follow_user_num_range`, `fans_user_num_range`, `friend_user_num_range`, `register_days_range`
- **Hyperparameters:**
  - Embedding Dimension ($k$): 16
  - Learning Rate: 0.001 (Adam optimizer, $\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$)
  - Regularization ($L_2$): $10^{-6}$
  - Batch Size: 8192
  - Max Epochs: 25
  - Early Stopping Patience: 4 epochs (monitoring validation `primary` metric)
  - Random Seed: 0

---

## 2. Hypothesis & Technical Description

### Hypothesis
Extending the standard 5-field baseline (`user_id`, `video_id`, `author_id`, `tab`, `dur_bucket`) to the full 13-field joint representation used in CWM (adding 3 extra video metadata fields: `music_id`, `video_type`, `upload_type`, and 5 user demographic/activity fields: `user_active_degree`, `follow_user_num_range`, `fans_user_num_range`, `friend_user_num_range`, `register_days_range`) will enrich the feature representation and allow the Factorization Machine to learn pairwise cross-field interactions (e.g., user activity level $\times$ video type, register duration $\times$ music category), thereby improving within-user ranking performance (`GAUC`, `nDCG@5`, and `primary`).

### Technical Implementation
1. **Feature Engineering & Quantization:**
   - User profile table (`user_features_pure.csv`) is indexed by `user_id` to extract 5 discrete profile fields.
   - Video metadata table (`video_features_basic_pure.csv`) is indexed by `video_id` to extract 4 discrete metadata fields.
   - Video duration (`duration_ms`) is quantized into 10 quantile bins whose boundaries $[11633, 19633, 32083, 49420, 70233, 91466, 116958, 161516, 235766]$ are computed strictly on the training set (`log_standard_4_08_to_4_21_pure.csv`).
2. **Vocabulary Encoding & Field Offsets:**
   - Vocabularies for all 13 fields are constructed strictly from the training partition. Unseen categories in validation/test are mapped to field-specific UNK buckets.
   - Cumulative offset indexing maps all categorical features into a global index space of dimension $D = 47,485$.
3. **FM Optimization:**
   - 1st-order linear weights $W \in \mathbb{R}^D$ and 2nd-order factor vectors $V \in \mathbb{R}^{D \times 16}$.
   - Exact gradient calculation with sparse updates (`np.add.at`) and Adam optimization.
   - Per-epoch validation on `log_public_4_22_to_4_28_pure.csv` computing official KuaiRand ranking metrics (`GAUC` and `nDCG@5`). Best checkpoint weights are restored upon convergence.

---

## 3. Exact Command Line Executed

```bash
cd /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31
.venv/bin/python baseline_runs/cycles/cycle-01/v3/run_v3.py
```

---

## 4. Training & Validation Execution Logs

```text
======================================================================
Variant v3 Experiment: CWM-13 Joint Features FM Model
Hyperparameters: k=16, lr=0.001, l2=1e-06, batch_size=8192, max_epochs=25, patience=4, seed=0
======================================================================
Loading data from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded user features for 27285 users.
Loaded video features for 7583 videos.
Loaded 1141112 train rows (2022-04-08 to 2022-04-21).
Loaded 124909 valid rows (2022-04-22 to 2022-04-28).
Duration quantile edges (10 buckets) computed from train: [ 11633.  19633.  32083.  49420.  70233.  91466. 116958. 161516. 235766.]
Field dimensions: {'user_id': 26211, 'video_id': 7539, 'tab': 16, 'dur_bucket': 11, 'author_id': 6483, 'music_id': 7161, 'video_type': 4, 'upload_type': 15, 'user_active_degree': 10, 'follow_user_num_range': 9, 'fans_user_num_range': 10, 'friend_user_num_range': 8, 'register_days_range': 8}
Total one-hot/embedding dimension: 47485
Encoded train: X shape (1141112, 13), pos_rate 0.3366
Encoded valid: X shape (124909, 13), pos_rate 0.3133
Data preparation complete in 9.51s

--- Starting Training ---
Epoch  1/25 | Train Loss: 0.6026 | Valid GAUC: 0.6588 | nDCG@5: 0.5322 | Primary: 0.5955 | Time: 3.10s
  --> New best primary score: 0.5955 (Saved checkpoint)
Epoch  2/25 | Train Loss: 0.5232 | Valid GAUC: 0.6640 | nDCG@5: 0.5345 | Primary: 0.5992 | Time: 3.25s
  --> New best primary score: 0.5992 (Saved checkpoint)
Epoch  3/25 | Train Loss: 0.5055 | Valid GAUC: 0.6656 | nDCG@5: 0.5352 | Primary: 0.6004 | Time: 3.45s
  --> New best primary score: 0.6004 (Saved checkpoint)
Epoch  4/25 | Train Loss: 0.4983 | Valid GAUC: 0.6656 | nDCG@5: 0.5349 | Primary: 0.6002 | Time: 3.45s
  --> No improvement for 1 epoch(s) (patience: 4)
Epoch  5/25 | Train Loss: 0.4939 | Valid GAUC: 0.6645 | nDCG@5: 0.5351 | Primary: 0.5998 | Time: 3.46s
  --> No improvement for 2 epoch(s) (patience: 4)
Epoch  6/25 | Train Loss: 0.4906 | Valid GAUC: 0.6644 | nDCG@5: 0.5343 | Primary: 0.5994 | Time: 3.68s
  --> No improvement for 3 epoch(s) (patience: 4)
Epoch  7/25 | Train Loss: 0.4877 | Valid GAUC: 0.6638 | nDCG@5: 0.5339 | Primary: 0.5988 | Time: 3.70s
  --> No improvement for 4 epoch(s) (patience: 4)

[Early Stopping Triggered] at epoch 7. Stopping training.

======================================================================
FINAL VALIDATION RESULTS (Best Checkpoint Restored)
======================================================================
Validation GAUC:    0.6656 (Control: 0.6671, Delta: -0.0015)
Validation nDCG@5:  0.5352 (Control: 0.5358, Delta: -0.0006)
Validation Primary: 0.6004 (Control: 0.6015, Delta: -0.0011)
Total Execution Time: 33.96s
======================================================================
```

---

## 5. Public Validation Metrics & Comparison

| Metric | Candidate `v3` (CWM-13) | Current Best (Control) | Delta vs Control | Status |
| :--- | :--- | :--- | :--- | :--- |
| **GAUC** | **0.6656** | 0.6671 | **-0.0015** | Slightly Lower |
| **nDCG@5** | **0.5352** | 0.5358 | **-0.0006** | Slightly Lower |
| **Primary Metric** | **0.6004** | **0.6015** | **-0.0011** | Slightly Lower |

### In-Depth Result Analysis
1. **Performance vs Baseline:**
   The full CWM-13 model achieves a primary score of **0.6004** (GAUC 0.6656, nDCG@5 0.5352) on the public validation set, which is slightly below the 5-field baseline control (0.6015, $\Delta = -0.0011$).
2. **Why User Profile Features Do Not Strongly Boost FM Ranking:**
   Within-user ranking evaluates candidate items for a single given user. Static user demographic and activity fields (`user_active_degree`, `fans_user_num_range`, etc.) are constant across all candidate items for a given user impression session. In a 2nd-order FM, interactions between static user features and other static user features merely add a constant shift to that user's prediction score, leaving intra-user rank order unchanged. Furthermore, pairwise interactions between user demographic buckets and item fields increase the parameter count ($D=47,485$) without offering fine-grained discrimination over direct item-user memorization.
3. **Training Dynamics:**
   The model reached peak validation performance at Epoch 3 (Primary: 0.6004) before starting to overfit on the training set (training loss steadily decreased from 0.5055 at epoch 3 down to 0.4877 at epoch 7). Early stopping triggered cleanly at epoch 7.

---

## 6. Execution Time & Resource Consumption

- **Data Loading & Preprocessing Time:** 9.51 seconds
- **Training Time (7 epochs):** 24.45 seconds (~3.49 seconds/epoch)
- **Total End-to-End Elapsed Time:** 33.96 seconds

---

## 7. Data Boundary & Leakage Audit

A strict verification was conducted to ensure full compliance with the KuaiRand-Pure benchmark guidelines:
1. **Allowed Files Checked:**
   - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Used strictly for training)
   - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Used strictly for validation)
   - `competition_data/data/user_features_pure.csv` (Static user metadata)
   - `competition_data/data/video_features_basic_pure.csv` (Static video metadata)
   - No external or unapproved files were accessed or downloaded.
2. **No Data Leakage:**
   - Quantile duration bucket boundaries were computed strictly on the training set (`log_standard_4_08_to_4_21_pure.csv`).
   - Feature vocabularies and categorical mappings were extracted strictly from the training partition. Unseen items and users in the validation set were mapped to dedicated UNK buckets.
   - Validation labels and scores were used solely for checkpoint selection and metric evaluation.

---

## 8. Document Statistics
- **Character Count:** 9,282
- **Word Count (Whitespace-delimited):** 1,157
- **Line Count:** 146

