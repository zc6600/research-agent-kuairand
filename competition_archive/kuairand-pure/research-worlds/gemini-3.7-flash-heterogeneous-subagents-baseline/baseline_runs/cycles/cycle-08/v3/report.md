# Experiment Report: Round 08 - Variant v3

## 1. Candidate Overview & Hypothesis

- **Variant**: `v3`
- **Cycle**: `cycle-08`
- **Model Architecture**: 11-Field Explicit Cross Layer + Factorization Machine (DCN-FM, $D = 11 \times 16 = 176$)
- **Focus / Hypothesis**:
  User content consumption and engagement dynamics in short-video platforms vary significantly across recommendation channels/scenarios (represented by the `tab` attribute: e.g., main feed, discovery, profile, search, topic channels). When users navigate between different tabs (scenario transition), their immediate engagement intent and content tolerance shift depending on the previous interaction context.
  
  Variant v3 formulates a strictly causal **Last-Interacted Scenario / Tab Transition** feature (`last_tab`). For each user interaction, the platform state tracks the `tab` of the user's immediately preceding interaction (assigned `'UNK'` for a user's initial interaction). This categorical state is maintained chronologically across the timeline from training (4/08–4/21) into validation (4/22–4/28), ensuring zero temporal leakage.
  
  By incorporating `last_tab` as an explicit 11th field in the Log-Duration DCN-FM model ($D=176$), the explicit cross layer ($x_1 = x_0 \odot (x_0 W_c + b_c) + x_0$) and 2nd-order FM layer can learn expressive cross-features capturing scenario transitions $(\text{last\_tab} \to \text{tab})$ alongside item duration buckets and user demographic profiles.

- **Feature Field Composition (11 Fields)**:
  1. `user_id`: Categorical user identifier (26,211 distinct IDs including UNK)
  2. `video_id`: Categorical item identifier (7,539 distinct IDs including UNK)
  3. `author_id`: Categorical content creator identifier (6,483 distinct IDs including UNK)
  4. `tab`: Current recommendation scenario/tab (16 distinct IDs including UNK)
  5. `dur_bucket`: Logarithmic duration discretization $\ln(1 + \text{duration\_ms})$ into 20 uniform bins (10 occupied bins including UNK)
  6. `user_active_degree`: User activity level category (10 distinct IDs including UNK)
  7. `follow_user_num_range`: User following count range (9 distinct IDs including UNK)
  8. `fans_user_num_range`: User follower count range (10 distinct IDs including UNK)
  9. `friend_user_num_range`: User mutual friend count range (8 distinct IDs including UNK)
  10. `register_days_range`: User account tenure range (8 distinct IDs including UNK)
  11. `last_tab`: Causal last-interacted recommendation tab/scenario (17 distinct IDs including UNK)
  - **Total One-Hot Dimension**: 40,321

---

## 2. Experimental Setup & Execution

- **Target Project Root**: `/Users/frank/github_project/Good4AI-simplify-scientist-remote-run/research_agent/projects/gemini-3.7-flash-heterogeneous-subagents-2026-08-31`
- **Candidate Directory**: `baseline_runs/cycles/cycle-08/v3`
- **Exact Command Line Executed**:
  ```bash
  .venv/bin/python baseline_runs/cycles/cycle-08/v3/run_v3.py
  ```
- **Hyperparameters**:
  - Embedding dimension $k$: 16
  - Concatenated embedding dimension $D$: $11 \times 16 = 176$
  - Learning rate $\eta$: 0.001 (Adam optimizer, $\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$)
  - $L_2$ regularization weight $\lambda$: $1\times 10^{-6}$
  - Batch size: 8,192
  - Max epochs: 20
  - Early stopping patience: 4
  - Random seed: 0
  - Loss function: Binary Cross-Entropy on `long_view`

---

## 3. Training & Validation Progress

### Causal Sequential State Statistics
- Total standard training interactions (4/08–4/21): 1,141,112 rows
- Total public validation interactions (4/22–4/28): 124,909 rows
- Training initial interaction count (`last_tab == 'UNK'`): 26,210 (100% matching distinct training users)
- Validation cold-start user interaction count (`last_tab == 'UNK'`): 422 (users with no prior history in train)
- Out-of-order temporal inversions: 0 (verified strictly monotonic per user)

### Log Duration Discretization Parameters
- Training set $\ln(1 + \text{duration\_ms})$ range: $[0.0000, 13.9791]$
- Cutoffs (19 internal thresholds):
  `[0.6990, 1.3979, 2.0969, 2.7958, 3.4948, 4.1937, 4.8927, 5.5916, 6.2906, 6.9895, 7.6885, 8.3875, 9.0864, 9.7854, 10.4843, 11.1833, 11.8822, 12.5812, 13.2801]`

