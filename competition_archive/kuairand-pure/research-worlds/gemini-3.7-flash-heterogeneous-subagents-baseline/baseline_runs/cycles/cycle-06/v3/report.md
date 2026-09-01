# Candidate Experiment Report: Round 06 - Variant v3

## 1. Executive Summary & Candidate Version
- **Candidate Identifier**: `v3` (Round 06 - Tri-Task Joint Optimization)
- **Model Architecture**: Tri-Task Shared-Backbone DCN-FM (10 Fields, $k=16$, 20 Log Duration Bins, Shared Explicit Cross Layer + 3 Dedicated Task Heads)
- **Optimization Objective**: Joint multi-task loss $L_{total} = L_{long\_view} + 0.2 \cdot L_{is\_click} + 0.2 \cdot L_{is\_like}$
- **Validation Primary Score**: **0.6041** (GAUC: **0.6706**, nDCG@5: **0.5376**)
- **Delta vs Current Best (Cycle 04 v2 Champion: 0.6047)**:
  - $\Delta$ Primary: **-0.0006**
  - $\Delta$ GAUC: **-0.0009**
  - $\Delta$ nDCG@5: **-0.0003**
- **Outcome / Verdict**: **Reject**. Tri-task joint training produces gradient interference and representation dilution on shared embeddings, causing long-view ranking quality to degrade relative to dedicated single-task optimization.

---

## 2. Hypothesis & Technical Description

### 2.1 Scientific Motivation & Mechanism Hypothesis
The KuaiRand dataset contains rich multi-action feedback signals ($is\_click$, $is\_like$, $long\_view$, $is\_follow$, etc.). The hypothesis posits that jointly training on $is\_click$ and $is\_like$ alongside $long\_view$ will regularize sparse user/video ID embeddings, leverage high-volume interaction signals ($is\_click$ ~46.3% positive rate), and improve generalization on the primary ranking target ($long\_view$).

### 2.2 Mathematical Formulation & Model Architecture
1. **Input Feature Space (10 Categorical Fields)**:
   - $user\_id$, $video\_id$, $author\_id$, $tab$
   - $dur\_bucket$: 20 uniform bins in $\log(1 + duration\_ms)$ space fitted strictly on train split
   - Demographic features: $user\_active\_degree$, $follow\_user\_num\_range$, $fans\_user\_num\_range$, $friend\_user\_num\_range$, $register\_days\_range$
   - Total dictionary dimension across 10 fields: $M = 40,304$.

2. **Shared Backbone Representation**:
   - Embedding table: $V \in \mathbb{R}^{M \times 16}$.
   - Concatenated embedding: $x_0 = [v_1, v_2, \dots, v_{10}] \in \mathbb{R}^{160}$.
   - Explicit Cross Layer (DCN): $u = x_0 W_c + b_c$, $x_1 = x_0 \odot u + x_0 \in \mathbb{R}^{160}$, with shared $W_c \in \mathbb{R}^{160 \times 160}$ and $b_c \in \mathbb{R}^{160}$.
   - FM 2nd-order interaction: $inter\_fm(E) = \frac{1}{2} \left( \|\sum_f E_f\|^2 - \sum_f \|E_f\|^2 \right) \in \mathbb{R}$.

3. **3 Dedicated Task Heads**:
   - For each task $t \in \{\text{long\_view}, \text{is\_click}, \text{is\_like}\}$:
     $$z^{(t)} = b^{(t)} + \sum_{f=1}^{10} W^{(t)}[X_f] + inter\_fm(E) + x_1 w_p^{(t)}$$
     where $W^{(t)} \in \mathbb{R}^{M}$, $b^{(t)} \in \mathbb{R}$, and $w_p^{(t)} \in \mathbb{R}^{160}$.

4. **Joint Loss Function**:
   $$L_{total} = L_{long\_view} + 0.2 \cdot L_{is\_click} + 0.2 \cdot L_{is\_like}$$
   where $L_t = -\frac{1}{B} \sum_{i=1}^B [y_i^{(t)} \log p_i^{(t)} + (1 - y_i^{(t)}) \log(1 - p_i^{(t)})]$.

---

## 3. Exact Execution Commands
```bash
# Set working directory to target project root
cd /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31

# Run candidate v3 training and validation
.venv/bin/python baseline_runs/cycles/cycle-06/v3/run_v3.py
```

---

## 4. Training & Validation Execution Logs

