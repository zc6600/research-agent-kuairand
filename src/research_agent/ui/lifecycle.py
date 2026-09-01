from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_RUN_ROOTS = (
    "research_record/runtime/tmp",
    ".git/research-agent-baseline",
)


@dataclass(frozen=True)
class RunLifecycle:
    run_id: str
    status: str
    kind: str | None = None
    terminal_status: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _snapshot(path: Path) -> RunLifecycle | None:
    value = _read_json(path)
    run_id = value.get("run_id")
    status = value.get("status")
    if not isinstance(run_id, str) or not run_id or not isinstance(status, str) or not status:
        return None
    return RunLifecycle(
        run_id=run_id,
        status=status,
        kind=str(value.get("kind")) if value.get("kind") else None,
        terminal_status=str(value.get("terminal_status")) if value.get("terminal_status") else None,
        started_at=str(value.get("started_at")) if value.get("started_at") else None,
        ended_at=str(value.get("ended_at")) if value.get("ended_at") else None,
    )


def read_run(target: Path, run_id: str) -> RunLifecycle | None:
    target = target.expanduser().resolve()
    for relative_root in _RUN_ROOTS:
        snapshot = _snapshot(target / relative_root / run_id / "run.json")
        if snapshot is not None:
            return snapshot
    return None


def run_directory(target: Path, run: RunLifecycle) -> Path:
    """Return the durable directory containing a run's artifacts."""

    relative_root = ".git/research-agent-baseline" if run.kind == "baseline" else "research_record/runtime/tmp"
    return target.expanduser().resolve() / relative_root / run.run_id


def latest_run(target: Path) -> RunLifecycle | None:
    candidates: list[tuple[str, int, RunLifecycle]] = []
    target = target.expanduser().resolve()
    for relative_root in _RUN_ROOTS:
        root = target / relative_root
        if not root.is_dir():
            continue
        for path in root.glob("*/run.json"):
            snapshot = _snapshot(path)
            if snapshot is None:
                continue
            try:
                modified_ns = path.stat().st_mtime_ns
            except OSError:
                modified_ns = 0
            candidates.append((snapshot.started_at or "", modified_ns, snapshot))

    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[0], item[1]))[2]
