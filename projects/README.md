# Project directories

Each directory under `projects/` is one independent research trajectory and its
own Git repository.

Workspace-managed projects use:

```text
p<nnn>-<task-slug>
```

For example:

```text
p001-kuairand-pure
p002-kuairand-pure
p003-movielens
```

The three-digit number identifies the trajectory. The suffix is only the stable
task or benchmark slug, in lowercase kebab-case. Do not put the agent, model,
loss, strategy, status, State id, or timestamp into a normal project name;
those can change while the trajectory remains the same project.

When the workspace creates a new trajectory, it derives the next number from
the numbered directories that actually exist, including archived or incomplete
numbered trajectories, and uses the next integer. There is no separate project
index or status registry to keep in sync.

For the KuaiRand workspace adapter, `competition.sh setup` without an explicit
`RESEARCH_AGENT_COMPETITION_TARGET` creates the next numbered trajectory.
`competition.sh step` and `competition.sh run` without an explicit target
continue the highest-numbered active `p<nnn>-kuairand-pure` directory; if none
exists yet they create `p001-kuairand-pure`. An explicit target always wins.

Standalone projects passed explicitly to `research-agent --target` or
`research-agent init --new` may use any repository name appropriate to their
task; the `p<nnn>-<task-slug>` convention is for workspace-managed trajectories.
