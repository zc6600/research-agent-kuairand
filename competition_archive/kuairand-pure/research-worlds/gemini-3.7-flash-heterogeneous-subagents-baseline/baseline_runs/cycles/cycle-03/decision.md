# Cycle 03 Decision

## 1. Selected Variant & Checkpoint Promotion
**Selected Candidate**: `variant-v3` (DCN-FM: Explicit Cross-Network Layer + Factorization Machine)
- **Previous Control (Cycle 01 v2)**: 10-field FM -> GAUC 0.6677, nDCG@5 0.5363, Primary 0.6020
- **Selected Candidate Metrics**: GAUC 0.6705, nDCG@5 0.5377, Primary 0.6041
- **Deltas vs Previous Best**: $\Delta$ Primary = +0.0021, $\Delta$ GAUC = +0.0028, $\Delta$ nDCG@5 = +0.0014
- **Delta vs Official Baseline Control (0.6015)**: $\Delta$ Primary = +0.0026

## 2. Integrated Model Specification (New Champion)
- **Feature Set**: 10 categorical fields (40,305 vocab size, embedding rank =16$, concatenated embedding dimension  = 160$):
  `user_id`, `video_id`, `author_id`, `tab`, `dur_bucket`, `user_active_degree`, `follow_user_num_range`, `fans_user_num_range`, `friend_user_num_range`, `register_days_range`.
- **Model Architecture (DCN-FM)**:
  - 1st-order Linear:  + \sum_i W_{x_i}$
  - 2nd-order FM Dot-Product: $\frac{1}{2} ((\sum_i e_i)^2 - \sum_i e_i^2)$
  - Explicit Cross Layer:  = x_0 \odot (x_0 W_c + b_c) + x_0$ where  \in \mathbb{R}^{160 \times 160}$, projected via  \in \mathbb{R}^{160}$ to output logit.
  - Total Parameters: 710,946.
- **Optimization**: Adam (lr=0.001, batch=8192, L2=^{-6}$, max_epochs=20, patience=4).

## 3. Comparative Summary of Candidates
| Candidate | Architecture Paradigm | Params | Valid GAUC | Valid nDCG@5 | Valid Primary | Delta vs Previous Best | Verdict |
|---|---|---|---|---|---|---|---|
| Control (Cycle 01 v2) | Standard FM (10 fields) | 685,186 | 0.6677 | 0.5363 | 0.6020 | +0.0000 | Baseline |
| Variant v1 | DeepFM (FM + MLP [64, 32]) | 697,603 | 0.6703 | 0.5375 | 0.6039 | +0.0019 | Strong Candidate |
| Variant v2 | Wide & Deep (MLP [128, 64]) | 714,115 | 0.6699 | 0.5372 | 0.6036 | +0.0016 | Strong Candidate |
| **Variant v3** | **DCN-FM (Explicit Cross Layer)** | **710,946** | **0.6705** | **0.5377** | **0.6041** | **+0.0021** | **ADOPTED (New Champion)** |

## 4. Scientific Rationale & Analysis
- Explicit polynomial feature crossing via DCN allows the model to learn asymmetric, multiplicative feature interactions directly across all 160 embedding dimensions without the gradient attenuation or hyperparameter sensitivity of deep MLPs.
- All candidates strictly satisfied data boundary and zero-leakage constraints.

## 5. Next Hypothesis for Cycle 04
With the DCN-FM architecture establishing a new performance record (Primary 0.6041), investigate **continuous duration modeling and non-linear bucketing transformations**. Instead of uniform 10-quantile binning, explore fine-grained 30-quantile duration binning, logarithmic duration encoding, and video duration-to-playtime ratio features.
