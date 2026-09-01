from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_agent.ui.parsers.common import first_text, mapping, mappings, read_yaml, scalar_text


@dataclass(frozen=True)
class ResearchRecordProjection:
    focus_id: str | None = None
    focus: str | None = None
    focus_kind: str | None = None
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
    best_metric: str | None = None
    best_experiment_id: str | None = None
    best_state_id: str | None = None


_ROOT_COLLECTIONS = ("bottlenecks", "research_threads", "threads")
_HYPOTHESIS_COLLECTIONS = ("hypotheses", "candidate_explanations", "explanations")
_EXPERIMENT_COLLECTIONS = ("experiments", "interventions", "tests")
_FOCUS_KIND = {
    "bottlenecks": "bottleneck",
    "research_threads": "research thread",
    "threads": "research thread",
}


def _collection(value: dict[str, Any], keys: tuple[str, ...]) -> tuple[str | None, list[dict[str, Any]]]:
    for key in keys:
        items = mappings(value.get(key))
        if items:
            return key, items
    return None, []


def _select_research_item(root_key: str | None, items: list[dict[str, Any]]) -> dict[str, Any]:
    for wanted in ("active", "forming"):
        for item in reversed(items):
            if scalar_text(item.get("status")) == wanted:
                return item
    if root_key != "bottlenecks" and items:
        return items[-1]
    return {}


