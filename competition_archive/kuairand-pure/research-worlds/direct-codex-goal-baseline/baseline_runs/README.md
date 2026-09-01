# Single-agent baseline run evidence

This directory records the direct Codex agent trajectory for the managed
KuaiRand-Pure public-validation view. All scored runs use
`starter_kit/evaluate.py`, train only on `competition_data/data`'s train file,
and keep the hidden-test-free curated data path. The published validation
reference is GAUC `0.6674`, nDCG@5 `0.5357`, primary `0.6016`.

The best-valid checkpoint is the highest completed public-validation primary;
sub-epsilon changes remain evidence and do not replace it without a valid
full evaluation.

## Frozen benchmark

The detailed, machine-readable record of the previous long-running Goal run is
available in [CODEX_GOAL_BENCHMARK.md](CODEX_GOAL_BENCHMARK.md) and
[CODEX_GOAL_BENCHMARK.json](CODEX_GOAL_BENCHMARK.json). The exact Goal prompt is
frozen in [CODEX_GOAL_PROMPT.md](CODEX_GOAL_PROMPT.md).

The run reached public-validation primary `0.6044532703` after 11 substantial
cycles. The Goal controller completion record reports `271,750` tokens and
`2,920` seconds of Goal usage. The final direct-session token ledger reports
`218,767` input tokens excluding cache, `10,945,536` cache-read input tokens,
and `56,419` output tokens (`24,747` reasoning tokens, a subset of output),
for a reported total of `275,186` tokens excluding cache. These are different
accounting snapshots and must not be added. No reliable per-cycle token split
was emitted, so comparisons should use one explicitly named whole-run ledger.
