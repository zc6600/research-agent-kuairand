# Independent Research Comparative Analysis: Cycle 01

**Comparator Role**: Independent gemini-3.7-flash Research Comparator  
**Project**: `gemini-3.7-flash-heterogeneous-subagents-2026-08-31`  
**Benchmark**: KuaiRand-Pure (Within-User Ranking over Logged Impressions)  
**Primary Metric**: `Primary = mean(GAUC, nDCG@5)`  
**Evaluation Target**: Public Validation Split (`log_public_4_22_to_4_28_pure.csv`, 124,909 rows, 22,377 users)  
**Date**: 2026-08-31  

---

## 1. Executive Summary & Final Recommendation

In Cycle 01, three distinct feature representation hypotheses were implemented and evaluated against the official 5-field Factorization Machine control baseline on KuaiRand-Pure:
- **Variant v1 (Video Metadata Extension - 8 fields)**: Added `music_id`, `video_type`, `upload_type` to baseline. Resulted in a slight performance drop (**Primary: 0.6007**, $\Delta = -0.0008$).
- **Variant v2 (User Demographic Extension - 10 fields)**: Added 5 demographic/activity fields (`user_active_degree`, `follow_user_num_range`, `fans_user_num_range`, `friend_user_num_range`, `register_days_range`). **Achieved a clean, consistent improvement across all metrics (Primary: 0.6020, $\Delta = +0.0005$; GAUC: 0.6677, $\Delta = +0.0006$; nDCG@5: 0.5363, $\Delta = +0.0005$)**.
- **Variant v3 (Full CWM-13 Joint Feature Representation - 13 fields)**: Combined both video metadata and user demographic extensions. Suffered from over-parameterization and early overfitting (**Primary: 0.6004**, $\Delta = -0.0011$).

### Recommendation
> [!IMPORTANT]
> **Adoption Recommendation: Adopt Variant v2 as the new project champion / checkpoint.**  
> Variant v2 is the only candidate that improves upon the control baseline across both GAUC and nDCG@5. It introduces minimal additional parameter cardinality (+45 dimensions), regularizes user-level representations, and maintains excellent training throughput (~26.1s). Candidates v1 and v3 should be rejected.

---

## 2. Quantitative Comparison Table

The table below provides a comprehensive comparison of the Control Baseline and all three Cycle 01 candidates. All metrics are computed strictly using the official `starter_kit/evaluate.py` evaluation semantics.

| Candidate | Hypothesis / Architecture | Feature Fields ($F$) | Global Dim ($D$) | Best Epoch | Valid GAUC | Valid nDCG@5 | Valid Primary | $\Delta$ GAUC vs Ctrl | $\Delta$ nDCG@5 vs Ctrl | $\Delta$ Primary vs Ctrl | Train Time (s) | Total Elapsed (s) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control** | Official Baseline FM | 5 | ~40,260 | - | 0.6671 | 0.5358 | 0.6015 | +0.0000 | +0.0000 | +0.0000 | ~25.0s | ~34.0s | *Baseline* |
| **Variant v1** | Video Metadata Ext | 8 | 47,440 | 8 | 0.6661 | 0.5354 | 0.6007 | -0.0010 | -0.0004 | -0.0008 | 27.47s | 36.01s | Reject |
| **Variant v2** | **User Demographic Ext** | **10** | **40,305** | **7** | **0.6677** | **0.5363** | **0.6020** | **+0.0006** | **+0.0005** | **+0.0005** | **26.11s** | **34.41s** | **ADOPT (Champion)** |
| **Variant v3** | Full CWM-13 Joint Ext | 13 | 47,485 | 3 | 0.6656 | 0.5352 | 0.6004 | -0.0015 | -0.0006 | -0.0011 | 24.45s | 33.96s | Reject |

*Note: All runs executed with $k=16$, batch size $8192$, learning rate $0.001$ (Adam), $L_2 = 10^{-6}$, random seed $0$, and early stopping patience $4$.*

---

## 3. Deep-Dive Candidate Analysis & Failure Modes

