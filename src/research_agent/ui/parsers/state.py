from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_agent.ui.parsers.common import first_text, mapping, read_yaml, scalar_text

_RESULT_METRICS = ("GAUC", "nDCG@5", "primary")
_REPORT_CYCLE_RE = re.compile(r"(?:^|/)cycle-(\d+)(?:[-_].*)?\.md$", re.IGNORECASE)


def _metric_items(value: object) -> tuple[dict[str, object], ...]:
    values = mapping(value)
    return tuple(
        {"name": name, "value": values[name]}
        for name in _RESULT_METRICS
        if name in values and scalar_text(values[name]) is not None
    )


def _report_cycle_id(report: str | None) -> int | None:
    if not report:
        return None
    match = _REPORT_CYCLE_RE.search(report.replace("\\", "/"))
    if match is None:
        return None
    return int(match.group(1))


@dataclass(frozen=True)
class StateProjection:
    id: str | None = None
    git_tag: str | None = None
    derived_from: str | None = None
    summary: str | None = None
    scientist_report: str | None = None
    research_cycle_id: int | None = None
    validation_metrics: tuple[dict[str, object], ...] = ()
    baseline_deltas: tuple[dict[str, object], ...] = ()
    evidence_ref: str | None = None


def parse_state(path: Path) -> StateProjection:
    value: dict[str, Any] = read_yaml(path)
    performance = mapping(value.get("performance"))
    scientist_report = scalar_text(value.get("scientist_report"))
    return StateProjection(
        id=scalar_text(value.get("id")),
        git_tag=scalar_text(value.get("git_tag")),
        derived_from=scalar_text(value.get("derived_from")),
        summary=first_text(value, "summary"),
        scientist_report=scientist_report,
        research_cycle_id=_report_cycle_id(scientist_report),
        validation_metrics=_metric_items(performance.get("validation")),
        baseline_deltas=_metric_items(performance.get("baseline_delta")),
        evidence_ref=scalar_text(performance.get("evidence_ref")),
    )


def parse_state_id(path: Path) -> str | None:
    return parse_state(path).id
