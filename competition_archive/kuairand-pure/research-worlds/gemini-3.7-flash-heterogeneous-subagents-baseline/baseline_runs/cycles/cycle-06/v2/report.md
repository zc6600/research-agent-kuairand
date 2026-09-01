# Candidate Experiment Report: Round 06 - Variant v2

## 1. Candidate Overview & Hypothesis
- **Candidate Version**: Variant `v2`
- **Model Architecture**: Multi-Task Joint Optimization DCN-FM with Like Auxiliary
- **Core Hypothesis**: Incorporating `is_like` (an explicit, high-intent user interaction signal with ~1.87% base rate) as an auxiliary multi-task training objective ($L = L_{\text{long\_view}} + 0.3 \cdot L_{\text{like}}$) regularizes the shared 10-field embedding layer and explicit cross representation. This shared feature representation prevents overfitting on noisy long-view labels while aligning representations toward user-preferred content.
- **Key Technical Details**:
  - **Shared Representations**: 10 fields (user_id, video_id, author_id, tab, 20 log-duration buckets, user_active_degree, follow_user_num_range, fans_user_num_range, friend_user_num_range, register_days_range) mapped to $k=16$ embedding dimensions ($D=160$ concatenated).
  - **Shared Cross Layer**: Explicit polynomial interaction layer $x_1 = x_0 \odot (x_0 W_c + b_c) + x_0$ where $W_c \in \mathbb{R}^{160 \times 160}, b_c \in \mathbb{R}^{160}$.
  - **Shared FM Interaction**: 2nd-order vector-product interaction $\frac{1}{2}\left((\sum_i E_i)^2 - \sum_i E_i^2\right)$.
  - **Dedicated Output Heads**: Independent linear weights ($W_{\text{long}}, W_{\text{like}} \in \mathbb{R}^{\text{dim}}$), biases ($b_{\text{long}}, b_{\text{like}}$), and projection vectors ($w_{p,\text{long}}, w_{p,\text{like}} \in \mathbb{R}^{160}$).
  - **Multi-Task Gradient Flow**: Gradients from primary BCE loss ($\frac{\partial L_{\text{long}}}{\partial z_{\text{long}}}$) and auxiliary BCE loss ($\alpha \frac{\partial L_{\text{like}}}{\partial z_{\text{like}}}$, $\alpha=0.3$) are jointly accumulated into shared embedding table $V$ and cross weights $W_c, b_c$.
  - **Evaluation Protocol**: Strictly evaluated on `long_view` ranking metrics on out-of-time public validation split (`log_public_4_22_to_4_28_pure.csv`).

## 2. Exact Execution Command
```bash
.venv/bin/python baseline_runs/cycles/cycle-06/v2/run_v2.py 2>&1 | tee baseline_runs/cycles/cycle-06/v2/run.log
```

