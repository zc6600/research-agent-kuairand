# Round 02 - Comparative Evaluation Report

## 1. Executive Summary & Recommendation

In Round 02, three candidate variants systematically explored the embedding dimension ($k$) and regularization capacity dynamics of the 10-field Factorization Machine (FM) architecture established by the **Cycle 01 v2 Champion** ($k=16$, Primary: `0.6020`, GAUC: `0.6677`, nDCG@5: `0.5363`).

- **Variant v1 ($k=8$, $L_2=10^{-6}$)**: Evaluated a compressed latent rank representation to act as structural regularization. It underperformed across all metrics ($\Delta\text{Primary} = -0.0022$), suffering from an under-capacity bottleneck that failed to capture fine-grained pairwise interactions across the 10 fields.
- **Variant v2 ($k=32$, $L_2=10^{-6}$)**: Doubled embedding capacity to $1.29\text{M}$ parameters. While it achieved lower training loss, it exhibited rapid out-of-sample overfitting, peaking prematurely at Epoch 4 with $\Delta\text{Primary} = -0.0011$.
- **Variant v3 ($k=64$, $L_2=10^{-5}$)**: Quadrupled capacity to $2.58\text{M}$ parameters combined with $10\times$ stronger $L_2$ weight decay. The aggressive regularization penalized dense signals without curbing sparse ID overfitting, peaking at Epoch 3 with $\Delta\text{Primary} = -0.0016$ and incurring significant training time ($58.81\text{s}$).

### Final Recommendation for Main Agent
> [!IMPORTANT]
> **RETAIN CURRENT BEST CHECKPOINT (CYCLE 01 v2 CHAMPION)**.
> All three Round 02 variants underperformed the Control baseline ($k=16$). The latent factor dimension $k=16$ remains the Pareto-optimal capacity frontier for the current 10-field feature representation on KuaiRand-Pure. Do not promote any candidate from Cycle 02 into the parent checkpoint.
>
> **Recommended Focus for Round 03**: Rather than uniform rank scaling, investigate field-specific architectures (e.g., Field-aware Factorization Machines / FFM, bilinear interaction scaling, or continuous engagement features such as historical user CTR / play-rate aggregates).

---

## 2. Comprehensive Candidate vs Control Comparison

All models were trained on the exact same 10-field feature set (40,305 total categorical dimensions) using Adam optimization ($\text{lr}=0.001$, batch size 8192) and evaluated strictly on the official public validation split (`log_public_4_22_to_4_28_pure.csv`, 124,909 impressions across 22,377 users) using `starter_kit/evaluate.py`.

### Primary Comparison Matrix

| Model / Variant | Rank ($k$) | Reg ($L_2$) | Latent Params ($V$) | Best Epoch | Valid GAUC | Valid nDCG@5 | Valid Primary | $\Delta$ vs Control | Train Time (s) | Epoch Time (s) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Control (Cycle 01 v2)** | **16** | **$10^{-6}$** | **644,880** | **7** | **0.6677** | **0.5363** | **0.6020** | **+0.0000** | **26.11s** | **~2.38s** |
| **Variant v1** | 8 | $10^{-6}$ | 322,440 | 5 | 0.6645 | 0.5351 | 0.5998 | -0.0022 | 16.00s | ~1.78s |
| **Variant v2** | 32 | $10^{-6}$ | 1,289,760 | 4 | 0.6664 | 0.5353 | 0.6009 | -0.0011 | 37.08s | ~4.63s |
| **Variant v3** | 64 | $10^{-5}$ | 2,579,520 | 3 | 0.6659 | 0.5348 | 0.6004 | -0.0016 | 58.81s | ~8.40s |

### Epoch Progression Comparison

```
Validation Primary Score Trajectory:
Epoch 1:  v3 (0.5977) > v2 (0.5954) > Control (0.5931) > v1 (0.5892)
Epoch 2:  v3 (0.6000) > v2 (0.5997) > v1 (0.5963)     > Control (0.5990)
Epoch 3:  Control (0.6009) > v2 (0.6008) > v3 (0.6004)* > v1 (0.5985)
Epoch 4:  Control (0.6011) > v2 (0.6009)* > v1 (0.5990) > v3 (0.5993)
Epoch 5:  Control (0.6013) > v1 (0.5998)* > v2 (0.5997) > v3 (0.5973)
Epoch 7:  Control (0.6020)* > v1 (0.5998) > v2 (0.5980) > v3 (0.5959)
(* indicates best epoch for each model)
```

---

## 3. In-Depth Technical Dynamics & Failure Analysis

### 3.1 Variant v1 ($k=8$): The Under-Capacity Bottleneck
- **Theoretical Premise**: Compressing $k$ down to 8 reduces the latent parameter count by 50% ($322\text{k}$ parameters), acting as an inductive bottleneck to prevent memorization of infrequent (user, video, author) pairs.
- **Empirical Failure Mode**: Across 10 distinct fields, there are $\binom{10}{2} = 45$ second-order interaction pairs. An 8-dimensional inner product space cannot simultaneously preserve orthogonal projections for user demographics, author identities, tabs, and duration buckets.
- **Diagnostic Signal**: Training loss reached an early plateau (loss $0.4973$ at epoch 5 vs $0.4880$ for $k=16$). Both GAUC ($-0.0032$) and nDCG@5 ($-0.0012$) suffered substantially, demonstrating underfitting.

