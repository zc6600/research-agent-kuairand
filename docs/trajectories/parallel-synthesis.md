# A Parallel Search for a Better Ranker: a Research Agent Trajectory

We used the optional Parallel/Synthesis mode to explore
KuaiRand-Pure from a fresh research world. The run started from a clean base
commit `885ddb9b9a301712c9cfc6bed790073d1ece107e`, with only the competition
`starter_kit/` present. It therefore began without an inherited competition
checkpoint or a continuing Scientist trajectory.

The experiment paired `gpt-5.6-luna` as the persistent META/reviewer with
`gemini-3.7-flash` as the Scientist. We ran one parallel round with three
branches, all launched concurrently from the same base, kept one branch after
review, and then enabled synthesis:

```text
META / reviewer:  gpt-5.6-luna, high
Scientist:        gemini-3.7-flash, high
rounds: 1, branches: 3, parallelism: 3, keep: 1, synthesis: enabled
```

The three Scientists developed separate research worlds. `r1b1` found a
roughly 0.6048 line but was judged redundant and weaker in evidence. `r1b2`
also reached roughly 0.6048 and became the primary implementation world.
`r1b3` reached roughly 0.6039 and contributed a different multi-task and model
capacity perspective. `gpt-5.6-luna` selected `r1b2` as the implementation parent and
kept `r1b3` as reference evidence for the next Scientist.

The selected r1b2 trajectory began by reproducing the pointwise FM control at
approximately 0.6015 primary. It then moved to a within-user pairwise BPR FM
at approximately 0.6039, added a train-only video-tag field to reach about
0.6044, and used a five-seed ensemble to reach about 0.6048. Listwise softmax
and hybrid BCE+BPR were explored along the way but did not improve the line.

The synthesis stage started a fresh `gemini-3.7-flash` Scientist from r1b2. The Scientist
received r1b3's report, logs, and memory as evidence, rather than as code to
merge or instructions to follow. It developed a six-field within-user pairwise
BPR factorization machine with latent rank `k=32`, five seeds, and
within-user rank-normalization ensembling. Rank normalization improved over
logit averaging by roughly 0.0005–0.0007; `k=32` was better than `k=16`, while
`k=48` and larger ten- or twenty-seed ensembles did not add useful signal.
Auxiliary click supervision, hard negatives, and listwise softmax were weaker
directions.

The resulting public-validation score was:

| Metric | Result |
|---|---:|
| GAUC | 0.6726716757 |
| nDCG@5 | 0.5384355783 |
| Primary | **0.6055536270** |

This score came from the synthesis Scientist's new implementation and
evaluation; it was not an average of the three branch scores. The trajectory
is a compact example of the intended handoff pattern: independent Scientists
first search without a shared live context, a reviewer chooses the most useful
research world, and a fresh Scientist receives selected evidence while
retaining scientific freedom.

This episode was kept as a trajectory story rather than folded into the
canonical competition submission. Its value is the sequence of ideas and the
evidence handoff: the improvement followed a concrete modeling path—pairwise
ranking, an additional public-only field, rank choice, and seed
normalization—rather than coming from parallelism alone.

The surviving structured record is the [parallel synthesis
record](../reports/parallel-synthesis-record.json), and the same episode is
referenced in the [final report](../FINAL_REPORT.md).
