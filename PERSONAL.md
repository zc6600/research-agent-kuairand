# Runtime Environment

This file records human-declared machine, permission, and resource facts. It
makes no research or strategy decisions. Facts not stated here remain unknown
until the agent verifies them.

## Local machine

- macOS on Apple Silicon.
- 8 GB RAM and roughly 10 GB free disk were available when this environment was
  last checked.
- Use only permissions and capabilities available in the current runtime.

## Experiment timing

- Each individual experiment must be designed to finish within 15 minutes.
- Faster is better: choose the quickest run that provides useful evidence and
  balance expected scientific value against runtime.

## Python tooling

- `uv` is installed.
- In the managed runtime, E001 (2026-08-26) showed that the default uv cache at
  `/Users/frank/.cache/uv` was not writable. Use
  `RESEARCH_UV_CACHE_DIR=/private/tmp/research-agent-uv-cache` for managed
  setup, or set `UV_CACHE_DIR` explicitly for direct uv commands when needed.
- Do not assume a project already has a `.venv`, `pyproject.toml`, `uv.lock`, or
  a pinned Python version. Inspect the selected project before choosing its
  Python environment.

## Remote compute (NSCC)

- A configured local `nscc` client can reach an NSCC supercomputer using PBS
  scheduling (`qsub` / `qstat` / `qdel`).
- Authentication is automated only when the required credential environment is
  present. If authentication is unavailable, remote work stays blocked rather
  than being inferred or simulated.
- Verify current project/account, quota, allocation, queue access, and resources
  with the environment commands (`nscc status`, `nscc run 'myprojects'`,
  `nscc run 'myquota -p'`). These values change and are intentionally not
  recorded here.
- The submit helper synchronizes the source tree with `rsync --delete` and
  excludes only `.git`; whatever sits in the tree is uploaded, and files
  removed locally are deleted remotely.
- `/raid` on NSCC is node-local temporary NVMe and may be wiped at any time.
- Credentials, private NSCC configuration, and SSH control sockets must not be
  printed or copied. Never claim a remote job was submitted unless the command
  returned successfully and produced a job ID.