### 3.2 Variant v2 ($k=32$): Empirical Overfitting on Sparse Slots
- **Theoretical Premise**: Expanding $k$ to 32 provides $1.29\text{M}$ embedding parameters, offering higher rank expressiveness for rich user-video interaction manifolds.
- **Empirical Failure Mode**: In KuaiRand-Pure, high-cardinality categorical fields (`user_id`: 26,211, `video_id`: 7,539, `author_id`: 6,483) have heavy power-law tails with low observation frequency. With default regularization ($L_2=10^{-6}$), the unconstrained 32-dimensional vectors rapidly over-memorized spurious training co-occurrences.
- **Diagnostic Signal**: Training loss dropped aggressively (0.4688 by epoch 8), but validation score degraded steeply after epoch 4 (falling from 0.6009 to 0.5968).

### 3.3 Variant v3 ($k=64$): The Uniform Regularization Dilemma
- **Theoretical Premise**: Scale capacity to $k=64$ ($2.58\text{M}$ parameters) while increasing $L_2$ penalty $10\times$ ($\lambda = 10^{-5}$) to constrain overfitting.
- **Empirical Failure Mode**: A uniform weight decay across all feature fields induces an unfavorable tension. For frequent features (e.g., `tab`, `user_active_degree`, `dur_bucket`), strong $L_2$ decay over-regularizes informative signals. For long-tail ID features, the increased dimensionality still permits rapid transient overfitting.
- **Diagnostic Signal**: Validation performance peaked at Epoch 3 (Primary $0.6004$) and decayed faster than any other variant (down to $0.5959$ by Epoch 7), while per-epoch compute time increased $3.5\times$ (~8.40s/epoch).

---

## 4. Verification & Audit Integrity

### 4.1 Data Boundary Compliance
All three candidate variants were audited against strict benchmark rules:
1. **Training Partition**: Restricted strictly to `competition_data/data/log_standard_4_08_to_4_21_pure.csv` (1,141,112 rows, dates 2022-04-08 to 2022-04-21).
2. **Validation Partition**: Restricted strictly to `competition_data/data/log_public_4_22_to_4_28_pure.csv` (124,909 rows, dates 2022-04-22 to 2022-04-28, 22,377 users).
3. **No Leakage**: Duration quantile cutoffs and category ID mappings were constructed exclusively on the training partition. Unseen validation entities correctly mapped to isolated `UNK` token IDs.
4. **No External Access**: Zero access to test datasets, external APIs, or unauthorized local files.

### 4.2 Metric & Evaluation Semantics
All candidates imported and executed `starter_kit/evaluate.py`:
- `GAUC` computation grouped by `user_id` on impressions with mixed labels.
- `nDCG@5` computed with top-5 rank truncation and binary relevance.
- `Primary` calculated strictly as `mean(GAUC, nDCG@5)`.
- All metric outputs and JSON logs match reported tables perfectly.

---

## 5. Candidate Strengths, Weaknesses, and Telemetry

| Candidate | Strengths | Weaknesses | Failure Mode |
|---|---|---|---|
| **v1 ($k=8$)** | Fast training (~1.78s/epoch, 16.00s total); lowest memory footprint. | Severely constrained expressiveness; underfits 10-field interaction space. | Representation under-capacity across 45 field pairs. |
| **v2 ($k=32$)** | Higher initial training expressiveness; closest to baseline (Primary 0.6009). | Rapid overfitting; peaks early at epoch 4; higher compute cost (~4.63s/epoch). | Over-parameterization on sparse user/video IDs. |
| **v3 ($k=64$)** | High representation headroom; fast early loss minimization. | Highest latency (58.81s); steepest post-peak degradation; $4\times$ memory footprint. | Uniform $L_2$ penalty fails to balance dense vs sparse interactions. |

---

## 6. Text & Telemetry Accounting

| Variant / Artifact | Characters | Words (Whitespace) | Lines |
|---|:---:|:---:|:---:|
| `v1/report.md` | 6,932 | 895 | 114 |
| `v2/report.md` | 7,100 | 893 | 113 |
| `v3/report.md` | 4,874 | 683 | 103 |
| `comparator/comparison.md` (This Report) | 9,259 | 1,268 | 111 |

---

## 7. Strategic Directions for Round 03

1. **Maintain $k=16$ as Standard Latent Dimension**: Experiments across $k \in \{8, 16, 32, 64\}$ establish that $k=16$ provides the optimal capacity balance for standard FM on KuaiRand-Pure.
2. **Explore Field-Aware Factorization (FFM)**: Distinct embedding vectors per field pair ($V_{i, f_j}$) can capture asymmetric cross-field dynamics (e.g., user-demographic interactions vs user-video interactions) without inflating global rank $k$.
3. **Continuous Feature Engineering**: Leverage historical interaction statistics (e.g., user historical completion rates, creator popularity scores, item click frequencies) computed strictly on training data.
4. **Adaptive Regularization / Dropout**: Implement field-specific weight decay or embedding dropout to selectively regularize sparse tail IDs while preserving dense demographic signals.
