# Research Agent

Research Agent is a lightweight framework for long-running, evidence-driven ML research.

> **Preserve the research world. Reset the researcher.**

A capable research agent must both **exploit** what it has learned and remain able to **explore** qualitatively different directions. In long persistent LLM trajectories, we observed a failure mode where experiments remain technically sophisticated but become increasingly local to the current research basin.

Research Agent addresses that problem with a trajectory-level handoff:

> **The new Scientist inherits the experience, not the momentum.**

## TikTok TechJam 2026 result

Research Agent was evaluated end to end on Problem 2 using the required KuaiRand-Pure benchmark. Its submitted implementation ranks candidate videos for each user and interaction context by combining 46 categorical features in an eight-seed Factorization Machine ensemble trained with NumPy on CPU.

| Checkpoint | GAUC | nDCG@5 | Primary | Delta vs official validation primary |
|---|---:|---:|---:|---:|
| Official five-field FM | 0.6674000 | 0.5357000 | 0.6016000 | — |
| **Research Agent submission** | **0.6728421** | **0.5390304** | **0.6059363** | **+0.0043363** |

The retained E001–E013 trajectory used **4 autonomous META–Scientist cycles out of the 50-iteration cap** (13 named experiments, including 7 Full evaluations), zero post-launch manual scientific interventions, and zero GPU-hours. Its four agent runs consumed **48,240,128 total input + output tokens including cache-read input** (4,020,880 excluding cache-read). The final 170,588-row test prediction file passes the unchanged Starter Kit alignment checker.

- [Final technical report](docs/FINAL_REPORT.md)
- [Public Research Agent code, evidence, iteration logs, telemetry, and checked output](submission/research-agent-kuairand/)
- [Final prediction file](submission/research-agent-kuairand/final/research-agent-test.csv)
- [Checker result and SHA-256](submission/research-agent-kuairand/final/submit-check.txt)

## Why fresh Scientists?

A useful research trajectory produces more than a candidate model. It produces evidence, failed experiments, evaluator knowledge, engineering knowledge, and scientific intuition.

Those experiences should survive. The exact cognition that produced them does not need to.

```text
useful research trajectory
        ↓
evidence / failures / intuition
        ↓
externalized research world persists
        ↓
trajectory ends
        ↓
fresh Scientist inherits the research world
        ↓
new reasoning trajectory
```

A fresh Scientist is therefore **cognitively fresh, but scientifically informed**. Previous work appears as evidence and inherited knowledge rather than as the Scientist's own unfinished thought.

## Architecture

Research Agent separates three responsibilities:

| Layer | Responsibility | Lifetime |
|---|---|---|
| **Scientist** | Scientific judgment, coding, experiments, interpretation | One research trajectory |
| **META** | Audit, selective persistence, trajectory handoff, State crystallization | Across trajectories |
| **Runtime** | Process isolation, cancellation, runner configuration, deterministic invariants | System lifetime |

> **Scientist owns the science. META owns what survives. Runtime owns what must be deterministic.**

The serial loop is intentionally simple:

```text
persistent research world
        ↓
     fresh Scientist
        ↓
reason / code / experiment
        ↓
evidence + implementation + free-form report
        ↓
        META
        ↓
audit / compress / preserve / optional State
        ↓
updated research world
        ↓
     fresh Scientist
```

META does **not** choose the next hypothesis, model, feature, objective, or experiment. It maintains the environment in which independent scientific reasoning can happen.

## Parallel breadth

The same externalized research world can also seed several independent Scientist trajectories:

```text
                 research world R0
                 /       |       \
                /        |        \
       Scientist A  Scientist B  Scientist C
            ↓            ↓            ↓
          world A      world B      world C
                \        |        /
                 \       |       /
                  post-hoc review
```

Parallel branches run in isolated worktrees from the same inherited starting progress. They do not share one live reasoning context, so breadth is created by sampling independent successor research worlds rather than by extending a common trajectory.

A Reviewer compares completed worlds after the branches finish. Selection is explicit; a reviewed branch is only adopted into the target through `parallel-promote`.