def _latest_child(value: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    _, items = _collection(value, keys)
    return items[-1] if items else {}


def _experiment_status(value: dict[str, Any]) -> str | None:
    evaluation = mapping(value.get("evaluation"))
    return scalar_text(evaluation.get("status")) or scalar_text(value.get("status"))


def _experiment_fidelity(value: dict[str, Any]) -> str | None:
    evaluation = mapping(value.get("evaluation"))
    return scalar_text(evaluation.get("fidelity")) or scalar_text(value.get("fidelity"))


def _experiment_official_score(value: dict[str, Any]) -> bool | None:
    official = value.get("official_score")
    if isinstance(official, bool):
        return official

    evaluation = mapping(value.get("evaluation"))
    status = (scalar_text(evaluation.get("status")) or "").lower()
    fidelity = (scalar_text(evaluation.get("fidelity")) or "").lower()
    split = (scalar_text(evaluation.get("split")) or "").lower()
    if not any((status, fidelity, split)):
        return None
    return status == "completed" and fidelity == "full" and split == "public_validation"


def _experiment_evidence_count(value: dict[str, Any]) -> int | None:
    evidence = value.get("evidence")
    if not isinstance(evidence, list):
        return None
    return len(evidence)


def _experiment_metric(value: dict[str, Any]) -> str | None:
    evaluation = mapping(value.get("evaluation"))
    primary = mapping(evaluation.get("primary_metric"))
    if not primary:
        primary = mapping(value.get("primary_metric"))
    metric_value = scalar_text(primary.get("value"))
    if not metric_value:
        return None

    name = scalar_text(primary.get("name"))
    metric = f"{name}: {metric_value}" if name else metric_value
    delta = scalar_text(evaluation.get("improvement_over_comparator"))
    if delta:
        comparator = scalar_text(evaluation.get("compared_with_state"))
        metric += f" · Δ {delta}"
        if comparator:
            metric += f" vs {comparator}"
    return metric


def _metric_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _iter_experiments(root: dict[str, Any]):
    _, direct = _collection(root, _EXPERIMENT_COLLECTIONS)
    yield from direct
    _, hypotheses = _collection(root, _HYPOTHESIS_COLLECTIONS)
    for hypothesis in hypotheses:
        _, experiments = _collection(hypothesis, _EXPERIMENT_COLLECTIONS)
        yield from experiments


def _best_full_validation(
    roots: list[dict[str, Any]],
) -> tuple[str | None, str | None, str | None]:
    best: tuple[float, str | None, str | None, str | None] | None = None
    for root in roots:
        for experiment in _iter_experiments(root):
            evaluation = mapping(experiment.get("evaluation"))
            status = scalar_text(evaluation.get("status"))
            fidelity = scalar_text(evaluation.get("fidelity"))
            split = scalar_text(evaluation.get("split"))
            if status != "completed" or fidelity != "full" or split != "public_validation":
                continue

            primary = mapping(evaluation.get("primary_metric"))
            metric_value = _metric_number(primary.get("value"))
            if metric_value is None:
                continue

            metric_name = scalar_text(primary.get("name"))
            experiment_id = scalar_text(experiment.get("id"))
            state_id = scalar_text(experiment.get("resulting_state")) or scalar_text(
                experiment.get("starting_state")
            )
            if best is None or metric_value > best[0]:
                best = (metric_value, metric_name, experiment_id, state_id)

    if best is None:
        return None, None, None

    value, name, experiment_id, state_id = best
    display_value = format(value, ".6g")
    metric = f"{name}: {display_value}" if name else display_value
    return metric, experiment_id, state_id


def _best_simple_experiment(
    experiments: list[dict[str, Any]],
) -> tuple[str | None, str | None, str | None]:
    best: tuple[float, str | None, str | None, str | None] | None = None
    for experiment in experiments:
        if experiment.get("official_score") is not True:
            continue
        primary = mapping(experiment.get("primary_metric"))
        value = _metric_number(primary.get("value"))
        if value is None:
            continue
        name = scalar_text(primary.get("name"))
        experiment_id = scalar_text(experiment.get("id"))
        state_id = scalar_text(experiment.get("resulting_state"))
        if best is None or value > best[0]:
            best = (value, name, experiment_id, state_id)
    if best is None:
        return None, None, None
    value, name, experiment_id, state_id = best
    display = format(value, ".6g")
    return (f"{name}: {display}" if name else display), experiment_id, state_id


def _parse_simple_ledger(document: dict[str, Any]) -> ResearchRecordProjection | None:
    experiments = mappings(document.get("experiments"))
    if not experiments:
        return None
    latest = experiments[-1]
    best_metric, best_experiment_id, best_state_id = _best_simple_experiment(experiments)
    record = first_text(latest, "record", "summary", "result", "observation")
    return ResearchRecordProjection(
        focus_id=scalar_text(latest.get("id")),
        focus=record,
        focus_kind="experiment",
        experiment_id=scalar_text(latest.get("id")),
        experiment_status="recorded",
        experiment_result=record,
        experiment_metric=_experiment_metric(latest),
        experiment_fidelity=_experiment_fidelity(latest),
        experiment_official_score=_experiment_official_score(latest),
        experiment_resulting_state=scalar_text(latest.get("resulting_state")),
        experiment_evidence_count=_experiment_evidence_count(latest),
        best_metric=best_metric,
        best_experiment_id=best_experiment_id,
        best_state_id=best_state_id,
    )


def parse_research_record(path: Path) -> ResearchRecordProjection:
    document = read_yaml(path)

    # Current lightweight format: a complete chronological experiment ledger where
    # each experiment's scientific content is one human-readable paragraph.
    simple = _parse_simple_ledger(document)
    if simple is not None:
        return simple

    # Backward-compatible UI reading for older nested research records.
    root_key, roots = _collection(document, _ROOT_COLLECTIONS)
    best_metric, best_experiment_id, best_state_id = _best_full_validation(roots)
    selected = _select_research_item(root_key, roots)
    if not selected:
        return ResearchRecordProjection(
            best_metric=best_metric,
            best_experiment_id=best_experiment_id,
            best_state_id=best_state_id,
        )

    hypothesis = _latest_child(selected, _HYPOTHESIS_COLLECTIONS)
    experiment = _latest_child(hypothesis, _EXPERIMENT_COLLECTIONS) if hypothesis else {}
    if not experiment:
        experiment = _latest_child(selected, _EXPERIMENT_COLLECTIONS)

    return ResearchRecordProjection(
        focus_id=scalar_text(selected.get("id")),
        focus=first_text(selected, "description", "question", "title", "name"),
        focus_kind=_FOCUS_KIND.get(root_key or "", "research focus") if root_key else None,
        hypothesis_id=scalar_text(hypothesis.get("id")),
        hypothesis=first_text(hypothesis, "description", "explanation", "claim", "question", "title"),
        experiment_id=scalar_text(experiment.get("id")),
        experiment_status=_experiment_status(experiment),
        experiment_result=first_text(experiment, "actual_result", "result", "observation"),
        experiment_metric=_experiment_metric(experiment),
        experiment_conclusion=first_text(experiment, "conclusion", "interpretation"),
        experiment_fidelity=_experiment_fidelity(experiment),
        experiment_official_score=_experiment_official_score(experiment),
        experiment_resulting_state=scalar_text(experiment.get("resulting_state")),
        experiment_evidence_count=_experiment_evidence_count(experiment),
        best_metric=best_metric,
        best_experiment_id=best_experiment_id,
        best_state_id=best_state_id,
    )
