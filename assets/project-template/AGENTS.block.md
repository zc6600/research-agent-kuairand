<!-- BEGIN research-agent project contract -->
## Research roles

When a research-agent invocation explicitly assigns the current agent the META
or supervisor role, keep that role and follow the META launch prompt and root
research-agent runtime contract. Do not switch into the Scientist role merely
because the working directory is the target repository. The external root Skill
is documentation for the caller; a runtime-launched META receives its required
files directly in the launcher prompt.

A Scientist process launched by research-agent receives its required project
files directly in the launcher prompt. Do not treat this contract as a request
to open `research_record/SKILL.md` during a runtime-launched invocation;
`SKILL.md` is external-agent documentation. `research_record/SYSTEM_CONTRACT.md` and
`research_record/RESEARCH_METHOD.md`, plus the task, environment, and active
coordination input, remain authoritative in their own domains. Serial Scientist
coordination comes from `RESEARCH_AGENT_BRIEF`; Parallel Scientist coordination
comes from `RESEARCH_AGENT_PARALLEL_CONTEXT` instead.

Fresh Scientists are cognitively fresh, not scientifically blank. They inherit
the project's externalized progress rather than the previous Scientist's hidden
reasoning trajectory. Runtime-launched Scientists receive `EXPLORE.md`,
`OPTIMIZE.md`, `ENGINEERING.md`, `KNOWLEDGE.md`,
`RESEARCH_INTUITION.md`, `DO_BETTER.md`, and the current `STATE.yaml`, with
`RESEARCH_RECORD.yaml`, State-linked or historical Scientist reports, and raw
evidence available for deeper reconstruction when needed. A Scientist may
challenge any fallible memory when the underlying evidence warrants it.

`EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, and `KNOWLEDGE.md` are shared
research-environment memory: META may initialize/curate them and Scientist may
update them directly during research. `RESEARCH_RECORD.yaml`,
`RESEARCH_BRIEF.md`, `RESEARCH_INTUITION.md`, `DO_BETTER.md`, and `STATE.yaml`
are META-written. Scientist writes its new append-only free-form report,
experiment evidence/logs, and implementation changes under `system/**`.
Scientist must not edit `STATE.yaml`; META must not edit the contents of
`system/**`.

When a Scientist leaves a coherent retained implementation, it first finishes
its evidence and free-form report and returns. META may then crystallize that
implementation into a State by writing `STATE.yaml` with a `scientist_report`
provenance pointer, committing the unchanged Scientist-authored `system/**`
together with the descriptor, and creating the immutable State tag.

When the opt-in `parallel` command is used, the coordinator mechanically clones
each selected research world into isolated detached Git worktrees. Each fresh
Scientist independently chooses its own hypotheses or exploratory questions,
experiments, implementation changes, and research direction; Parallel does not
have a scientific planner. After the Scientists finish, a post-hoc Parallel
Reviewer ranks completed research worlds without prescribing future scientific
work. The target research world changes only after explicit guarded promotion.

Before a data-dependent claim, Scientist should inspect enough of the real
project files, source, and evaluator to understand the semantics that materially
affect that claim. Keep `research_record/EXPLORE.md` current for durable observed
facts and `ENGINEERING.md` current for reusable execution facts. META and the
Parallel Reviewer independently inspect relevant source, logs, evaluator
behavior, and implementation/State evidence when auditing claims.
<!-- END research-agent project contract -->
