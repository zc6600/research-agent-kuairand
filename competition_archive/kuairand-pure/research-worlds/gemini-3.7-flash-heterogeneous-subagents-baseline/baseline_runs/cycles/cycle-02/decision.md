# Cycle 02 Decision

## 1. Selected Action & Checkpoint Status
**Decision**: **Retain Current Best Checkpoint (Cycle 01 v2 Champion)**
- **Active Champion**: 10-Field FM (=16$, =10^{-6}$) -> GAUC 0.6677, nDCG@5 0.5363, Primary 0.6020
- **Cycle 02 Candidates Evaluated**:
  - Variant v1 (=8$, =10^{-6}$): Primary 0.5998 ($\Delta$ = -0.0022) -> Underfitting bottleneck
  - Variant v2 (=32$, =10^{-6}$): Primary 0.6009 ($\Delta$ = -0.0011) -> Premature overfitting
  - Variant v3 (=64$, =10^{-5}$): Primary 0.6004 ($\Delta$ = -0.0016) -> Severe overparameterization
- **All variants rejected; active checkpoint unchanged at Primary = 0.6020**.

## 2. Comparative Matrix
| Candidate | Configuration | Latent Params | Valid GAUC | Valid nDCG@5 | Valid Primary | Delta vs Control | Verdict |
|---|---|---|---|---|---|---|---|
| **Control (Cycle 01 v2)** | **10-field, k=16, L2=1e-6** | **644,880** | **0.6677** | **0.5363** | **0.6020** | **+0.0000** | **Retained Champion** |
| Variant v1 | 10-field, k=8, L2=1e-6 | 322,440 | 0.6645 | 0.5351 | 0.5998 | -0.0022 | Rejected |
| Variant v2 | 10-field, k=32, L2=1e-6 | 1,289,760 | 0.6664 | 0.5353 | 0.6009 | -0.0011 | Rejected |
| Variant v3 | 10-field, k=64, L2=1e-5 | 2,579,520 | 0.6659 | 0.5348 | 0.6004 | -0.0016 | Rejected |

## 3. Scientific Rationale & Diagnostic Takeaways
- The hypothesis that rank scaling would improve ranking performance is falsified.
- =16$ provides the Pareto optimal capacity for symmetric pairwise interactions across the 10 categorical fields.
- =8$ lacks capacity to separate multi-field interactions, while =32$ and =64$ suffer from rapid overparameterization on sparse user/video IDs.
- Data boundary and leakage compliance verified cleanly across all candidates.

## 4. Next Hypothesis for Cycle 03
Explore non-linear deep interaction architectures (DeepFM / Wide&Deep MLP on top of the 10-field embeddings with =16$) to test whether higher-order non-linear combinations can surpass symmetric 2nd-order dot products.
