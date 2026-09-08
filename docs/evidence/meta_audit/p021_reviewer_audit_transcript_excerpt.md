# Evidence Excerpt: Autonomous Reviewer / META Code & Evidence Audit

- **Project Run**: `p021-kuairand-pure` (Round 1)
- **Reviewer Agent Model**: `gpt-5.6-luna`
- **Role**: Parallel Reviewer / META
- **Source Log**: `/Users/frank/github_project/Good4AI/research_agent/projects/p021-kuairand-pure/research_record/runtime/tmp/95e584dda1c7411494df9d832f7b9b69/parallel/meta/reviewer-r1/reviewer.log`
- **Artifact Decision**: `docs/evidence/meta_audit/p021_review_r1_proxy_integrity_rejection.json`

---

## 1. Context & Task Prompt

```text
You are the Parallel Reviewer for run P95e584dd, round 1, inside a disposable control worktree.
Review only completed research; do not prescribe future scientific questions, bottlenecks,
hypotheses, or experiments...
Audit candidate commits with git show/diff and branch result/log/memory from audit_dir.
Count uncertainty reduction, bottleneck understanding, falsified hypotheses, reusable knowledge,
and improved States as research progress. Reject unsupported gains, leakage, dirty State boundaries,
and weak evidence.
```

---

## 2. Source-Level Inspection (Line-by-line Code Audit)

During the audit of Scientist's branch `r1b1`, the Reviewer inspected the implementation in `system/data.py` and diagnostic `D003`:

```diff
     selected_users = set(rng.choice(train_users, size=num_users, replace=False))
     tr_sub = [x for x in splits['train'] if x[1] in selected_users]
-    return {'train': tr_sub, 'valid': splits['valid']}
+    # Keep complete user groups in the proxy validation view as well. With
+    # user_id as a train-fitted field, evaluating every validation user after
+    # sampling train users would send most users through UNK and change the
+    # mechanism being compared.
+    va_sub = [x for x in splits['valid'] if x[1] in selected_users]
+    return {'train': tr_sub, 'valid': va_sub}
```

### Reviewer Finding
The original Scientist code sampled train users for speed in "medium" proxy mode, but evaluated on the unfiltered validation split. Since `user_id` is an ID feature vocabulary fitted only on training users, all validation impressions belonging to unsampled users mapped to the `UNK` (unknown user) token. This caused artificial distribution shift and reversed the relative ordering between BCE and BPR, invalidating the diagnostic proxy!

---

## 3. Reviewer's Authoritative Ruling (`review-r1.normalized.json`)

```json
{
  "schema_version": 1,
  "parallel_id": "P95e584dd",
  "round": 1,
  "selected_branches": [
    "r1b1"
  ],
  "rejected": [],
  "summary": "Selected r1b1 as the sole retained research world for meaningful uncertainty reduction and bottleneck clarification. Its D003 evidence is consistent with the inspected source: medium mode samples complete train-user groups but scores unfiltered validation, so unsampled validation users use train-fitted UNK user features; the temporary aligned view reverses the BCE/BPR ordering, falsifying the proxy's predictive use in this run. E003 is a valid full public-validation comparison using the curated development files and evaluator-equivalent metrics: BPR primary 0.6029116 versus BCE 0.6014688, with BPR +0.0014429 over BCE. This is one-seed evidence, below epsilon=0.002, and does not establish a robust frontier or State improvement. The candidate commit is exactly the S001 base commit, system_state_dirty is false, and no hidden-test access or leakage is evidenced. The standalone D003/E003 log paths referenced by memory are absent from the audit snapshot; their claims are therefore treated as transcript/memory evidence rather than stronger durable receipts. No branch is rejected, but no State adoption or promotion is warranted from this review.",
  "next_action": "inspect",
  "status": "completed",
  "exit_code": 0,
  "observed_at": "2026-08-30T06:24:41.272570+00:00"
}
```

### Core Empirical Takeaways
1. **Auditing beyond claims**: The Reviewer did not take the Scientist's claimed metric gains at face value; it audited the underlying feature pipeline line by line.
2. **Preventing false state promotions**: Even though full validation reported BPR > BCE (+0.0014), because it was single-seed and below the significance threshold ($\varepsilon=0.002$), the Reviewer explicitly blocked State adoption (`"no State adoption or promotion is warranted from this review"`).
