"""Callable interface for the direct Codex Agent KuaiRand baseline."""

from .baseline_api import (
    evaluate_scores,
    fm_pairwise_scores,
    fm_scores,
    load_dataset,
    popularity_scores,
    project_root,
    run_fm_baseline,
    run_fm_pairwise_baseline,
    run_popularity_baseline,
    score_rows,
    score_rows_fm,
    score_rows_fm_pairwise,
    smoke_result,
)

__all__ = [
    "evaluate_scores",
    "fm_pairwise_scores",
    "fm_scores",
    "load_dataset",
    "popularity_scores",
    "project_root",
    "run_fm_baseline",
    "run_fm_pairwise_baseline",
    "run_popularity_baseline",
    "score_rows",
    "score_rows_fm",
    "score_rows_fm_pairwise",
    "smoke_result",
]
