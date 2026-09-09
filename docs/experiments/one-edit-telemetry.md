# One-edit read/write telemetry experiment

## Question

The Antigravity delegated case suggests a repeated pattern: a child rereads
the project, changes one feature, and exits. This experiment isolates the cost
of that one-edit unit without including a main agent, subagents, or a long
optimization trajectory.

## Protocol

Two fresh Antigravity sessions used the same toy ranking fixture, model, effort, and
accept-edits mode:

- Model: `gemini-3.7-flash`, medium effort
- Antigravity CLI: `1.1.27`
- Workspace: a disposable `/tmp` project with `README.md`, `task.md`,
  `src/ranker.py`, and `tests/test_ranker.py`
- Read arm: inspect the four files with `view_file`, make no mutation, then
  finish
- Write arm: use the supplied target and perform one
  `replace_file_content` mutation, changing `FRESHNESS_WEIGHT = 0.25` to
  `FRESHNESS_WEIGHT = 0.30`, then finish

The arms were separate sessions so the usage report gives an actual session
measurement for each side. The write arm deliberately did not reread the
fixture; its prompt supplied the exact target line.

## Measured usage

Antigravity reports `total_tokens` as input plus output and reports `cache_read_tokens`
separately. The inclusive column below is `input + output + cache_read`.
Reasoning tokens are a subset of output and are shown for auditability, not
added a second time.

| Arm | Tool actions | Input | Output | Reasoning | Cache read | Reported total | Inclusive total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Read only | `view_file` x4 | 37,377 | 641 | 388 | 65,132 | 38,018 | **103,150** |
| Write only | `replace_file_content` x1 | 22,980 | 842 | 644 | 16,291 | 23,822 | **40,113** |

The controlled inclusive-session ratio is:

```text
103,150 / 40,113 = 2.57x read-only versus write-only
```

If cache-read input is excluded, the ratio is:

```text
38,018 / 23,822 = 1.60x read-only versus write-only
```

## Project-shaped replication

To check that the effect was not only a toy-fixture artifact, two fresh Antigravity
sessions used a disposable copy of the real KuaiRand-Pure project context. The
source files came from the archived `p0_baseline_antigravity_2h` project; no
competition data was copied or evaluated.

- Model: `gemini-3.7-flash`, medium effort; Antigravity CLI `1.1.27`
- Read arm: ten `view_file` calls over `task.md`, `PERSONAL.md`, the starter-kit
  README/data/evaluator/baseline, the system README/CLI/API, and the data manifest
- Write arm: one `replace_file_content` call in `system/baseline_api.py`, changing
  the `run_popularity_baseline` default `prior` from `20.0` to `25.0`
- Both arms completed in one model turn; neither used a main agent or subagent

| Arm | Tool actions | Input | Output | Reasoning | Cache read | Reported total | Inclusive total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Read only | `view_file` x10 | 65,366 | 1,656 | 999 | 273,065 | 67,022 | **340,087** |
| Write only | `replace_file_content` x1 | 24,185 | 1,896 | 1,545 | 16,296 | 26,081 | **42,377** |

The project-shaped inclusive-session ratio is:

```text
340,087 / 42,377 = 8.03x read-only versus write-only
```

Excluding separately reported cache-read input, the ratio is:

```text
67,022 / 26,081 = 2.57x read-only versus write-only
```

## Scaling implication

For `N` independent children, a repeated one-edit pattern costs
`N × (read + write)`. If the exploration result is made reusable and only the
mutation is repeated, the corresponding accounting is `read + N × write`.
Using the project-shaped measurement and `N = 8` gives 3,059,712 versus
679,103 inclusive tokens, or about **4.5×** more for the repeated reread
pattern. This is arithmetic based on the measured arms, not a third agent run.

## Interpretation and boundary

The one-edit unit makes the cost asymmetry visible: even with only four small
files, the read-only session used about 2.6 times the inclusive tokens of the
write-only session. Repeating this unit across independent children therefore
repeats the context cost for every child.

These are controlled measurements, not universal code-agent constants. The
arms are separate sessions, and each write arm receives the exact target in its
prompt; this intentionally isolates mutation cost from exploration cost. The
toy fixture is small, while the replication reads a selected project-shaped
context rather than the full repository. Together they support the mechanism
behind the Antigravity failure mode; they do not estimate the full token usage
of the archived delegated run and do not use main-agent totals.

## Evidence

- Read arm conversation: `81aeb221-47fa-4854-b88b-6c980cafa3c5`
- Write arm conversation: `9b0a5ae7-813c-4a24-ae7a-fe87d0c9b331`
- Both sessions completed successfully with one model turn. The read arm made
  four `view_file` calls; the write arm made one `replace_file_content` call.
- The final write diff was exactly one line:
  `FRESHNESS_WEIGHT = 0.25` -> `FRESHNESS_WEIGHT = 0.30`.

Project-shaped replication:

- Read arm conversation: `204f8b01-64d2-4df4-8154-c3021a58ebe2`
- Write arm conversation: `35c72e21-e534-4423-bf78-df3493a6e67d`
- Transcript audit: exactly ten `view_file` calls in the read arm and exactly
  one `replace_file_content` call in the write arm.
- The final write diff was exactly one line in
  `system/baseline_api.py`: `prior: float = 20.0` -> `prior: float = 25.0` in
  `run_popularity_baseline`.
