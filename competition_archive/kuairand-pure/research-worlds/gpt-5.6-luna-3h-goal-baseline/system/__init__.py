"""Callable interface for the gpt-5.6-luna KuaiRand baseline."""

from .baseline_api import (
    evaluate_scores,
    load_dataset,
    popularity_scores,
    project_root,
    run_optimized_ranker,
    run_popularity_baseline,
    score_rows,
    smoke_result,
)

__all__ = [
    "evaluate_scores",
    "load_dataset",
    "popularity_scores",
    "project_root",
    "run_optimized_ranker",
    "run_popularity_baseline",
    "score_rows",
    "smoke_result",
]
