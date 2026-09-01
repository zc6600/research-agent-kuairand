# Round 06 Independent Comparator Evaluation Report

## 1. Executive Summary & Recommendation

In Cycle 06, the multi-task learning paradigm was investigated across three distinct configurations to evaluate whether auxiliary feedback signals (`is_click`, `is_like`) could regularize shared representations and enhance ranking performance on the primary target (`long_view`):
- **Candidate v1**: Multi-Task DCN-FM with Click Auxiliary ($\alpha_{\text{click}} = 0.3$)
- **Candidate v2**: Multi-Task DCN-FM with Like Auxiliary ($\alpha_{\text{like}} = 0.3$)
- **Candidate v3**: Tri-Task Joint DCN-FM ($\alpha_{\text{click}} = 0.2, \alpha_{\text{like}} = 0.2$)

### **Final Comparator Recommendation**:
> **REJECT ALL THREE CANDIDATES. RETAIN CYCLE 04 v2 CHAMPION AS CURRENT BEST CHECKPOINT.**
>
> None of the three multi-task variants improved upon the single-task Log-Duration DCN-FM champion (**Primary 0.604721**). All three candidates suffered measurable performance degradation ($\Delta \text{Primary} \in [-0.000626, -0.000464]$) stemming from **negative transfer and gradient conflict** between superficial engagement behaviors and sustained consumption (`long_view`).

---

## 2. Comprehensive Candidate Performance Comparison

All evaluations were conducted on the official out-of-time public validation partition (`log_public_4_22_to_4_28_pure.csv`, 124,909 impressions across 22,377 users) using exact `starter_kit/evaluate.py` ranking semantics.

| Model / Variant | GAUC | nDCG@5 | Primary Score | $\Delta$ vs Champion (Primary) | Optimal Epoch | Total Wall Time | Verdict |
|---|---|---|---|---|---|---|---|
| **Control (Cycle 04 v2 Champion)** | **0.671546** | **0.537897** | **0.604721** | — (Baseline) | 5 / 6 | 43.11s | **Active Champion** |
| **Candidate v1 (Aux Click MT, $\alpha=0.3$)** | 0.670947 | 0.537567 | 0.604257 | -0.000464 (-0.0005) | 5 | 41.11s | Reject |
| **Candidate v2 (Aux Like MT, $\alpha=0.3$)** | 0.670492 | 0.537726 | 0.604109 | -0.000612 (-0.0006) | 5 | 47.32s | Reject |
| **Candidate v3 (Tri-Task Joint MT, $\alpha_1=\alpha_2=0.2$)** | 0.670559 | 0.537631 | 0.604095 | -0.000626 (-0.0006) | 4 | 42.32s | Reject |

### Detailed Metric Deltas vs Control:
- **Variant v1 (Click Aux)**: $\Delta \text{GAUC} = -0.000599$, $\Delta \text{nDCG@5} = -0.000330$, $\Delta \text{Primary} = -0.000464$
- **Variant v2 (Like Aux)**: $\Delta \text{GAUC} = -0.001054$, $\Delta \text{nDCG@5} = -0.000171$, $\Delta \text{Primary} = -0.000612$
- **Variant v3 (Tri-Task)**: $\Delta \text{GAUC} = -0.000987$, $\Delta \text{nDCG@5} = -0.000266$, $\Delta \text{Primary} = -0.000626$

---

## 3. Data Boundary, Leakage & Integrity Audit

Each candidate subagent repository was independently inspected for data boundary compliance, script execution validity, and evaluation fidelity.

| Candidate | Data Boundary Compliance | Public Split Isolation | Duration Discretization Source | Official Evaluator Used | Verification Status |
|---|---|---|---|---|---|
| **v1** | Strict (Train: 4/08-4/21, Valid: 4/22-4/28) | Passed (Zero test leakage) | Train partition only | Passed (`starter_kit/evaluate.py`) | Verified |
| **v2** | Strict (Train: 4/08-4/21, Valid: 4/22-4/28) | Passed (Zero test leakage) | Train partition only | Passed (`starter_kit/evaluate.py`) | Verified |
| **v3** | Strict (Train: 4/08-4/21, Valid: 4/22-4/28) | Passed (Zero test leakage) | Train partition only | Passed (`starter_kit/evaluate.py`) | Verified |

- **Static Feature Integration**: All variants properly joined demographic features (`user_features_pure.csv`) and basic video metadata (`video_features_basic_pure.csv`).
- **Feature Vocabulary & Binning**: Vocabularies, UNK tokens, and 20 log-duration bin thresholds were strictly derived on the training set.
- **Evaluation Discipline**: Validation ranking scores were computed exclusively on true `long_view` ground truth without any contamination from auxiliary labels.

---

## 4. Deep Scientific Analysis: Negative Transfer & Gradient Interference Dynamics

### 4.1 Click Auxiliary Negative Transfer (Variant v1)
1. **Behavioral Divergence**:
   - In training data, `is_click` has a positive rate of 46.34% (528,845 positives) compared to 33.66% for `long_view` (384,121 positives).
   - Crucially, 146,333 impressions (~27.7% of all clicks) are "shallow clicks" where $y_{\text{click}} = 1$ but $y_{\text{long\_view}} = 0$ (i.e., user clicked/opened the video but bounced before satisfying the long-view dwell criteria).