## 3. Training & Validation Execution Logs
```text
Loading data from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded splits: {'train': 1141112, 'valid': 124909} in 3.30s
Encoding features across 10 fields with 20 Logarithmic Duration Bins...
Train log(1 + duration_ms) range: [0.0000, 13.9791]
Created 19 internal cutoffs for 20 log duration bins:
  Cutoffs: [0.699, 1.3979, 2.0969, 2.7958, 3.4948, 4.1937, 4.8927, 5.5916, 6.2906, 6.9895, 7.6885, 8.3875, 9.0864, 9.7854, 10.4843, 11.1833, 11.8822, 12.5812, 13.2801]
Feature encoding complete. Total dimension: 40304 across 10 fields in 6.14s
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

Initializing Multi-Task DCN_FM model (dim=40304, fields=10, k=16, D=160, alpha=0.3, lr=0.001, l2=1e-06, seed=0)...

Starting Multi-Task DCN_FM training with Like Auxiliary (alpha=0.3)...
Epoch  1/20 | Train Tot: 0.6789 (Long: 0.5956, Like: 0.2778) | Valid GAUC: 0.6604 | nDCG@5: 0.5326 | Primary: 0.5965 | Time: 4.58s
Epoch  2/20 | Train Tot: 0.5343 (Long: 0.5094, Like: 0.0830) | Valid GAUC: 0.6680 | nDCG@5: 0.5360 | Primary: 0.6020 | Time: 5.69s
Epoch  3/20 | Train Tot: 0.5232 (Long: 0.5011, Like: 0.0738) | Valid GAUC: 0.6696 | nDCG@5: 0.5369 | Primary: 0.6033 | Time: 5.51s
Epoch  4/20 | Train Tot: 0.5177 (Long: 0.4985, Like: 0.0637) | Valid GAUC: 0.6704 | nDCG@5: 0.5371 | Primary: 0.6038 | Time: 5.52s
Epoch  5/20 | Train Tot: 0.5143 (Long: 0.4968, Like: 0.0584) | Valid GAUC: 0.6705 | nDCG@5: 0.5377 | Primary: 0.6041 | Time: 6.42s
Epoch  6/20 | Train Tot: 0.5121 (Long: 0.4953, Like: 0.0562) | Valid GAUC: 0.6703 | nDCG@5: 0.5375 | Primary: 0.6039 | Time: 5.13s
Epoch  7/20 | Train Tot: 0.5102 (Long: 0.4937, Like: 0.0548) | Valid GAUC: 0.6707 | nDCG@5: 0.5372 | Primary: 0.6039 | Time: 5.24s
Epoch  8/20 | Train Tot: 0.5079 (Long: 0.4917, Like: 0.0538) | Valid GAUC: 0.6689 | nDCG@5: 0.5365 | Primary: 0.6027 | Time: 4.79s
Epoch  9/20 | Train Tot: 0.5052 (Long: 0.4893, Like: 0.0532) | Valid GAUC: 0.6671 | nDCG@5: 0.5355 | Primary: 0.6013 | Time: 4.43s
Early stopping triggered at epoch 9 (best epoch: 5)

Training completed in 47.32s.
Best Validation Epoch: 5
Best Validation GAUC:    0.6705
Best Validation nDCG@5:  0.5377
Best Validation Primary: 0.6041
```

## 4. Performance Metrics & Comparative Analysis

| Metric | Cycle 04 v2 Champion (Single-Task DCN-FM) | Variant v2 (Multi-Task Like Aux $\alpha=0.3$) | Delta vs Champion |
|---|---|---|---|
| **Validation GAUC** | 0.6715 | **0.6705** | -0.0010 |
| **Validation nDCG@5** | 0.5379 | **0.5377** | -0.0002 |
| **Primary Metric (Mean)** | 0.6047 | **0.6041** | **-0.0006** |
| **Optimal Epoch** | Epoch 6 | Epoch 5 | -1 |
| **Total Wall-Clock Time** | 48.56s | 47.32s | -1.24s |

### Scientific Diagnostic Takeaways:
1. **Slight Negative Transfer**: While `is_like` is a clean explicit engagement signal, its correlation with passive long dwell time is partial. Content optimized for high instant like rates (e.g., short punchy clips) differs from content driving high completion / long views on longer videos. Forcing the shared $V$ and $W_c$ representation to balance both objectives introduces a slight gradient conflict (-0.0006 Primary).
2. **Convergence Acceleration**: Auxiliary gradient signals accelerated convergence, reaching the validation optimum at Epoch 5 (Primary 0.6041) before regularized overfitting began at Epoch 6.
3. **Verdict**: While multi-task auxiliary training with `is_like` stabilizes training loss cleanly, it does not surpass the single-task Log-Duration DCN-FM champion on `long_view` ranking.

## 5. Data Boundary & Leakage Audit
- **Authorized Files Accessed**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Training split)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Validation split)
  - `competition_data/data/user_features_pure.csv` (Demographic features)
  - `competition_data/data/video_features_basic_pure.csv` (Author mapping)
- **Strict Boundary Confirmation**:
  - No access to test or hidden datasets.
  - Duration bin edges fitted exclusively on the standard training partition (`[20220408, 20220421]`).
  - Feature vocabularies and UNK mappings built exclusively from training partition.
  - Validation labels strictly evaluated on out-of-time public validation set using official starter-kit evaluation script.

## 6. Document Statistics
- Character count: 7,323
- Word count: 950
- Line count: 91