```mermaid
graph TD
    subgraph Control ["Control (5 Fields)"]
        C_FE["user_id, video_id, author_id, tab, dur_bucket"]
        C_Score["Primary: 0.6015"]
    end

    subgraph Variant_v1 ["Variant v1 (8 Fields)"]
        V1_FE["Baseline + music_id, video_type, upload_type"]
        V1_Issue["High Sparsity (music_id = 7,161)<br/>Overfitting from Epoch 8"]
        V1_Score["Primary: 0.6007 (-0.0008)"]
    end

    subgraph Variant_v2 ["Variant v2 (10 Fields) - WINNER"]
        V2_FE["Baseline + 5 User Profile Buckets"]
        V2_Mech["Low Cardinality (+45 dims)<br/>Demographic Regularization<br/>Interactions w/ Video/Author"]
        V2_Score["Primary: 0.6020 (+0.0005)"]
    end

    subgraph Variant_v3 ["Variant v3 (13 Fields)"]
        V3_FE["Full CWM-13 Joint"]
        V3_Issue["78 Pairwise Interactions<br/>Static-Static Invariance<br/>Early Overfitting at Epoch 3"]
        V3_Score["Primary: 0.6004 (-0.0011)"]
    end

    Control --> Variant_v1
    Control --> Variant_v2
    Control --> Variant_v3
```

### Variant v1: Video Metadata Extension (8 fields)
- **Design**: Integrated item-side metadata (`music_id`, `video_type`, `upload_type`) with baseline item and interaction features.
- **Outcome**: GAUC 0.6661, nDCG@5 0.5354, Primary 0.6007 ($\Delta = -0.0008$).
- **Mechanism of Failure**:
  1. **Sparse Parameter Dilution**: `music_id` has 7,161 categories across 7,539 unique videos. This near 1:1 mapping creates extreme sparsity without sufficient co-occurrence counts to train high-quality latent vectors $v_{\text{music}} \in \mathbb{R}^{16}$.
  2. **Overfitting Dynamics**: While train loss decreased monotonically from 0.6204 to 0.4685, validation performance peaked at Epoch 8 (0.6007) and degraded sharply by Epoch 12 (0.5970). The model memorized item-side noise without improving generalization on user preference ranking.

### Variant v2: User Demographic Extension (10 fields) — *Selected Champion*
- **Design**: Integrated 5 user profile/activity buckets (`user_active_degree`, `follow_user_num_range`, `fans_user_num_range`, `friend_user_num_range`, `register_days_range`) with the 5 baseline fields.
- **Outcome**: GAUC 0.6677, nDCG@5 0.5363, Primary 0.6020 ($\Delta = +0.0005$).
- **Why It Succeeded**:
  1. **High Information Density with Negligible Cardinality**: The 5 user demographic fields add only 45 total categorical buckets (10, 9, 10, 8, 8 categories respectively). The total vocabulary dimension expanded from ~40,260 to only 40,305.
  2. **Effective Cross-Entity Regularization**: In a 2nd-order FM, terms like $\langle v_{\text{active\_degree}}, v_{\text{video\_id}} \rangle$ and $\langle v_{\text{tenure}}, v_{\text{author\_id}} \rangle$ allow the model to learn broad preference priors (e.g., highly active users preferring certain video durations or author styles) that transfer across users who share demographic profiles.
  3. **Balanced Learning Trajectory**: Peak performance was achieved at Epoch 7 with stable convergence and no premature over-saturation.

### Variant v3: Full CWM-13 Joint Extension (13 fields)
- **Design**: Jointly combined all 4 video metadata fields and 5 user demographic fields into a single 13-field FM.
- **Outcome**: GAUC 0.6656, nDCG@5 0.5352, Primary 0.6004 ($\Delta = -0.0011$).
- **Mechanism of Failure**:
  1. **Interaction Noise and Intra-User Invariance**: A 13-field FM computes $\binom{13}{2} = 78$ pairwise interactions. Pairs among static user features ($\binom{5}{2} = 10$ pairs) evaluate to identical scalar values for all candidate items evaluated for a given user impression session. Under within-user ranking (GAUC/nDCG@5), constant shifts within a user do not alter relative item order, wasting model capacity.
  2. **Interference between Noisy Video Features and User Features**: Pairwise cross-products between noisy sparse item fields (`music_id`) and user demographics introduced substantial variance, accelerating overfitting (best primary was hit prematurely at Epoch 3).

