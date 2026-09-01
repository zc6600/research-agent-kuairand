# Cycle 01 Decision

## 1. Selected Variant
**Selected Candidate**: `variant-v2` (User Demographic Extension, 10 fields)
- **Previous Control**: Official Baseline FM (5 fields) -> GAUC 0.6671, nDCG@5 0.5358, Primary 0.6015
- **Selected Candidate Metrics**: GAUC 0.6677, nDCG@5 0.5363, Primary 0.6020
- **Deltas**: $\Delta$ Primary = +0.0005, $\Delta$ GAUC = +0.0006, $\Delta$ nDCG@5 = +0.0005

## 2. Integrated Changes & Model Specification
- **Feature Set**: 10 fields:
  1. `user_id`
  2. `video_id`
  3. `author_id`
  4. `tab`
  5. `dur_bucket` (10 quantiles)
  6. `user_active_degree`
  7. `follow_user_num_range`
  8. `fans_user_num_range`
  9. `friend_user_num_range`
  10. `register_days_range`
- **Model Architecture**: Factorization Machine (=16$, $\text{lr}=0.001$, $\text{batch}=8192$, L2=^{-6}$, max_epochs=25, patience=4)
- **Vocabulary Size**: 40,305 total categorical slots.

## 3. Comparative Summary of Candidates
| Candidate | Description | Valid GAUC | Valid nDCG@5 | Valid Primary | Delta vs Control | Verdict |
|---|---|---|---|---|---|---|
| Control | 5-field Baseline FM | 0.6671 | 0.5358 | 0.6015 | +0.0000 | Baseline |
| Variant v1 | 8-field Video Metadata Ext | 0.6661 | 0.5354 | 0.6007 | -0.0008 | Rejected |
| **Variant v2** | **10-field User Demographic Ext** | **0.6677** | **0.5363** | **0.6020** | **+0.0005** | **ADOPTED** |
| Variant v3 | 13-field Full CWM Joint Ext | 0.6656 | 0.5352 | 0.6004 | -0.0011 | Rejected |

## 4. Rationale & Analysis
- Variant v2 enriches user representations using low-cardinality demographic and activity status bins without injecting high-cardinality noise. This improves cross-feature interactions with video IDs and author IDs.
- Variants v1 and v3 suffered from excessive sparsity introduced by music_id without feature pruning or stronger regularization.
- All candidates strictly satisfied data boundary and leakage audits.

## 5. Next Hypothesis for Cycle 02
Now that the 10-field feature representation is established as the new champion checkpoint (Primary 0.6020), explore embedding dimension capacity and factorization rank ( \in \{8, 32, 64\}$) along with regularization tuning to test if higher or lower latent rank improves representation learning and ranking accuracy.
