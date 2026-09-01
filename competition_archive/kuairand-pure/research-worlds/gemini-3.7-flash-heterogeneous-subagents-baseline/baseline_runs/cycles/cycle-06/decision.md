# Cycle 06 Decision

## 1. Selected Action & Checkpoint Status
**Decision**: **Retain Current Best Checkpoint (Cycle 04 v2 Champion)**
- **Active Champion**: Log-Duration DCN-FM (10 fields, =16$, 20 log-duration bins) -> GAUC 0.6715, nDCG@5 0.5379, Primary 0.6047
- **Cycle 06 Candidates Evaluated**:
  - Variant v1 (Click Aux MT, $\alpha=0.3$): Primary 0.6043 ($\Delta$ = -0.0005) -> Gradient conflict from 27.7% shallow clicks
  - Variant v2 (Like Aux MT, $\alpha=0.3$): Primary 0.6041 ($\Delta$ = -0.0006) -> Extreme sparsity (1.87% likes) and variance
  - Variant v3 (Tri-Task MT, $\alpha=0.2$): Primary 0.6041 ($\Delta$ = -0.0006) -> Hard parameter sharing capacity dilution
- **All variants rejected; active champion checkpoint unchanged at Primary = 0.6047**.

## 2. Comparative Matrix
| Candidate | Configuration | Valid GAUC | Valid nDCG@5 | Valid Primary | Delta vs Champion | Verdict |
|---|---|---|---|---|---|---|
| **Control (Cycle 04 v2)** | **Log-Duration DCN-FM** | **0.6715** | **0.5379** | **0.6047** | **+0.0000** | **Retained Champion** |
| Variant v1 | DCN-FM + Click Aux MT ($\alpha=0.3$) | 0.6709 | 0.5376 | 0.6043 | -0.0005 | Rejected |
| Variant v2 | DCN-FM + Like Aux MT ($\alpha=0.3$) | 0.6705 | 0.5377 | 0.6041 | -0.0006 | Rejected |
| Variant v3 | DCN-FM + Tri-Task MT ($\alpha=0.2$) | 0.6706 | 0.5376 | 0.6041 | -0.0006 | Rejected |

## 3. Scientific Rationale & Diagnostic Takeaways
- The hypothesis that auxiliary loss targets improve representation learning on `long_view` is falsified.
- Multi-task learning suffers from negative transfer: 27.7% of clicks are shallow clicks without long view completion. For these impressions, click gradients push embeddings toward positive engagement while long view gradients pull them in reverse, creating severe gradient conflict.
- Hard parameter sharing across multi-task objectives dilutes embedding capacity.
- Data boundary and leakage compliance verified cleanly across all candidates.

## 4. Next Hypothesis for Cycle 07
Investigate **Historical Behavior Priors & Exposure Debiasing**. Instead of joint loss multi-task training, extract static historical item popularity and user interaction frequency priors from the training log, or use Inverse Propensity Weighting (IPS) based on item exposure frequency to debias the cross-network training objective.