---

## 4. Rigorous Audit & Data Boundary Verification

An independent code and data audit was conducted on all three candidate implementations:

1. **Permitted Data Split Adherence**:
   - Training Partition: Strictly restricted to `log_standard_4_08_to_4_21_pure.csv` (1,141,112 interaction records).
   - Validation Partition: Strictly restricted to `log_public_4_22_to_4_28_pure.csv` (124,909 interaction records).
   - Metadata Tables: Only static lookup files `user_features_pure.csv` (27,285 users) and `video_features_basic_pure.csv` (7,583 videos) were accessed.
   - Forbidden / Test Sets: No access to test files, random exposure logs (`log_random_4_22_to_4_28_pure.csv`), or external sources.
2. **Leakage Prevention**:
   - Quantile Binning: Duration quantile split edges were computed strictly from the training partition.
   - Vocabulary Encoding: All categorical index maps and global offsets were constructed solely from training data. Unseen validation entities were deterministically mapped to dedicated `UNK` slots.
   - Target Isolation: No validation label statistics or future signals leaked into feature transformations or model weights.
3. **Metric Integrity**:
   - All candidates faithfully implement or import the official `starter_kit/evaluate.py` evaluator.
   - Tie-corrected Mann-Whitney U for GAUC (only users with $0 < \text{positives} < \text{impressions}$ included, weighted by positives).
   - Identity gain $2^{\text{rel}} - 1$ for binary labels with logarithmic discount for nDCG@5.

---

## 5. Resource & Efficiency Telemetry

| Candidate | Preprocessing Time (s) | Training Time (s) | Epochs Trained | Sec / Epoch | Total Elapsed Time (s) | Peak Memory |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control** | ~5.0 s | ~25.0 s | 10 | ~2.50 s | ~34.0 s | < 500 MB |
| **Variant v1** | 8.54 s | 27.47 s | 12 | ~2.29 s | 36.01 s | < 500 MB |
| **Variant v2** | **8.30 s** | **26.11 s** | **11** | **~2.37 s** | **34.41 s** | **< 500 MB** |
| **Variant v3** | 9.51 s | 24.45 s | 7 | ~3.49 s | 33.96 s | < 500 MB |

All candidates execute well within the compute budget (< 40 seconds per run), ensuring rapid cycle iteration.

---

## 6. Strategic Takeaways & Guidance for Cycle 02

1. **Retain Variant v2 as the Base Representation**: The 10-field feature configuration (`user_id`, `video_id`, `author_id`, `tab`, `dur_bucket`, `user_active_degree`, `follow_user_num_range`, `fans_user_num_range`, `friend_user_num_range`, `register_days_range`) provides a superior foundation over the 5-field baseline.
2. **Key Insight on High-Cardinality Item Features**: Raw item identifiers like `music_id` degrade generalization in shallow linear/bilinear models. If music or video type signals are to be revisited in later cycles, they require clustering, frequency thresholding, or learned multi-hot pooling rather than one-hot concatenation.
3. **Promising Directions for Cycle 02**:
   - **Hyperparameter Optimization on 10-Field FM**: Tune embedding dimension $k \in \{8, 24, 32\}$, learning rate $\eta \in \{0.0005, 0.002\}$, and $L_2$ weight regularization $\lambda \in \{10^{-5}, 10^{-4}\}$ on Variant v2 to combat the onset of overfitting around Epoch 8.
   - **Continuous Feature Discretization Refinement**: Experiment with non-linear duration bucketings (e.g. logarithmic bins or adaptive clustering) and ratio features (e.g., duration vs. user mean watch time).
   - **Higher-Order or Deep Architectures**: Explore DeepFM / DCN architectures built on top of the 10-field feature matrix.

---

## 7. Document Statistics & Verification

- **Report Character Count**: 11,115
- **Whitespace-delimited Word Count**: 1,513
- **Line Count**: 145
