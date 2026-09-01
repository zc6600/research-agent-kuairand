# Cycle 05 Decision

## 1. Selected Action & Checkpoint Status
**Decision**: **Retain Current Best Checkpoint (Cycle 04 v2 Champion)**
- **Active Champion**: Log-Duration DCN-FM (10 fields, =16$, 20 log duration bins) -> GAUC 0.6715, nDCG@5 0.5379, Primary 0.6047
- **Cycle 05 Candidates Evaluated**:
  - Variant v1 (Hour-of-Day, 11 fields): Primary 0.6044 ($\Delta$ = -0.0003) -> High intra-session correlation
  - Variant v2 (Day-of-Week + Hour, 12 fields): Primary 0.6043 ($\Delta$ = -0.0004) -> Out-of-time distribution shift
  - Variant v3 (Coarse 4-Dayparts, 11 fields): Primary 0.6044 ($\Delta$ = -0.0003) -> Small top-rank lift (nDCG@5 0.5380), but lower GAUC
- **All variants rejected; active champion checkpoint unchanged at Primary = 0.6047**.

## 2. Comparative Matrix
| Candidate | Configuration | Fields | Valid GAUC | Valid nDCG@5 | Valid Primary | Delta vs Champion | Verdict |
|---|---|---|---|---|---|---|---|
| **Control (Cycle 04 v2)** | **Log-Duration DCN-FM** | **10** | **0.6715** | **0.5379** | **0.6047** | **+0.0000** | **Retained Champion** |
| Variant v1 | DCN-FM + Hour-of-Day | 11 | 0.6709 | 0.5379 | 0.6044 | -0.0003 | Rejected |
| Variant v2 | DCN-FM + DOW + Hour | 12 | 0.6710 | 0.5377 | 0.6043 | -0.0004 | Rejected |
| Variant v3 | DCN-FM + Coarse Daypart | 11 | 0.6709 | 0.5380 | 0.6044 | -0.0003 | Rejected |

## 3. Scientific Rationale & Diagnostic Takeaways
- Temporal context features (, Mon Aug 31 21:29:25 +08 2026) operate at the impression/session level. Because candidate items within a single user session share identical temporal timestamps, additive temporal embeddings do not provide within-session discriminative ranking power.
- Temporal patterns show weekly non-stationarity between the historical training window (04-08 to 04-21) and the out-of-time public validation week (04-22 to 04-28).
- Data boundary and leakage compliance verified cleanly across all candidates.

## 4. Next Hypothesis for Cycle 06
Explore **Multi-Task Auxiliary Signals and Multi-Loss Joint Optimization**. KuaiRand contains 12 logged user feedback actions (, , , , ). Jointly optimizing the shared 10-field embedding and DCN cross representations with auxiliary objectives (e.g.  or  binary cross-entropy loss) will regularize sparse video and user embeddings, improving  ranking generalization.
