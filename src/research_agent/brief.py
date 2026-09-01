from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REQUIRED_FIELDS = ("schema_version", "cycle_id")
_BUDGET_FIELDS = frozenset({"llm_tokens", "gpu_hours"})


@dataclass(frozen=True)
class CycleBrief:
    schema_version: int
    cycle_id: int
    concerns: tuple[str, ...]
    constraints: tuple[str, ...]
    budget: dict[str, int | float]


def _positive_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def _string_list(value: Any, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"cycle brief {field} must be a JSON array")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"cycle brief {field} contains an invalid string")
        result.append(item.strip())
    return tuple(result)


def read_cycle_brief(path: Path) -> CycleBrief:
    """Read one schema-v2 META-to-Scientist supervision brief.

    The brief is ordinary coordination state written by META, so runtime parsing
    is deliberately tolerant: only schema_version and cycle_id are required;
    omitted concerns, constraints, and budget default to empty values; extension
    fields are ignored. Fields the launcher actually consumes remain type-checked.
    """
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cycle brief is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("cycle brief must be a JSON object")

    missing = [field for field in _REQUIRED_FIELDS if field not in value]
    if missing:
        raise ValueError(f"cycle brief is missing fields: {', '.join(sorted(missing))}")
    if value.get("schema_version") != 2:
        raise ValueError("cycle brief has an unsupported schema_version; expected 2")

    cycle_id = value.get("cycle_id")
    if not isinstance(cycle_id, int) or isinstance(cycle_id, bool) or cycle_id < 1:
        raise ValueError("cycle brief has an invalid cycle_id")

    concerns = _string_list(value.get("concerns", []), field="concerns")
    constraints = _string_list(value.get("constraints", []), field="constraints")

    budget = value.get("budget", {})
    if not isinstance(budget, dict):
        raise ValueError("cycle brief budget must be a JSON object")
    normalized_budget: dict[str, int | float] = {}
    for key, item in budget.items():
        if key not in _BUDGET_FIELDS:
            continue
        if not _positive_number(item) or (key == "llm_tokens" and not isinstance(item, int)):
            raise ValueError(f"cycle brief budget.{key} must be a positive number")
        normalized_budget[key] = item

    return CycleBrief(
        schema_version=2,
        cycle_id=cycle_id,
        concerns=concerns,
        constraints=constraints,
        budget=normalized_budget,
    )
