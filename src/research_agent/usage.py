from __future__ import annotations

from pathlib import Path
from typing import Any

from research_agent.runtime import utc_now
from research_agent.telemetry import collect_runner, subtract_reports


def collect(
    skill_root: Path,
    target: Path,
    *,
    runner: str,
    final: bool,
    session: str | None = None,
    include_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    del skill_root
    report = collect_runner(runner, (target, *include_paths), session=session)
    report["final"] = final and report.get("accounting_status") == "measured"
    report["observed_at"] = utc_now()
    return report


def run_delta(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    report = subtract_reports(after, before)
    report["final"] = report.get("accounting_status") == "measured"
    report["observed_at"] = utc_now()
    return report
