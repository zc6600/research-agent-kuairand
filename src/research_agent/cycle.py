from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STATUSES = frozenset({"continue", "converged", "budget_exhausted", "needs_human", "failed"})


@dataclass(frozen=True)
class CycleResult:
    status: str
    summary: str
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "summary": self.summary,
            "next_action": self.next_action,
        }


def synthetic_result(
    status: str,
    summary: str,
    next_action: str = "Inspect the project state.",
    **_: object,
) -> CycleResult:
    return CycleResult(status=status, summary=summary, next_action=next_action)


def read_cycle_result(path: Path) -> CycleResult:
    """Read META's small outer-loop handoff.

    This is intentionally ordinary IPC rather than a signed or archived
    receipt. Scientific evidence lives in current research artifacts and
    observed State behavior; this file only tells the launcher how META ended.
    """
    if not path.is_file():
        return synthetic_result(
            "needs_human",
            "META ended without writing a cycle result.",
            "Inspect the META output and project state before continuing.",
        )
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return synthetic_result(
            "needs_human",
            f"META cycle result is unreadable: {exc}",
            "Inspect the META output and project state before continuing.",
        )
    if not isinstance(value, dict):
        return synthetic_result("needs_human", "META cycle result is not a JSON object.")

    status = value.get("status")
    summary = value.get("summary")
    next_action = value.get("next_action")
    if status not in STATUSES:
        return synthetic_result("needs_human", "META cycle result has an unsupported status.")
    if not isinstance(summary, str) or not summary.strip():
        return synthetic_result("needs_human", "META cycle result is missing a summary.")
    if not isinstance(next_action, str) or not next_action.strip():
        return synthetic_result("needs_human", "META cycle result is missing a next_action.")

    return CycleResult(
        status=status,
        summary=summary.strip(),
        next_action=next_action.strip(),
    )


def _cycle_id_from_json(path: Path) -> int | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    cycle_id = value.get("cycle_id")
    if isinstance(cycle_id, int) and not isinstance(cycle_id, bool) and cycle_id > 0:
        return cycle_id
    return None


def next_cycle_id(target: Path) -> int:
    """Return the next target-global cycle id from META's current brief."""
    current = _cycle_id_from_json(
        target / "research_record" / "runtime" / "current-brief.json"
    )
    return (current or 0) + 1
