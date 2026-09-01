"""Callable interface for the gemini-3.7-flash heterogeneous-subagent baseline."""

from .baseline_api import (
    evaluate_scores,
    load_dataset,
    popularity_scores,
    project_root,
    run_popularity_baseline,
    score_rows,
    smoke_result,
)

__all__ = [
    "evaluate_scores",
    "load_dataset",
    "popularity_scores",
    "project_root",
    "run_popularity_baseline",
    "score_rows",
    "smoke_result",
]