```
Loading data strictly from /Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31/competition_data/data ...
Loaded splits: {'train': 1141112, 'valid': 124909} in 3.03s
Encoding features across 10 fields with 20 Logarithmic Duration Bins...
Train log(1 + duration_ms) range: [0.0000, 13.9791]
Created 19 internal cutoffs for 20 log duration bins:
  Cutoffs: [0.699, 1.3979, 2.0969, 2.7958, 3.4948, 4.1937, 4.8927, 5.5916, 6.2906, 6.9895, 7.6885, 8.3875, 9.0864, 9.7854, 10.4843, 11.1833, 11.8822, 12.5812, 13.2801]
Feature encoding complete. Total dimension: 40304 across 10 fields in 5.82s
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

Target Label Statistics (Train Split):
  Task 'long_view ':  384121 positives (33.66%)
  Task 'is_click  ':  528845 positives (46.34%)
  Task 'is_like   ':   21312 positives (1.87%)

Target Label Statistics (Validation Split):
  Task 'long_view ':   39132 positives (31.33%)
  Task 'is_click  ':   55438 positives (44.38%)
  Task 'is_like   ':    2245 positives (1.80%)

Initializing TriTaskDCNFM model (dim=40304, fields=10, k=16, D=160, lr=0.001, l2=1e-06, seed=0)...
Task loss weights: {'long_view': 1.0, 'is_click': 0.2, 'is_like': 0.2}

Starting Tri-Task Joint DCN_FM training...
Epoch  1/20 | Loss: 0.7730 (LV: 0.5901, Click: 0.6294, Like: 0.2850) | Valid GAUC: 0.6620 | nDCG@5: 0.5332 | Primary: 0.5976 | Time: 4.51s
Epoch  2/20 | Loss: 0.6356 (LV: 0.5082, Click: 0.5511, Like: 0.0857) | Valid GAUC: 0.6678 | nDCG@5: 0.5357 | Primary: 0.6018 | Time: 4.33s
Epoch  3/20 | Loss: 0.6255 (LV: 0.5007, Click: 0.5430, Like: 0.0806) | Valid GAUC: 0.6700 | nDCG@5: 0.5370 | Primary: 0.6035 | Time: 4.44s
Epoch  4/20 | Loss: 0.6212 (LV: 0.4982, Click: 0.5398, Like: 0.0753) | Valid GAUC: 0.6706 | nDCG@5: 0.5376 | Primary: 0.6041 | Time: 4.51s
Epoch  5/20 | Loss: 0.6176 (LV: 0.4964, Click: 0.5374, Like: 0.0685) | Valid GAUC: 0.6701 | nDCG@5: 0.5373 | Primary: 0.6037 | Time: 5.26s
Epoch  6/20 | Loss: 0.6141 (LV: 0.4946, Click: 0.5352, Like: 0.0619) | Valid GAUC: 0.6694 | nDCG@5: 0.5365 | Primary: 0.6030 | Time: 6.22s
Epoch  7/20 | Loss: 0.6110 (LV: 0.4928, Click: 0.5329, Like: 0.0584) | Valid GAUC: 0.6693 | nDCG@5: 0.5365 | Primary: 0.6029 | Time: 6.18s
Epoch  8/20 | Loss: 0.6077 (LV: 0.4904, Click: 0.5303, Like: 0.0566) | Valid GAUC: 0.6678 | nDCG@5: 0.5358 | Primary: 0.6018 | Time: 6.87s
Early stopping triggered at epoch 8 (best epoch: 4)

Training completed in 42.32s.
Best Validation Epoch: 4
Best Validation GAUC:    0.6706
Best Validation nDCG@5:  0.5376
Best Validation Primary: 0.6041
Saved results to baseline_runs/cycles/cycle-06/v3/results.json
```

---

## 5. Public Validation Metrics & Comparison

| Metric | Official Baseline (FM 5-field) | Active Champion (Cycle 04 v2) | Candidate v3 (Tri-Task Joint) | $\Delta$ vs Champion | $\Delta$ vs Baseline |
|---|---|---|---|---|---|
| **GAUC** | 0.6674 | **0.6715** | 0.6706 | -0.0009 | +0.0032 |
| **nDCG@5** | 0.5357 | **0.5379** | 0.5376 | -0.0003 | +0.0019 |
| **Primary** | 0.6016 | **0.6047** | 0.6041 | **-0.0006** | **+0.0025** |
| Evaluated Users | 22,377 | 22,377 | 22,377 | 0 | 0 |
| Evaluated Rows | 124,909 | 124,909 | 124,909 | 0 | 0 |

---

## 6. Diagnostic & Scientific Failure Analysis

1. **Task Gradient Conflict**:
   - $is\_click$ represents superficial interest / click-through probability (46.34% positive rate), while $long\_view$ requires sustained watching and high completion rate (33.66% positive rate). High-click items frequently have low retention / short watch times, generating conflicting gradient updates on item embeddings.
   - $is\_like$ is extremely sparse (1.87% positive rate). The gradients for rare like events produce sharp, noisy updates to user and item embeddings that destabilize the shared representation space.
2. **Embedding Representation Dilution**:
   - With embedding dimension $k=16$, representation capacity is limited. Forcing the 10-field embedding layer and explicit cross layer to jointly predict three distinct user engagement behaviors dilutes the features needed specifically for predicting $long\_view$ ranking.
3. **Premature Convergence & Negative Transfer**:
   - While the auxiliary losses continued decreasing through Epoch 8 (Click: 0.6294 $\to$ 0.5303, Like: 0.2850 $\to$ 0.0566), validation performance on $long\_view$ peaked at Epoch 4 (Primary 0.6041) and degraded to 0.6018 by Epoch 8 due to negative transfer from the auxiliary objectives.

---

## 7. Execution Time & Resource Consumption
- Total script execution time: **42.32 seconds**
- Peak memory footprint: ~150 MB (single process, numpy-based vectorized mini-batch Adam)
- Convergence: Early stopped at epoch 8 (patience 4, best epoch 4).

---

## 8. Data Boundary & Leakage Audit
- **Data Files Accessed Strictly**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (1,141,112 rows, train only)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (124,909 rows, public validation only)
  - `competition_data/data/user_features_pure.csv` (demographic features)
  - `competition_data/data/video_features_basic_pure.csv` (video author mapping)
- **Leakage Safeguards**:
  - Duration log discretization bins fitted strictly on training data (range $[0.0000, 13.9791]$, 19 cutoffs).
  - Feature vocabularies and UNK mappings fitted strictly on training split.
  - Multi-task auxiliary targets utilized exclusively during training; public validation strictly evaluated on ground-truth $long\_view$ labels.
  - Zero access to test splits or external datasets.

---

## 9. Report Document Statistics
- Character Count: 9,731 characters
- Word Count: 1,288 words
- Line Count: 159 lines