Optional `--synthesis` adds a deliberately narrow form of cross-branch learning. One selected branch remains the **only implementation parent**; evidence from other completed worlds is copied as **reference-only input** to a fresh Scientist. Branch code, memory, and scores are not merged automatically, and the Scientist remains free to reject the synthesis.

> **Serial handoff preserves continuity across time. Parallel sampling preserves diversity across alternatives.**

This is intentionally different from continuously sharing all branch experience: branch independence comes first, and cross-branch evidence sharing happens only after review when complementary findings appear worth reconsidering together.

## Research memory

The system externalizes different kinds of research information instead of forcing them into one conversation history:

```text
Evidence & provenance
→ experiments, metrics, logs, Scientist reports

Verified/shared knowledge
→ data, evaluator, environment, reusable knowledge

Current research state
→ concise maintained brief

Fallible priors
→ scientific intuition and process lessons

Reusable implementation
→ State + system/**
```

The implementation-level ownership and artifact semantics are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Quick start

Requirements:

- Git and [`uv`](https://docs.astral.sh/uv/).
- At least one supported agent CLI installed and authenticated: Codex, Gemini,
  Claude, AGY, or OpenCode.

For example, install Codex using the
[official Codex CLI instructions](https://developers.openai.com/codex/cli),
then run `codex` once and complete the offered sign-in flow:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex
```

Clone the repository and prepare its pinned Python environment:

```bash
git clone https://github.com/zc6600/research-agent-kuairand.git
cd research-agent-kuairand
uv sync --locked --python 3.12
```

Run the launcher from the repository root:

```bash
./scripts/research-agent --help
./scripts/research-agent doctor
```

Run one bounded autonomous research cycle on an existing target:

```bash
./scripts/research-agent step \
  --cli codex \
  --target /absolute/path/to/project \
  --allow-edits
```

The main lifecycle is:

```text
init → step → run → resume
```

- **`init`** creates or prepares a research environment.
- **`step`** runs one bounded META–Scientist cycle and returns control for human observability.
- **`run`** continues the same autonomous protocol for multiple cycles within the configured budget/bounds.
- **`resume`** reconstructs the externalized research world and continues after interruption.

`step` is a control surface around autonomous research; it does not put the human inside the scientific decision loop.

### Reproduce the Research Agent competition submission

The public submission package pins Python 3.12.11 and NumPy 2.5.2 and contains the final Research Agent implementation, organizer evaluator, E001–E013 ledger, transition patches, measured usage telemetry, and final output:

```bash
cd submission/research-agent-kuairand
uv run --python 3.12.11 --with numpy==2.5.2 \
  python system/ensemble_46.py \
  --data-dir /absolute/path/to/KuaiRand-Pure/data \
  --seeds 0 1 2 3 4 5 6 7 \
  --k 16 --lr 0.001 --l2 1e-5 --full \
  --submission final/research-agent-test.csv \
  --output final/research-agent-run.json
```

See [`submission/research-agent-kuairand/README.md`](submission/research-agent-kuairand/README.md) for data requirements, exact checker command, evidence layout, and resource accounting.

## Dashboard

Research Agent includes a read-only local dashboard for presenting a project's
research result and provenance:

```bash
./scripts/research-agent gui \
  --target /absolute/path/to/project
```

The dashboard shows the live run status, current State, latest research record,
retained validation result, token usage, research intuition, and the underlying
read-only artifacts. The retained-result panel reads the validation metrics and
baseline delta from `research_record/STATE.yaml`, so a later exploratory record
does not replace the score-bearing checkpoint in the presentation.

For the competition submission, the project can be presented without a recorded
video. The public repository, the screenshots under [`docs/dashboard/`](docs/dashboard/),
the checked Research Agent output, and the reproducible command above form a self-contained
asynchronous walkthrough. If a live presentation is requested, the same dashboard
can be used for a short end-to-end demonstration of State, evidence, iteration
history, resource usage, and the retained result.

To sample independent successor trajectories from the same research world:

```bash
./scripts/research-agent parallel \
  --cli codex \
  --target /absolute/path/to/project \
  --branches 3 \
  --keep 1 \
  --parallelism 3 \
  --allow-edits
```

Add `--synthesis` only when you want the post-hoc reviewer to consider a final evidence-synthesis pass. Adoption of a reviewed result remains explicit through `parallel-promote`.

Competition-specific entry points may wrap the same protocol. For the KuaiRand workspace, use `competitions/kuairand` and `scripts/competition.sh`.

## Heterogeneous models

META and Scientist can use different CLIs, models, and reasoning-effort settings. This lets model choice follow role requirements without turning one model's search behavior into universal research policy.

The competition runner supports role-specific options such as:

```text
--meta-cli / --scientist-cli
--meta-model / --scientist-model
--meta-effort / --scientist-effort
```

Shared model/effort settings remain available as fallbacks.

## Documentation

Start with [`docs/README.md`](docs/README.md) for the full map.

| Topic | Document |
|---|---|
| Devpost-ready project narrative | [`docs/project_story.md`](docs/project_story.md) |
| Why the system exists, competition story, results, limitations | [`docs/FINAL_REPORT.md`](docs/FINAL_REPORT.md) |
| Ownership, memory semantics, State, Git, serial/parallel execution | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Competition baselines, archived research worlds, and failure analyses | [`competition_archive/kuairand-pure/`](competition_archive/kuairand-pure/INDEX.md) |
| Generic dated observations and retrospectives | [`docs/reports/`](docs/reports/) |

Trajectory analyses are intentionally post-hoc. They help us understand failure modes without becoming mandatory Scientist reasoning templates.

## Team contributions

The team worked across overlapping areas, with the following primary contributions:

- **Chen Zhu — Team Lead ([@zc18202534657](https://github.com/zc18202534657)):** overall system direction, Research Agent architecture, competition framing, end-to-end integration, and final submission coordination.
- **Zhou Ziyu ([@zziyu-4104](https://github.com/zziyu-4104)):** recommender modeling, feature and ensemble experimentation, and experimental-evidence review.
- **Shilin Xu ([@xushilin37](https://github.com/xushilin37)):** KuaiRand-Pure data workflow, Starter Kit contract checks, metric verification, and submission alignment.
- **GE GAO ([@gegao855](https://github.com/gegao855)):** agent runtime engineering, execution reliability, testing, and integration support.
- **Jiran Li ([@jiran-li](https://github.com/jiran-li)):** reproducibility, research records, telemetry, documentation, dashboard materials, and submission packaging.

These responsibilities describe human work on the framework, benchmark setup,
verification, and submission. After the retained competition run was launched,
the Scientist selected hypotheses, changed candidate code, recovered from failures,
and chose checkpoints without manual scientific intervention.

## Limitations

- The benchmark evidence comes from one recommender-system task and two single-agent controls; it does not isolate every causal contribution of META, State, and trajectory reset.
- Selective persistence is lossy. A maintained summary can omit useful context or become an anchor of its own, so raw evidence and original Scientist reports remain available for audit.
- KuaiRand-1K and KuaiRand-27K bonus benchmarks were not attempted.
- The final Research Agent implementation is practical on CPU but retrains eight seeds; checkpoint persistence and incremental execution would reduce repeated work in production use.

## Design principles

Research Agent intentionally keeps the control surface small:

- optimize the real evaluator, not compliance with a research template;
- prefer measured evidence over plausible prose;
- preserve failed and negative experiments;
- keep scientific intuition distinct from verified fact;
- let a Scientist continue a productive line of inquiry within one trajectory;
- reset at trajectory boundaries so experience can survive without preserving cognitive momentum;
- use parallel Scientists when additional breadth is worth the budget, without forcing live cross-branch memory sharing;
- let META audit scientific validity rather than duplicate every line of coding work;
- keep deterministic mechanics in runtime code;
- add new control mechanisms only after observed failures justify them.

The research method is a prior, not a policy.
