from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_agent.ui.lifecycle import RunLifecycle, latest_run, run_directory
from research_agent.ui.parsers.common import mapping, read_json, scalar_text


@dataclass(frozen=True)
class RuntimeProjection:
    cycle_id: int | None = None
    meta_concerns: tuple[str, ...] = ()
    last_status: str | None = None
    last_summary: str | None = None
    next_action: str | None = None
    usage_total: int | None = None
    usage_status: str | None = None
    usage_models: tuple[dict[str, Any], ...] = ()
    parallel_id: str | None = None
    parallel_rounds_completed: int | None = None
    parallel_rounds_total: int | None = None
    parallel_selected_branches: tuple[str, ...] = ()
    parallel_synthesis_status: str | None = None
    parallel_branches: tuple[dict[str, Any], ...] = ()


def _run_result(run_dir: Path, run: RunLifecycle) -> dict[str, Any]:
    if run.kind == "baseline":
        return read_json(run_dir / "baseline" / "result.json")
    if run.kind == "parallel":
        return read_json(run_dir / "parallel" / "result.json")
    return read_json(run_dir / "meta" / "result.json")


def _run_usage(run_dir: Path, run: RunLifecycle) -> dict[str, Any]:
    if run.kind == "baseline":
        paths = (run_dir / "baseline" / "model-usage.json", run_dir / "baseline" / "usage.json")
    else:
        paths = (run_dir / "meta" / "model-usage.json", run_dir / "meta" / "usage.json")
    for path in paths:
        usage = read_json(path)
        if usage:
            return usage
    return {}


def _parallel_branches(manifest: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    branches: list[dict[str, Any]] = []
    rounds_log = manifest.get("rounds_log")
    if not isinstance(rounds_log, list):
        return ()
    for round_record in rounds_log:
        if not isinstance(round_record, dict):
            continue
        selected = {
            str(value)
            for value in round_record.get("selected_branches", [])
            if isinstance(value, str)
        }
        raw_branches = round_record.get("branches")
        if not isinstance(raw_branches, list):
            continue
        for branch in raw_branches:
            if not isinstance(branch, dict):
                continue
            branch_id = branch.get("branch_id")
            if not isinstance(branch_id, str) or not branch_id:
                continue
            branches.append({
                "branch_id": branch_id,
                "kind": str(branch.get("kind") or "replica"),
                "round": branch.get("round"),
                "status": str(branch.get("status") or "unknown"),
                "summary": str(branch.get("summary") or ""),
                "candidate_state_id": str(branch.get("candidate_state_id") or ""),
                "selected": branch_id in selected,
                "workspace_retained": bool(branch.get("workspace_retained")),
            })
    return tuple(branches)


def _parallel_selected_branches(manifest: dict[str, Any]) -> tuple[str, ...]:
    selected: list[str] = []
    rounds_log = manifest.get("rounds_log")
    if not isinstance(rounds_log, list):
        return ()
    for round_record in rounds_log:
        if not isinstance(round_record, dict):
            continue
        values = round_record.get("selected_branches")
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, str) and value and value not in selected:
                selected.append(value)
    return tuple(selected)


def _parallel_synthesis_status(manifest: dict[str, Any]) -> str | None:
    rounds_log = manifest.get("rounds_log")
    if not isinstance(rounds_log, list):
        return None
    for round_record in reversed(rounds_log):
        if not isinstance(round_record, dict):
            continue
        status = scalar_text(mapping(round_record.get("synthesis")).get("status"))
        if status:
            return status
    return None


def _parallel_projection(
    run_dir: Path,
    result: dict[str, Any],
) -> dict[str, Any]:
    manifest = read_json(run_dir / "parallel" / "manifest.json")
    raw_selected = result.get("selected_branches")
    selected = tuple(str(value) for value in raw_selected if isinstance(value, str)) if isinstance(raw_selected, list) else ()
    if not selected:
        selected = _parallel_selected_branches(manifest)
    raw_synthesis = mapping(result.get("synthesis"))
    synthesis_status = scalar_text(raw_synthesis.get("status")) or _parallel_synthesis_status(manifest)
    rounds_completed = result.get("rounds_completed")
    if not isinstance(rounds_completed, int) or isinstance(rounds_completed, bool):
        rounds_log = manifest.get("rounds_log")
        rounds_completed = len([item for item in rounds_log if isinstance(item, dict)]) if isinstance(rounds_log, list) else 0
    rounds_total = manifest.get("rounds")
    if not isinstance(rounds_total, int) or isinstance(rounds_total, bool):
        rounds_total = rounds_completed
    parallel_id = scalar_text(result.get("parallel_id")) or scalar_text(manifest.get("parallel_id"))
    return {
        "parallel_id": parallel_id,
        "parallel_rounds_completed": rounds_completed,
        "parallel_rounds_total": rounds_total,
        "parallel_selected_branches": selected,
        "parallel_synthesis_status": synthesis_status,
        "parallel_branches": _parallel_branches(manifest),
    }


def parse_runtime(target: Path) -> RuntimeProjection:
    target = target.expanduser().resolve()
    runtime = target / "research_record" / "runtime"
    run = latest_run(target)
    is_baseline = run is not None and run.kind == "baseline"
    brief = {} if is_baseline else read_json(runtime / "current-brief.json")
    run_dir = run_directory(target, run) if run is not None else None
    result = _run_result(run_dir, run) if run is not None and run_dir is not None else {}
    usage = _run_usage(run_dir, run) if run is not None and run_dir is not None else {}

    raw_concerns = brief.get("concerns")
    concerns = raw_concerns if isinstance(raw_concerns, list) else []
    cycle = brief.get("cycle_id")
    usage_total = usage.get("total")
    raw_models = usage.get("models")
    models = tuple(item for item in raw_models if isinstance(item, dict)) if isinstance(raw_models, list) else ()
    result_status = str(result.get("status")) if result.get("status") else None
    if result_status is None and run is not None:
        result_status = run.terminal_status

    projection: dict[str, Any] = {}
    if run is not None and run.kind == "parallel" and run_dir is not None:
        projection = _parallel_projection(run_dir, result)

    return RuntimeProjection(
        cycle_id=cycle if isinstance(cycle, int) and not isinstance(cycle, bool) else None,
        meta_concerns=tuple(str(item) for item in concerns if str(item).strip()),
        last_status=result_status,
        last_summary=str(result.get("summary")) if result.get("summary") else None,
        next_action=str(result.get("next_action")) if result.get("next_action") else None,
        usage_total=usage_total if isinstance(usage_total, int) and not isinstance(usage_total, bool) else None,
        usage_status=str(usage.get("accounting_status")) if usage.get("accounting_status") else None,
        usage_models=models,
        **projection,
    )
