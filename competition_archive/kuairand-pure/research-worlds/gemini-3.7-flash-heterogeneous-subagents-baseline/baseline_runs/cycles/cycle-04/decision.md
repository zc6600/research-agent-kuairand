# Cycle 04 Decision

## 1. Selected Variant & Checkpoint Promotion
**Selected Candidate**: `variant-v2` (Logarithmic Duration Discretization in DCN-FM)
- **Previous Control (Cycle 03 v3)**: DCN-FM (10 fields, 10-quantile duration) -> GAUC 0.6705, nDCG@5 0.5377, Primary 0.6041
- **Selected Candidate Metrics**: GAUC 0.6715, nDCG@5 0.5379, Primary 0.6047
- **Deltas vs Previous Best**: $\Delta$ Primary = +0.0006, $\Delta$ GAUC = +0.0010, $\Delta$ nDCG@5 = +0.0002
- **Delta vs Official Baseline Control (0.6015)**: $\Delta$ Primary = +0.0032

## 2. Integrated Model Specification (New Champion)
- **Feature Set**: 10 fields (40,304 vocab size, =16$, =160$):
  `user_id`, `video_id`, `author_id`, `tab`, `log_dur_bucket` (20 uniform log-bins on $\ln(1 + \text{duration\_ms})$), `user_active_degree`, `follow_user_num_range`, `fans_user_num_range`, `friend_user_num_range`, `register_days_range`.
- **Model Architecture (Log-Duration DCN-FM)**:
  - 1st-order Linear:  + \sum_i W_{x_i}$
  - 2nd-order FM Dot-Product: $\frac{1}{2} ((\sum_i e_i)^2 - \sum_i e_i^2)$
  - Explicit Cross Layer:  = x_0 \odot (x_0 W_c + b_c) + x_0$ where  \in \mathbb{R}^{160 \times 160}$, projected via  \in \mathbb{R}^{160}$ to output logit.
  - Total Parameters: 710,930.
- **Optimization**: Adam (lr=0.001, batch=8192, L2=^{-6}$, max_epochs=20, patience=4).

## 3. Comparative Summary of Candidates
| Candidate | Description | Valid GAUC | Valid nDCG@5 | Valid Primary | Delta vs Previous Best | Verdict |
|---|---|---|---|---|---|---|
| Control (Cycle 03 v3) | DCN-FM (10-quantile dur) | 0.6705 | 0.5377 | 0.6041 | +0.0000 | Baseline |
| Variant v1 | DCN-FM (30-quantile dur) | 0.6707 | 0.5374 | 0.6041 | -0.00005 | Rejected (Tied) |
| **Variant v2** | **DCN-FM (20 log-duration bins)** | **0.6715** | **0.5379** | **0.6047** | **+0.0006** | **ADOPTED (New Champion)** |
| Variant v3 | DCN-FM (Dual 10-bin + 50-bin dur) | 0.6697 | 0.5370 | 0.6034 | -0.0007 | Rejected |

## 4. Scientific Rationale & Analysis
- Video durations in KuaiRand exhibit extreme heavy-tailed skewness. Frequency quantiles compress the long tail, whereas uniform log-scale discretization $\ln(1 + \text{duration\_ms})$ geometrically spaces duration bins, aligning with user psychological time perception and yielding significant ranking discrimination (+0.0010 GAUC).
- Clean data boundary compliance verified on all candidates.

## 5. Next Hypothesis for Cycle 05
Investigate **contextual & temporal dynamics**. Incorporate hour-of-day/time-bucket and day-of-week context from interaction timestamps (, Mon Aug 31 21:25:07 +08 2026) into the Champion DCN-FM model to test if user consumption habits vary significantly by time of day and weekday vs weekend.
