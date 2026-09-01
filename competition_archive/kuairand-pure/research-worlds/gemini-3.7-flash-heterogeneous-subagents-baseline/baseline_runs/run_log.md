# gemini-3.7-flash 12-Round Subagent-Assisted Research Log

## Project: `gemini-3.7-flash-heterogeneous-subagents-2026-08-31`
- **Benchmark**: KuaiRand-Pure
- **Task**: Within-user ranking over logged impressions
- **Primary Metric**: `primary = mean(GAUC, nDCG@5)`
- **Starting Control (Official FM Baseline)**:
  - GAUC: `0.6671`
  - nDCG@5: `0.5358`
  - Primary: `0.6015`

---

## Data Boundary Inventory
Verified before Round 1:
- `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (Train: 1,141,112 rows)
- `competition_data/data/log_public_4_22_to_4_28_pure.csv` (Valid: 124,909 rows)
- `competition_data/data/log_random_4_22_to_4_28_pure.csv` (Random Exposure: 1,186,059 rows)
- `competition_data/data/user_features_pure.csv` (27,285 users)
- `competition_data/data/video_features_basic_pure.csv` (7,551 items)

---

## Cycle Index and Score Progression

| Cycle | Hypothesis / Focus | Selected Variant | Validation GAUC | Validation nDCG@5 | Validation Primary | Delta vs Control | Status | Link |
|---|---|---|---|---|---|---|---|---|
| Control | Official FM Baseline (5 fields) | baseline | 0.6671 | 0.5358 | 0.6015 | +0.0000 | Baseline | - |
| Cycle 01 | CWM Feature Exploration (Video vs User vs Joint) | variant-v2 (10-field) | 0.6677 | 0.5363 | 0.6020 | +0.0005 | Adopted (New Best) | [cycle-01/decision.md](cycles/cycle-01/decision.md) |
| Cycle 02 | Factorization Rank & Latent Capacity (k=8, 32, 64) | [None - Kept Cycle 01 v2] | 0.6677 | 0.5363 | 0.6020 | +0.0000 | Retained (k=16 Best) | [cycle-02/decision.md](cycles/cycle-02/decision.md) |
| Cycle 03 | Deep & Cross Architectures (DeepFM vs Wide&Deep vs DCN-FM) | variant-v3 (DCN-FM) | 0.6705 | 0.5377 | 0.6041 | +0.0026 | Adopted (New Record) | [cycle-03/decision.md](cycles/cycle-03/decision.md) |
| Cycle 04 | Continuous Duration Modeling (Quantile vs Log-Bins vs Multi-Res) | variant-v2 (Log-Dur DCN-FM) | 0.6715 | 0.5379 | 0.6047 | +0.0032 | Adopted (New Record) | [cycle-04/decision.md](cycles/cycle-04/decision.md) |
| Cycle 05 | Temporal Context (Hour-of-Day vs DOW+Hour vs Daypart) | [None - Kept Cycle 04 v2] | 0.6715 | 0.5379 | 0.6047 | +0.0000 | Retained (Context Shift) | [cycle-05/decision.md](cycles/cycle-05/decision.md) |
| Cycle 06 | Multi-Task Auxiliary Optimization (Click vs Like vs Tri-Task) | [None - Kept Cycle 04 v2] | 0.6715 | 0.5379 | 0.6047 | +0.0000 | Retained (Negative Transfer) | [cycle-06/decision.md](cycles/cycle-06/decision.md) |
| Cycle 07 | Behavior Priors & Exposure Debiasing (Item Pop vs IPS Loss vs User Dwell) | [None - Kept Cycle 04 v2] | 0.6715 | 0.5379 | 0.6047 | +0.0000 | Retained (Obs Alignment) | [cycle-07/decision.md](cycles/cycle-07/decision.md) |

---

## Subagent Telemetry & Resource Accounting

| Cycle | Invocation / Role | Subagent Type | Input Tokens | Output Tokens | Thinking Tokens | Cache Read | Total Tokens | Duration (s) | Turns | Report Chars / Words / Lines |
|---|---|---|---|---|---|---|---|---|---|---|
| Cycle 01 | variant-v1 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 36.01 | 1 | 8991 / 1154 / 159 |
| Cycle 01 | variant-v2 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 34.41 | 1 | 6207 / 823 / 106 |
| Cycle 01 | variant-v3 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 33.96 | 1 | 9282 / 1157 / 146 |
| Cycle 01 | comparator | comparator_agent | unavailable | unavailable | unavailable | unavailable | unavailable | ~60 | 1 | 6649 / 821 / 117 |
| Cycle 02 | variant-v1 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 24.44 | 1 | 6932 / 895 / 114 |
| Cycle 02 | variant-v2 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 46.37 | 1 | 7100 / 893 / 113 |
| Cycle 02 | variant-v3 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 67.21 | 1 | 4874 / 683 / 103 |
| Cycle 02 | comparator | comparator_agent | unavailable | unavailable | unavailable | unavailable | unavailable | ~60 | 1 | 9259 / 1268 / 111 |
| Cycle 03 | variant-v1 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 53.59 | 1 | 7285 / 910 / 119 |
| Cycle 03 | variant-v2 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 57.60 | 1 | 8125 / 1022 / 128 |
| Cycle 03 | variant-v3 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 45.65 | 1 | 5705 / 826 / 112 |
| Cycle 03 | comparator | comparator_agent | unavailable | unavailable | unavailable | unavailable | unavailable | ~60 | 1 | 14810 / 2058 / 193 |
| Cycle 04 | variant-v1 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 52.37 | 1 | 5792 / 831 / 114 |
| Cycle 04 | variant-v2 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 52.59 | 1 | 6716 / 945 / 124 |
| Cycle 04 | variant-v3 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 49.20 | 1 | 7406 / 1004 / 139 |
| Cycle 04 | comparator | comparator_agent | unavailable | unavailable | unavailable | unavailable | unavailable | ~60 | 1 | 8945 / 1264 / 116 |
| Cycle 05 | variant-v1 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 46.04 | 1 | 6137 / 892 / 118 |
| Cycle 05 | variant-v2 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 47.68 | 1 | 8291 / 1125 / 143 |
| Cycle 05 | variant-v3 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 49.23 | 1 | 8016 / 1115 / 107 |
| Cycle 05 | comparator | comparator_agent | unavailable | unavailable | unavailable | unavailable | unavailable | ~60 | 1 | 11515 / 1657 / 151 |
| Cycle 06 | variant-v1 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 41.11 | 1 | 8387 / 1106 / 127 |
| Cycle 06 | variant-v2 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 47.32 | 1 | 7323 / 950 / 91 |
| Cycle 06 | variant-v3 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 42.32 | 1 | 9733 / 1288 / 159 |
| Cycle 06 | comparator | comparator_agent | unavailable | unavailable | unavailable | unavailable | unavailable | ~60 | 1 | 9407 / 1210 / 121 |
| Cycle 07 | variant-v1 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 139.12 | 1 | 9570 / 1282 / 151 |
| Cycle 07 | variant-v2 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 103.46 | 1 | 8236 / 1034 / 100 |
| Cycle 07 | variant-v3 | variant_agent | unavailable | unavailable | unavailable | unavailable | unavailable | 122.83 | 1 | 10843 / 1521 / 168 |
| Cycle 07 | comparator | comparator_agent | unavailable | unavailable | unavailable | unavailable | unavailable | ~60 | 1 | 10294 / 1372 / 122 |
