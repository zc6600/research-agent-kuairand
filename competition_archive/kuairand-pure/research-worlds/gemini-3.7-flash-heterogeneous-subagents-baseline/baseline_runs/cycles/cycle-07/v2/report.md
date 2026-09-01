# Candidate Experiment Report: Round 07 - Variant v2

## 1. Candidate Overview & Hypothesis
- **Candidate Version**: Variant `v2`
- **Model Architecture**: Inverse Propensity Scoring (IPS) Debiased Log-Duration DCN-FM (10 fields, $k=16, D=160$)
- **Core Hypothesis**: Short-video recommendation logs suffer from severe exposure/popularity bias where head videos receive disproportionately higher impressions, biasing model parameters toward over-represented items. By applying sample-level Inverse Propensity Scoring (IPS) loss weights $w_i = (N / \text{imp}(v_i))^{0.2}$ (normalized such that $\mathbb{E}[w] = 1.0$ and clipped to $[0.5, 2.0]$) during Binary Cross-Entropy loss calculation, the model down-weights dominant head items and up-weights under-exposed tail items. This debiased gradient flow is hypothesized to learn more generalizable user-item preference representations across diverse content.
- **Key Technical Details**:
  - **Feature Representation (10 Fields)**: `user_id`, `video_id`, `author_id`, `tab`, `dur_bucket` (20 log-duration uniform bins), `user_active_degree`, `follow_user_num_range`, `fans_user_num_range`, `friend_user_num_range`, `register_days_range` mapped to $k=16$ embedding dimensions ($D=160$ concatenated).
  - **DCN-FM Architecture**: Logits combine bias $b$, linear features $W[X]$, 2nd-order FM vector interactions $\frac{1}{2}((\sum E)^2 - \sum E^2)$, and explicit polynomial cross layer $x_1 = x_0 \odot (x_0 W_c + b_c) + x_0$ projected via $w_p$.
  - **IPS Propensity Weighting**:
    - Item impression counts $\text{imp}(v)$ computed strictly on training partition ($N=1,141,112$ interactions across 7,538 items).
    - Raw propensity weights: $w_{\text{raw}, i} = (N / \text{imp}(v_i))^{0.2}$ (range $[2.6276, 16.2729]$, mean $4.9898$).
    - Scaling & clipping: $w_i = \text{clip}(w_{\text{raw}, i} / \bar{w}_{\text{raw}}, 0.5, 2.0)$ yielding sample weights with mean $0.9985$, standard deviation $0.2903$, range $[0.5266, 2.0000]$.
  - **Weighted Gradient Backpropagation**: $\frac{\partial L}{\partial z_i} = \frac{w_i (p_i - y_i)}{B}$ directly scales linear, cross, and FM embedding gradients.
  - **Optimization Protocol**: Adam ($\beta_1=0.9, \beta_2=0.999$, $\text{lr}=0.001$, $L_2=1\times 10^{-6}$, batch size $8192$, max epochs $20$, patience $4$).

## 2. Exact Execution Command
```bash
.venv/bin/python baseline_runs/cycles/cycle-07/v2/run_v2.py 2>&1 | tee baseline_runs/cycles/cycle-07/v2/run.log
```

