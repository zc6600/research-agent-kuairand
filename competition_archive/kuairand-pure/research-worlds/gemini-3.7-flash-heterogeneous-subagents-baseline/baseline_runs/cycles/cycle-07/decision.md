# Cycle 07 Decision

## 1. Selected Action & Checkpoint Status
**Decision**: **Retain Current Best Checkpoint (Cycle 04 v2 Champion)**
- **Active Champion**: Log-Duration DCN-FM (10 fields, =16$, 20 log-duration bins) -> GAUC 0.6715, nDCG@5 0.5379, Primary 0.6047
- **Cycle 07 Candidates Evaluated**:
  - Variant v1 (Item Pop Prior, 11 fields): Primary 0.6037 ($\Delta$ = -0.0010) -> Redundant with video_id embeddings
  - Variant v2 (IPS Loss Debiased, =0.2$): Primary 0.6044 ($\Delta$ = -0.0003) -> Slight observational distribution shift
  - Variant v3 (User Hist Rate Prior, 11 fields): Primary 0.6032 ($\Delta$ = -0.0015) -> Invariant within-user, zero ranking signal
- **All variants rejected; active champion checkpoint unchanged at Primary = 0.6047**.

## 2. Comparative Matrix
| Candidate | Configuration | Fields | Valid GAUC | Valid nDCG@5 | Valid Primary | Delta vs Champion | Verdict |
|---|---|---|---|---|---|---|---|
| **Control (Cycle 04 v2)** | **Log-Duration DCN-FM** | **10** | **0.6715** | **0.5379** | **0.6047** | **+0.0000** | **Retained Champion** |
| Variant v1 | DCN-FM + Item Pop Prior | 11 | 0.6701 | 0.5373 | 0.6037 | -0.0010 | Rejected |
| Variant v2 | DCN-FM + IPS Loss Weighting | 10 | 0.6711 | 0.5378 | 0.6044 | -0.0003 | Rejected |
| Variant v3 | DCN-FM + User Hist Dwell Prior | 11 | 0.6698 | 0.5367 | 0.6032 | -0.0015 | Rejected |

## 3. Scientific Rationale & Diagnostic Takeaways
- The hypothesis that observational exposure debiasing (IPS) or coarse scalar priors improve public validation is falsified.
- KuaiRand public validation is drawn from standard recommendation traffic. Counterfactual IPS loss down-weights head items, producing a small calibration penalty on observational test traffic.
- User-level scalar priors are invariant across all candidate items evaluated in a user request, providing no discriminative rank-ordering information.
- Data boundary and leakage compliance verified cleanly across all candidates.

## 4. Next Hypothesis for Cycle 08
Investigate **Sequential User History and Short-Term Preference Modeling**. Compute recent user interaction history (e.g. mean pooling of the user last =5$ clicked / long-viewed item embeddings strictly up to each interaction timestamp) to provide dynamic, dynamic-state user representations rather than static ID embeddings alone.
