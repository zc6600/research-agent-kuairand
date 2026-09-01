# Project Story

> Autonomous ML discovery through pure evidence.

## Inspiration

Machine-learning research is usually described as a search over models: train
one candidate, compare a score, and keep the best checkpoint. We found that
the harder problem is the researcher itself.

An autonomous coding agent can run experiments and write impressive reports,
but a long-running trajectory gradually accumulates momentum. It remembers
unfinished hypotheses, debugging detours, and its own assumptions about what
should work. Over time, it may become very good at optimizing one local basin
while becoming less willing to explore a different one.

Starting a new agent from zero avoids that lock-in, but also discards valuable
evidence, failed experiments, evaluator knowledge, and engineering lessons.
We wanted a system that could preserve the science without preserving the
trajectory.

That led to our guiding principle:

> **A fresh Scientist should inherit the experience, not the momentum.**

## What it does

Our system runs bounded, evidence-driven machine-learning research. It gives an
agent enough autonomy to choose hypotheses, modify code, run experiments, and
interpret results, while keeping the research world durable between agent
trajectories.

The system has two scientific roles—not three. The critical insight is that
**Scientist** and **META** operate on fundamentally different time horizons,
and that asymmetry is the core of the design:

- **Scientist** lives inside a single research trajectory. Its job is scientific
  judgment: forming hypotheses, implementing candidates, running experiments, and
  interpreting the evidence it sees in its session. A Scientist's authority and
  context are intentionally local—it does not persist across handoffs.

- **META** lives across trajectories. It audits a Scientist's report against
  actual artifacts, decides what knowledge is durable enough to enter the shared
  research world, and crystallizes strong implementations into versioned States.
  Because META spans many sessions, its synthesis horizon is fundamentally longer
  than any single Scientist's reasoning window.

The temporal asymmetry between META and Scientist is not incidental: a Scientist
that ran yesterday appears to the current Scientist only through the research
world META maintained—not through shared context, not through inherited
reasoning. The deterministic process mechanics—isolation, budgets, provenance,
cancellation—are infrastructure, not a third scientific voice. This is what
makes trajectory reset safe without losing progress.

When one Scientist stops, the next one can start with the current State,
research brief, evidence ledger, negative results, and scientific intuition—
without inheriting the previous model's unfinished chain of thought.

