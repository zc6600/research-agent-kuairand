"""Small, callable KuaiRand-Pure baseline API.

The project keeps the official starter kit as the metric and data contract.
This module provides a narrow API that can be imported by tests, notebooks, or
future research-agent cycles without going through a shell script.
"""

from __future__ import annotations

import collections
from pathlib import Path
from typing import Iterable, Sequence, TypedDict


KuaiRandRow = tuple[int, str, str, str, str, float, int]


class ScoreRecord(TypedDict):
    row_id: int
    user_id: str
    video_id: str
    score: float


def project_root() -> Path:
    """Return this child research repository root."""

    return Path(__file__).resolve().parents[1]


def default_data_dir() -> Path:
    """Return the local development data directory expected by this project."""

    return project_root() / "competition_data" / "data"


def load_dataset(data_dir: str | Path | None = None) -> dict[str, list[KuaiRandRow]]:
    """Load KuaiRand-Pure splits through the official starter-kit loader."""

    from starter_kit.data import load

    selected = default_data_dir() if data_dir is None else Path(data_dir)
    return load(str(selected))


def popularity_scores(
    train_rows: Iterable[KuaiRandRow],
    target_rows: Sequence[KuaiRandRow],
    *,
    prior: float = 20.0,
) -> list[float]:
    """Score target rows with smoothed item long-view popularity from train rows."""

    positives: collections.Counter[str] = collections.Counter()
    impressions: collections.Counter[str] = collections.Counter()
    for row in train_rows:
        video_id = row[2]
        impressions[video_id] += 1
        positives[video_id] += row[6]

    total_impressions = sum(impressions.values())
    global_mean = (sum(positives.values()) / total_impressions) if total_impressions else 0.0

    def score(video_id: str) -> float:
        if impressions[video_id] == 0:
            return global_mean
        return (positives[video_id] + prior * global_mean) / (impressions[video_id] + prior)

    return [float(score(row[2])) for row in target_rows]


def score_rows(
    train_rows: Iterable[KuaiRandRow],
    target_rows: Sequence[KuaiRandRow],
    *,
    prior: float = 20.0,
) -> list[ScoreRecord]:
    """Return submission-shaped score records for a target split."""

    scores = popularity_scores(train_rows, target_rows, prior=prior)
    return [
        {
            "row_id": row_id,
            "user_id": row[1],
            "video_id": row[2],
            "score": score,
        }
        for row_id, (row, score) in enumerate(zip(target_rows, scores, strict=True))
    ]


def evaluate_scores(rows: Sequence[KuaiRandRow], scores: Sequence[float]) -> dict[str, float | int]:
    """Evaluate scores with the official GAUC/nDCG@5 implementation."""

    from starter_kit.evaluate import evaluate

    return evaluate([row[1] for row in rows], [row[6] for row in rows], list(scores))


def run_popularity_baseline(
    data_dir: str | Path | None = None,
    *,
    split: str = "valid",
    prior: float = 20.0,
) -> dict[str, float | int]:
    """Load data, score one split, and return official metrics."""

    splits = load_dataset(data_dir)
    if split not in splits:
        available = ", ".join(sorted(splits))
        raise ValueError(f"unknown split {split!r}; available splits: {available}")
    scores = popularity_scores(splits["train"], splits[split], prior=prior)
    return evaluate_scores(splits[split], scores)


def run_optimized_ranker(
    data_dir: str | Path | None = None,
    *,
    split: str = "valid",
    k: int = 16,
    lr: float = 0.001,
    epochs: int = 40,
    seed: int = 0,
) -> dict[str, float | int]:
    """Run the validated six-field FM ranker on one local development split."""

    splits = load_dataset(data_dir)
    if split not in splits:
        available = ", ".join(sorted(splits))
        raise ValueError(f"unknown split {split!r}; available splits: {available}")

    from starter_kit.baseline import run_fm

    result = run_fm(
        splits,
        k=k,
        lr=lr,
        epochs=epochs,
        seed=seed,
        verbose=False,
    )
    return {
        key: value.item() if hasattr(value, "item") else value
        for key, value in result[split].items()
    }


def smoke_rows() -> dict[str, list[KuaiRandRow]]:
    """Tiny deterministic dataset for interface smoke tests."""

    return {
        "train": [
            (20220408, "u1", "v1", "a1", "0", 1000.0, 1),
            (20220408, "u1", "v2", "a2", "0", 1000.0, 0),
            (20220409, "u2", "v1", "a1", "1", 900.0, 1),
            (20220409, "u2", "v3", "a3", "1", 900.0, 0),
        ],
        "valid": [
            (20220422, "u1", "v1", "a1", "0", 1000.0, 1),
            (20220422, "u1", "v2", "a2", "0", 1000.0, 0),
            (20220422, "u2", "v3", "a3", "1", 900.0, 0),
            (20220422, "u2", "v1", "a1", "1", 900.0, 1),
        ],
    }


def smoke_result() -> dict[str, float | int]:
    """Run a deterministic API smoke check without requiring local KuaiRand files."""

    splits = smoke_rows()
    scores = popularity_scores(splits["train"], splits["valid"], prior=1.0)
    return evaluate_scores(splits["valid"], scores)
