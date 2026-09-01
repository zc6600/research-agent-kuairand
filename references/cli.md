# CLI Reference

The checkout script and installed command expose the same interface:

```bash
./scripts/research-agent <command> ...
research-agent <command> ...
```

The Python CLI is the source of truth for argument validation and deterministic runtime boundaries. Scientific judgment and artifact ownership live in META/Scientist prompts and project-local research memory, not in CLI flags.

## Commands

| Command | Meaning |
|---|---|
| `init` | Initialize one project with the current research-record format |
| `step` | Run one META session with at most one fresh Scientist |
| `run` | Run one persistent META session for up to `--max-cycles` Scientist sessions |
| `resume` | Start another META session from the same project memory |
| `launch-inner` | Launch exactly one fresh Serial Scientist from the current project/brief |
| `parallel` | Run isolated independent Scientist replicas followed by post-hoc review |
| `parallel-promote` | Legacy explicit Parallel adoption path; see limitation below |
| `state materialize` | Reuse a historical implementation State without rewinding research memory |
| `state create` | Create an immutable tag for an already committed META-described State |
| `usage` | Read supported runner telemetry |
| `doctor` | Check installed runner commands and versions |

There is no record migration command. `research-agent-record-v5` is intentionally incompatible with older project-local prompt/record semantics; initialize a clean project rather than silently mixing versions.

## Initialize

```bash
research-agent init --target /absolute/project
```

or create a new project from explicit task/personal inputs. Initialization creates the persistent research environment, including Record, Brief, Explore, Optimize, Engineering, Knowledge, Intuition, and Do Better layers. Mutable research memory is not Git State history.

## Serial

Run one supervised Scientist session:

```bash
research-agent step --cli codex --target /absolute/project --allow-edits
```

Run several fresh Scientist sessions under one persistent META:

```bash
research-agent run --cli codex --target /absolute/project --allow-edits --max-cycles 20
```

Continue later with another META session reading the same externalized progress:

```bash
research-agent resume --cli codex --target /absolute/project --allow-edits --max-cycles 10
```

`step`, `run`, and `resume` each start one META process. META may launch fresh Scientists through `launch-inner`; an active Scientist cannot recursively launch another Scientist.

Direct `launch-inner` intentionally skips META for that one invocation. Scientist may therefore leave `system/**` changes and its free-form report, but there is no supervisor in that invocation to write `STATE.yaml` or crystallize a State afterward.

## State

Scientist changes implementation under `system/**` and writes its report. META writes `STATE.yaml` only after that report exists and after auditing the retained implementation/evidence. META then commits the unchanged implementation plus descriptor and invokes canonical State creation.

```bash
research-agent state create --target /absolute/project S006
```

`state create` is mechanical: it requires a committed `system/** + STATE.yaml` boundary and an existing `scientist_report` referenced by the descriptor. It does not author the descriptor itself.

To reuse a historical State:

```bash
research-agent state materialize --target /absolute/project S006
```

Materialization restores only the State-controlled implementation/descriptor, leaves current research memory at current research time, and returns the linked Scientist report path for provenance.

## Parallel

Parallel remains a separate opt-in branching runtime:

```bash
research-agent parallel \
  --cli codex \
  --target /absolute/project \
  --allow-edits \
  --rounds 2 \
  --branches 2 \
  --keep 1 \
  --parallelism 2
```

The coordinator creates isolated worktrees. Each Scientist independently chooses its scientific work from the same externalized parent world. A post-hoc Reviewer compares completed worlds and does not prescribe future science.

Parallel Scientists follow the same ownership boundary as Serial Scientists: they may change `system/**` and write evidence/reports, but they do not own `STATE.yaml`.

The current `parallel-promote` implementation predates post-Scientist META ownership of `STATE.yaml`. Until that path is refactored, do not assume a code-changing Parallel branch can be canonically promoted as a State merely because review selected it. Reports/evidence remain inspectable and diagnostic-only research worlds remain useful; canonical State creation requires META-style post-session crystallization.

Optional synthesis is still an evidence-exposure mechanism, not a permission to merge code or rewrite ownership rules.

## Models and reasoning effort

`--cli` selects the default runner for META and Scientist. Role-specific overrides are available through `--meta-cli`, `--scientist-cli`, `--meta-model`, `--scientist-model`, `--meta-effort`, and `--scientist-effort`.

Shared `--model` and `--effort` apply to both roles unless overridden. Supported generic effort values are:

```text
low | medium | high | max
```

## Output and permissions

Automated research paths require explicit `--allow-edits`.

```text
-v / --verbose   stream detailed runner output
-q / --quiet     print only final status
```

Runtime JSON and logs under `research_record/runtime/` are process coordination and telemetry, not a second research ledger. Git commit order is not research chronology.