![Research dashboard showing the current research world, State, evaluation, and token usage](https://raw.githubusercontent.com/zc6600/research-agent-kuairand/main/docs/dashboard/1.png)

## How we built it

We built a persistence boundary around a simple research loop. Each cycle
begins with a fresh Scientist reading the inherited research world, forming
hypotheses, implementing experiments, and writing a session report. META then
audits the report against actual artifacts, decides what knowledge is durable
enough to survive, and updates the world before the next Scientist begins.
Evidence is permanent; private reasoning is not.

The research world stores different kinds of information separately:

| Layer | What it stores |
|---|---|
| Evidence | Metrics, logs, code diffs, provenance, and failed experiments |
| Verified knowledge | Dataset facts, evaluator semantics, and reusable environment knowledge |
| Research state | The current understanding, open questions, and strongest checkpoint |
| Scientific intuition | Useful but explicitly fallible hypotheses and process lessons |
| Implementation State | The reproducible code and versioned retained artifact |

For the benchmark proof point, we evaluated the system on TikTok TechJam 2026
Problem 2 using the required KuaiRand-Pure dataset. The final submitted
ranker is a CPU-only NumPy ensemble of eight Factorization Machines. It uses 46
categorical fields: 38 baseline demographic, video, and context fields plus 8
leakage-safe historical preference, affinity, matching, interaction-volume,
and video-age features.

The research protocol enforced a strict public-validation boundary. The
organizer's Starter Kit evaluator was unchanged, hidden/test labels were not
used for development or model selection, and the final prediction file passed
the official alignment checker.

The development stack was Python 3.12, NumPy, `uv`, and Git, with Research
Agent orchestrating authenticated AGY, Codex, and Gemini coding-agent CLIs. The
only training data was the organizer-provided KuaiRand-Pure split; no external
training data or pretrained weights trained on benchmark test labels were used.
No application API was integrated directly; LLM access was mediated by those
authenticated CLI tools.

Across the four retained cycles, measured LLM consumption was **48,240,128
total input + output tokens including cache-read input** (4,020,880 excluding
cache-read). Combined agent wall-clock was **1h 55m 29s**, and training and
evaluation used **0 GPU-hours**. These are telemetry measurements rather than
claims about subscription pricing or plan quotas.

![Research Agent architecture showing the persistent research world, fresh Scientist sessions, META review, and Runtime](https://raw.githubusercontent.com/zc6600/research-agent-kuairand/main/docs/system.png)

## Challenges we ran into

**Persistence is not automatically memory.** If we preserve an entire
conversation, we also preserve its biases and unfinished commitments. If we
preserve nothing, every new trajectory wastes time rediscovering the evaluator
and repeating failed experiments. We had to decide what should survive, who
should curate it, and what evidence each claim actually supports.

**Scientific validity is harder than a passing metric.** A higher score can
come from a real improvement, leakage, an evaluation mismatch, or an
implementation that does not match its report. We therefore treated every score
as an evidence object: the implementation, data split, command, metrics, and
interpretation had to remain connected.

**Operational fragility in long-horizon runs.** Long-horizon agents use
heterogeneous CLIs, finite token budgets, and imperfect workspace tooling. In
one baseline attempt, the CLI silently fell back to a global scratch workspace.
The run returned a plausible score, but the artifacts were not in the requested
target. We fixed this by explicitly binding each run to a new target project,
adding independent post-run scoring, and excluding results that could not be
attributed to the correct workspace.

**Parallelism at the wrong granularity is expensive and unrewarding.** We
explored both task-level and trajectory-level parallelism. Task-level parallel
runs—multiple agents working within the same research cycle simultaneously—
consumed tokens at a much higher rate without producing proportionally better
results. The diversity was not there: agents sharing the same current context
tend to converge on similar directions regardless of their model family. In
contrast, trajectory-level parallelism—independent Scientist sessions each
starting from the same research world but developing entirely separately—
produced meaningfully different approaches and better exploration. The right
level to parallelize is the trajectory, not the task.

## Accomplishments that we're proud of

We are proud that the system improved both the research process and the
benchmark result.

| Checkpoint | GAUC | nDCG@5 | Primary |
|---|---:|---:|---:|
| Official five-field FM | 0.6674000 | 0.5357000 | 0.6016000 |
| **Final retained submission** | **0.6728421** | **0.5390304** | **0.6059363** |
| Improvement | **+0.0054421** | **+0.0033304** | **+0.0043363** |

> Research Agent achieved the highest verified public-validation score in our
> recorded comparison, outperforming the direct use of general-purpose coding
> agents such as Codex and AGY/Gemini.

The retained trajectory reached this result through four autonomous
META–Scientist cycles and 13 named experiments, with zero post-launch manual
scientific interventions, 48,240,128 total input + output tokens including
cache-read input, and zero GPU-hours. The submitted implementation runs with
NumPy on CPU, uses eight Factorization Machine seeds, and includes the evidence
needed to reproduce and audit the final checkpoint.

![Dashboard showing the retained validation checkpoint, metrics, evidence path, and baseline delta](https://raw.githubusercontent.com/zc6600/research-agent-kuairand/main/docs/dashboard/2.png)

The highest-scoring trajectory was also the most heterogeneous one. The
Scientist role rotated across model families across four cycles—`gpt-5.6-sol`
in cycle 1, `gemini-3.7-flash` in cycles 2 and 4, and `gpt-5.6-luna` in
cycle 3—while META used `gemini-3.7-flash` throughout. We believe the rotation
mattered: different model families appear to have different internal blind
spots, and switching the Scientist at trajectory boundaries may sample from
parts of the hypothesis space that a single model family would consistently
underweight.

## What we learned

**Autonomy is not a context-window problem.** The quality of autonomous
research depends on the boundary between temporary reasoning and durable
knowledge—not on how much the agent can hold in memory at once.

**Models have distinct research personalities, and those personalities have
consequences.** We observed consistent behavioral differences across model
families when used as Scientist:

- `gpt-5.6-luna` tends to be conservative and depth-first. It deepens the
  current direction rather than pivoting broadly—strong at exploitation, weaker
  at exploration when the current basin is nearly exhausted.
- `gemini-3.7-flash` tends toward breadth-first traversal. It explores more
  alternatives within a trajectory and is more willing to try qualitatively
  different directions, but without supervision it is more likely to introduce
  subtle coding errors—a failure mode that compounds over long sessions.

This suggested a natural pairing: **`gpt-5.6-luna` as META** (conservative,
good at auditing evidence, resistant to plausible but unsupported claims) and
**`gemini-3.7-flash` as Scientist** (exploratory, willing to challenge the
current framing). The roles are matched to the behavioral priors of each
model family.

**Model-switching at the Scientist level may help overcome internal blind
spots.** Our best result came from a trajectory that rotated the Scientist role
across model families. A single model's persistent search bias—whatever it
reliably overlooks or underweights—becomes a real constraint over many cycles.
Switching models at trajectory boundaries appears to be a practical way to
sample different parts of the hypothesis space without requiring a formal
diversity mechanism.

**Negative results are first-class research assets.** A failed feature family
or an invalid run can save future trajectories from repeating the same mistake—
provided the failure is recorded with the right scope and provenance.

**Evaluation discipline is part of the model.** Public validation, unchanged
tooling, explicit artifact paths, and independent re-scoring made it possible
to distinguish a promising idea from a merely plausible narrative. The system's
best result became more valuable because we could explain not only what
improved, but why we trusted the improvement.

## What's next: Autonomous ML Discovery through Pure Evidence

The most important open question is whether model-switching at the Scientist
level is a reliable diversity mechanism. Does rotating model families
systematically explore different research basins, or was the gain in our
trajectory attributable to other factors? We want to run controlled studies
that vary model assignment across otherwise identical research worlds.

We also want to understand when trajectory-level parallelism is worth its
budget: how much exploration does each independent branch add, and which
branching conditions produce the most complementary evidence?

More broadly, we plan to measure the quality of knowledge handoff. Which kinds
of scientific intuition survive a reset intact? Which get compressed into
anchors that constrain the next Scientist as much as momentum would have?

The long-term goal is a research system that gets better over time without
requiring one agent to think forever—and without inheriting the search biases
of any particular model family that thought along the way.

## Links

- Repository: https://github.com/zc6600/research-agent-kuairand
- Technical report: https://github.com/zc6600/research-agent-kuairand/blob/main/docs/FINAL_REPORT.md
- Evidence archive: https://github.com/zc6600/research-agent-kuairand/tree/main/competition_archive/kuairand-pure