2. **Gradient Conflict in Shared Parameters**:
   - For shallow clicks, $\frac{\partial \mathcal{L}_{\text{click}}}{\partial z_{\text{click}}} < 0$ (pushing embeddings toward positive engagement), whereas $\frac{\partial \mathcal{L}_{\text{long}}}{\partial z_{\text{long}}} > 0$ (pushing embeddings toward negative classification).
   - In the shared embedding table $V \in \mathbb{R}^{40304 \times 16}$ and explicit cross layer $W_c \in \mathbb{R}^{160 \times 160}$, the auxiliary click loss pulls video and user representations toward high clickability rather than high retention.
   - Consequently, within-user ranking discriminability is degraded (GAUC dropped by 0.0006).

### 4.2 Like Auxiliary Gradient Sparsity & Misalignment (Variant v2)
1. **Sparsity & Extreme Imbalance**:
   - `is_like` has a positive base rate of only 1.87% (21,312 positives out of 1.14M training rows).
   - Sparse explicit feedback signals produce sharp, localized, high-variance gradient spikes on specific active video IDs and author IDs.
2. **Intent Mismatch**:
   - High-like videos often consist of punchy, short-duration comedy or meme clips with immediate gratification, whereas `long_view` rewards longer dwell duration.
   - While `nDCG@5` suffered less degradation (-0.0002) than in v1, overall global discriminability across all impressions deteriorated significantly ($\Delta \text{GAUC} = -0.0011$).

### 4.3 Tri-Task Representation Dilution (Variant v3)
1. **Backbone Capacity Bottleneck**:
   - With fixed embedding dimension $k=16$ ($D=160$ concatenated), the shared backbone capacity is severely constrained.
   - Forcing the representation to concurrently capture three conflicting objectives (`long_view`, `is_click`, `is_like`) creates capacity competition.
2. **Premature Convergence & Negative Transfer Overfitting**:
   - Candidate v3 peaked at Epoch 4 (Primary 0.6041) before decaying sharply by Epoch 8 (Primary 0.6018), even as auxiliary training losses continued to fall (Click: 0.6294 $\to$ 0.5303, Like: 0.2850 $\to$ 0.0566).
   - This empirically confirms that auxiliary task over-optimization directly cannibalizes primary ranking generalization.

---

## 5. Candidate Strengths, Weaknesses, and Failure Modes

### Variant v1 (Aux Click MT)
- **Strengths**: High-volume signal (46.3% positives) provided stable gradients; fastest execution time (41.11s).
- **Weaknesses**: 27.7% shallow-click mismatch caused direct gradient antagonism against `long_view`.
- **Failure Mode**: Promoted clickbait-style items into the top ranks, reducing `nDCG@5` to 0.5376.

### Variant v2 (Aux Like MT)
- **Strengths**: Clean high-intent explicit signal; preserved top-tier ranking better than v1 (`nDCG@5` 0.5377).
- **Weaknesses**: Severe data sparsity (1.87% base rate) caused erratic gradient updates in shared embeddings; lowest GAUC (0.6705).
- **Failure Mode**: Poor generalization on unliked long-dwell impressions.

### Variant v3 (Tri-Task MT)
- **Strengths**: Comprehensive multi-action modeling structure with clean per-head modularity.
- **Weaknesses**: Simultaneous exposure to both shallow-click gradient conflict and like sparsity; capacity bottleneck.
- **Failure Mode**: Earliest validation degradation (Epoch 4 peak) and lowest overall primary score (0.604095).

---

## 6. Strategic Takeaways & Recommendations for Subsequent Cycles

1. **Abandon Shared-Backbone Naive Hard Parameter Sharing Multi-Tasking**:
   - Standard hard parameter sharing forces conflicting objectives into a low-dimensional shared embedding bottleneck ($k=16$).
   - Auxiliary engagement signals in KuaiRand do not exhibit positive transfer to `long_view` under symmetric shared backbones.
2. **Promising Alternative Directions**:
   - **Feature-Level Dwell / Engagement Priors**: Rather than using `is_click` as a multi-task loss target, incorporate historical user/item click-to-long-view conversion rates as static continuous input features.
   - **Asymmetric / Gated Architectures**: If multi-task learning is revisited, explore MMoE (Multi-gate Mixture-of-Experts) or Progressive Layered Extraction (PLE) to decouple task-specific representation subspaces from shared spaces.
   - **Advanced Feature Interactions & Higher-Order Discretization**: Single-task DCN-FM with enriched feature fields (e.g., cross-feature embeddings, author-level historical statistics, fine-grained duration-ratio buckets) remains the most promising path forward.

---

## 7. Evidence & Text Accounting

### Candidate Subagent Reports Audited:
- `baseline_runs/cycles/cycle-06/v1/report.md`: 127 lines | 1,106 words | 8,387 characters
- `baseline_runs/cycles/cycle-06/v2/report.md`: 91 lines | 950 words | 7,323 characters
- `baseline_runs/cycles/cycle-06/v3/report.md`: 159 lines | 1,288 words | 9,733 characters

### Comparator Report Statistics:
- **Total Lines**: 121 lines
- **Total Word Count**: 1,210 words
- **Total Character Count**: 9,407 characters