### Per-Epoch Training Log
| Epoch | Train Loss | Valid GAUC | Valid nDCG@5 | Primary Score | Epoch Time (s) |
|:-----:|:----------:|:----------:|:------------:|:-------------:|:--------------:|
| 1 | 0.5852 | 0.6634 | 0.5335 | 0.5985 | 12.82s |
| 2 | 0.5077 | 0.6691 | 0.5360 | 0.6026 | 8.88s |
| 3 | 0.5001 | 0.6701 | 0.5371 | 0.6036 | 10.87s |
| 4 | 0.4973 | 0.6702 | 0.5371 | 0.6036 | 8.46s |
| **5 (Best)** | **0.4949** | **0.6705** | **0.5375** | **0.6040** | **7.80s** |
| 6 | 0.4920 | 0.6693 | 0.5361 | 0.6027 | 7.98s |
| 7 | 0.4874 | 0.6677 | 0.5354 | 0.6015 | 6.87s |
| 8 | 0.4808 | 0.6623 | 0.5323 | 0.5973 | 5.73s |
| 9 | 0.4743 | 0.6557 | 0.5295 | 0.5926 | 5.43s |

*Early stopping triggered at Epoch 9 after 4 consecutive non-improving epochs past Epoch 5.*

---

## 4. Public Validation Metrics & Comparison

### Comparison vs Current Best Benchmark (Cycle 04 v2 Champion - Log-Duration DCN-FM)
| Metric | Cycle 04 v2 Champion (10-Field DCN-FM) | Cycle 08 v3 (11-Field Causal Last-Tab DCN-FM) | Delta ($\Delta$) | Status |
|:---|:---:|:---:|:---:|:---:|
| **Primary Score** | **0.6047** | **0.6040** | **-0.0007** | Competitive (-0.12%) |
| **GAUC** | **0.6715** | **0.6705** | **-0.0010** | Slight Drop (-0.15%) |
| **nDCG@5** | **0.5379** | **0.5375** | **-0.0004** | Slight Drop (-0.07%) |
| Best Epoch | 5 | 5 | 0 | Identical Convergence |
| Number of Fields | 10 | 11 | +1 | Tab Transition Added |
| Cross Dim ($D$) | 160 | 176 | +16 | Expanded Cross Layer |
| Total Dimension | 40,304 | 40,321 | +17 | Minimal Param Overhead |

---

## 5. Execution Time & System Performance
- **Data Ingestion & Causal Tracking**: 7.06s
- **Feature Vocabulary & Encoding**: 15.34s
- **Training Time (9 epochs)**: 74.85s (~8.32s / epoch)
- **Total Wall-Clock Time**: 97.25s

---

## 6. Technical Insights & Analytical Findings

1. **Impact of Causal Tab Transition**: Adding the 1-step previous tab (`last_tab`) as a categorical context field achieves a solid validation Primary Score of **0.6040** (GAUC: 0.6705, nDCG@5: 0.5375), demonstrating high competitive quality close to the champion (0.6047).
2. **Channel Switching Sparsity**: In KuaiRand-Pure, users predominantly browse within dominant tabs (tab 0 and tab 1) for extended runs, making the transition signal $(\text{last\_tab} \to \text{tab})$ predominantly identity-dominated. The additional parameter space ($D=176$ vs $160$) slightly increases cross-layer dispersion without introducing sufficient variance over the static `tab` field alone.
3. **Strict Causal State Tracking**: The sequential state pipeline successfully maintains user interaction histories across time boundaries with zero leakage, proving a clean foundation for sequential and multi-step state models.

---

## 7. Data Boundary & Leakage Audit

- **Strict KuaiRand-Pure Boundary**: Fully verified and compliant.
- **Allowed Data Files Used**:
  - `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Train: 1,141,112 rows)
  - `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Valid: 124,909 rows)
  - `competition_data/data/user_features_pure.csv` (Demographic side features)
  - `competition_data/data/video_features_basic_pure.csv` (Item-author mapping)
- **Leakage Prevention**:
  - `last_tab` was computed sequentially per user strictly using past timestamped events ($t_{\text{prev}} < t_{\text{curr}}$).
  - Categorical vocabularies and logarithmic duration cutoffs were fitted exclusively on the standard training partition (4/08–4/21).
  - Out-of-time evaluation on `log_public_4_22_to_4_28_pure.csv` was executed with official `starter_kit/evaluate.py` semantics.
  - No access to test or unauthorized data sources.

---

## 8. Report Statistics
- **Character Count**: 8015
- **Whitespace-delimited Word Count**: 1092
- **Line Count**: 133