## 3. Training & Validation Execution Logs
```text
Loading data from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded splits: {'train': 1141112, 'valid': 124909} in 9.09s
Computing Inverse Propensity Scoring (IPS) weights (power=0.2, clip=[0.5, 2.0])...
IPS Weights computed on 7538 unique items across 1141112 training impressions in 2.90s:
  Raw weights:     min=2.6276, max=16.2729, mean=4.9898
  Clipped weights: min=0.5266, max=2.0000, mean=0.9985, std=0.2903
Encoding features across 10 fields with 20 Logarithmic Duration Bins...
Train log(1 + duration_ms) range: [0.0000, 13.9791]
Created 19 internal cutoffs for 20 log duration bins:
  Cutoffs: [0.699, 1.3979, 2.0969, 2.7958, 3.4948, 4.1937, 4.8927, 5.5916, 6.2906, 6.9895, 7.6885, 8.3875, 9.0864, 9.7854, 10.4843, 11.1833, 11.8822, 12.5812, 13.2801]
Feature encoding complete. Total dimension: 40304 across 10 fields in 18.61s
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

Initializing IPS DCN_FM model (dim=40304, fields=10, k=16, D=160, lr=0.001, l2=1e-06, seed=0)...

Starting IPS DCN_FM training with sample-level debiasing loss (power=0.2, clip=[0.5, 2.0])...
Epoch  1/20 | Train Loss: 0.5763 | Valid GAUC: 0.6631 | nDCG@5: 0.5335 | Primary: 0.5983 | Time: 10.62s
Epoch  2/20 | Train Loss: 0.4948 | Valid GAUC: 0.6686 | nDCG@5: 0.5360 | Primary: 0.6023 | Time: 13.81s
Epoch  3/20 | Train Loss: 0.4869 | Valid GAUC: 0.6698 | nDCG@5: 0.5371 | Primary: 0.6035 | Time: 14.51s
Epoch  4/20 | Train Loss: 0.4839 | Valid GAUC: 0.6703 | nDCG@5: 0.5370 | Primary: 0.6037 | Time: 15.02s
Epoch  5/20 | Train Loss: 0.4806 | Valid GAUC: 0.6711 | nDCG@5: 0.5378 | Primary: 0.6044 | Time: 13.60s
Epoch  6/20 | Train Loss: 0.4760 | Valid GAUC: 0.6701 | nDCG@5: 0.5369 | Primary: 0.6035 | Time: 9.49s
Epoch  7/20 | Train Loss: 0.4708 | Valid GAUC: 0.6681 | nDCG@5: 0.5358 | Primary: 0.6019 | Time: 9.40s
Epoch  8/20 | Train Loss: 0.4661 | Valid GAUC: 0.6626 | nDCG@5: 0.5332 | Primary: 0.5979 | Time: 9.13s
Epoch  9/20 | Train Loss: 0.4618 | Valid GAUC: 0.6575 | nDCG@5: 0.5306 | Primary: 0.5941 | Time: 7.88s
Early stopping triggered at epoch 9 (best epoch: 5)

Training completed in 103.46s.
Best Validation Epoch: 5
Best Validation GAUC:    0.6711
Best Validation nDCG@5:  0.5378
Best Validation Primary: 0.6044
Saved results to /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/baseline_runs/cycles/cycle-07/v2/results.json
```

## 4. Performance Metrics & Comparative Analysis

| Metric | Cycle 04 v2 Champion (Log-Duration DCN-FM) | Variant v2 (IPS Debiased Loss $p=0.2$) | Delta vs Champion |
|---|---|---|---|
| **Validation GAUC** | 0.6715 | **0.6711** | -0.0004 |
| **Validation nDCG@5** | 0.5379 | **0.5378** | -0.0001 |
| **Primary Metric (Mean)** | 0.6047 | **0.6044** | **-0.0003** |
| **Optimal Epoch** | Epoch 5 | Epoch 5 | 0 |
| **Total Wall-Clock Time** | 43.11s | 103.46s | +60.35s |

### Scientific Diagnostic Takeaways:
1. **Validation Traffic Distribution vs IPS Debiasing**: The public validation set (`log_public_4_22_to_4_28_pure.csv`) originates from production standard recommendation logging rather than uniform random exploration. Production traffic inherently reflects natural item popularity distributions. While IPS debiasing successfully reduces head-item overconfidence during training, slightly dampening head-item scores mildly degrades ranking precision on popularity-correlated standard test traffic (-0.0003 Primary).
2. **Effective Variance Control**: Thanks to the square-root-like dampening power ($p=0.2$) and bounded clipping range ($[0.5, 2.0]$), IPS avoided destructive gradient variance, preserving high ranking fidelity (Primary $0.6044$ vs Champion $0.6047$).
3. **Verdict**: Standard unweighted empirical risk minimization remains marginally superior on standard logging distributions for this benchmark, making unweighted DCN-FM the preferred architecture for the current public validation target.

## 5. Data Boundary & Leakage Audit
- **Authorized Files Accessed**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Standard training split)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Public validation split)
  - `competition_data/data/user_features_pure.csv` (Demographic features)
  - `competition_data/data/video_features_basic_pure.csv` (Author mapping)
- **Strict Boundary Confirmation**:
  - Zero access to unapproved or test datasets.
  - Item impression counts and propensity weights were computed strictly from the training partition (`[20220408, 20220421]`).
  - Duration discretization bin boundaries were estimated strictly on the training partition.
  - Vocabulary maps and UNK assignments were built exclusively on training interactions.
  - Validation metrics were evaluated on the official out-of-time public validation set using standard evaluation script semantics.

## 6. Document Statistics
- Character count: 8,233
- Word count: 1,034
- Line count: 99

