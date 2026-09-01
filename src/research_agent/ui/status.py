from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_agent.ui.parsers import parse_intuition, parse_research_record, parse_runtime, parse_state
from research_agent.ui.parsers.common import read_text


@dataclass(frozen=True)
class ResearchSnapshot:
    """Stable read-only UI contract projected from mutable research artifacts."""

    project: str
    cycle_id: int | None = None
    state_id: str | None = None
    best_metric: str | None = None
    best_experiment_id: str | None = None
    best_state_id: str | None = None
    focus_id: str | None = None
    focus: str | None = None
    focus_kind: str | None = None
    # Compatibility fields for callers that still think in the current bottleneck model.
    bottleneck_id: str | None = None
    bottleneck: str | None = None
    hypothesis_id: str | None = None
    hypothesis: str | None = None
    experiment_id: str | None = None
    experiment_status: str | None = None
    experiment_result: str | None = None
    experiment_metric: str | None = None
    experiment_conclusion: str | None = None
    experiment_fidelity: str | None = None
    experiment_official_score: bool | None = None
    experiment_resulting_state: str | None = None
    experiment_evidence_count: int | None = None
    intuition: str | None = None
    meta_concerns: tuple[str, ...] = ()
    last_status: str | None = None
    last_summary: str | None = None
    next_action: str | None = None
    usage_total: int | None = None
    usage_status: str | None = None
    usage_models: tuple[dict[str, Any], ...] = ()
    record_version: str | None = None
    state_git_tag: str | None = None
    state_derived_from: str | None = None
    state_summary: str | None = None
    state_scientist_report: str | None = None
    research_cycle_id: int | None = None
    state_validation_metrics: tuple[dict[str, Any], ...] = ()
    state_baseline_deltas: tuple[dict[str, Any], ...] = ()
    state_evidence_ref: str | None = None
    parallel_id: str | None = None
    parallel_rounds_completed: int | None = None
    parallel_rounds_total: int | None = None
    parallel_selected_branches: tuple[str, ...] = ()
    parallel_synthesis_status: str | None = None
    parallel_branches: tuple[dict[str, Any], ...] = ()


# Backward-compatible name for existing UI modules and external callers.
ResearchStatus = ResearchSnapshot


def inspect_snapshot(target: Path) -> ResearchSnapshot:
    target = target.expanduser().resolve()
    record_root = target / "research_record"
    research = parse_research_record(record_root / "RESEARCH_RECORD.yaml")
    runtime = parse_runtime(target)
    state = parse_state(record_root / "STATE.yaml")
    version = read_text(record_root / "VERSION").strip() or None

    return ResearchSnapshot(
        project=target.name,
        cycle_id=runtime.cycle_id,
        state_id=state.id,
        best_metric=research.best_metric,
        best_experiment_id=research.best_experiment_id,
        best_state_id=research.best_state_id,
        focus_id=research.focus_id,
        focus=research.focus,
        focus_kind=research.focus_kind,
        bottleneck_id=research.focus_id if research.focus_kind == "bottleneck" else None,
        bottleneck=research.focus if research.focus_kind == "bottleneck" else None,
        hypothesis_id=research.hypothesis_id,
        hypothesis=research.hypothesis,
        experiment_id=research.experiment_id,
        experiment_status=research.experiment_status,
        experiment_result=research.experiment_result,
        experiment_metric=research.experiment_metric,
        experiment_conclusion=research.experiment_conclusion,
        experiment_fidelity=research.experiment_fidelity,
        experiment_official_score=research.experiment_official_score,
        experiment_resulting_state=research.experiment_resulting_state,
        experiment_evidence_count=research.experiment_evidence_count,
        intuition=parse_intuition(record_root / "RESEARCH_INTUITION.md"),
        meta_concerns=runtime.meta_concerns,
        last_status=runtime.last_status,
        last_summary=runtime.last_summary,
        next_action=runtime.next_action,
        usage_total=runtime.usage_total,
        usage_status=runtime.usage_status,
        usage_models=runtime.usage_models,
        record_version=version,
        state_git_tag=state.git_tag,
        state_derived_from=state.derived_from,
        state_summary=state.summary,
        state_scientist_report=state.scientist_report,
        research_cycle_id=state.research_cycle_id,
        state_validation_metrics=state.validation_metrics,
        state_baseline_deltas=state.baseline_deltas,
        state_evidence_ref=state.evidence_ref,
        parallel_id=runtime.parallel_id,
        parallel_rounds_completed=runtime.parallel_rounds_completed,
        parallel_rounds_total=runtime.parallel_rounds_total,
        parallel_selected_branches=runtime.parallel_selected_branches,
        parallel_synthesis_status=runtime.parallel_synthesis_status,
        parallel_branches=runtime.parallel_branches,
    )


def inspect_status(target: Path) -> ResearchSnapshot:
    """Compatibility wrapper; new code may use inspect_snapshot directly."""

    return inspect_snapshot(target)
