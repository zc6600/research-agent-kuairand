"""Small, callable KuaiRand-Pure baseline API.

The project keeps the official starter kit as the metric and data contract.
This module provides a narrow API that can be imported by tests, notebooks, or
future research-agent cycles without going through a shell script.
"""

from __future__ import annotations

import collections
import csv
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import TypedDict

import numpy as np

KuaiRandRow = tuple[int, str, str, str, str, float, int]


class ScoreRecord(TypedDict):
    row_id: int
    user_id: str
    video_id: str
    score: float


FM_FIELDS = ("user_id", "video_id", "author_id", "tab", "dur_bucket")


def _read_rows(path: Path, video_authors: dict[str, str]) -> list[KuaiRandRow]:
    """Read one hidden-test-free log file into the starter-kit row shape."""

    rows: list[KuaiRandRow] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                (
                    int(row["date"]),
                    row["user_id"],
                    row["video_id"],
                    video_authors.get(row["video_id"], "UNK"),
                    row["tab"],
                    float(row["duration_ms"]),
                    1 if row["long_view"] != "0" else 0,
                )
            )
    return rows


def _load_curated_dataset(data_dir: Path) -> dict[str, list[KuaiRandRow]] | None:
    """Load the managed train/public view when the full raw eval file is absent."""

    train_path = data_dir / "log_standard_4_08_to_4_21_pure.csv"
    valid_path = data_dir / "log_public_4_22_to_4_28_pure.csv"
    if not train_path.is_file() or not valid_path.is_file():
        return None

    video_authors: dict[str, str] = {}
    video_path = data_dir / "video_features_basic_pure.csv"
    with video_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            video_authors[row["video_id"]] = row["author_id"]

    splits = {
        "train": _read_rows(train_path, video_authors),
        "valid": _read_rows(valid_path, video_authors),
    }
    random_path = data_dir / "log_random_4_22_to_4_28_pure.csv"
    if random_path.is_file():
        splits["random_valid"] = _read_rows(random_path, video_authors)
    return splits


def _sigmoid(values: np.ndarray) -> np.ndarray:
    """Numerically stable sigmoid used by the numpy-only FM implementation."""

    return 1.0 / (1.0 + np.exp(-np.clip(values, -30.0, 30.0)))


def _encode_fm_rows(
    train_rows: Sequence[KuaiRandRow],
    other_rows: Sequence[KuaiRandRow],
    extra_fields: Sequence[str] = (),
) -> tuple[np.ndarray, np.ndarray, int]:
    """Encode FM fields using train-only vocabularies.

    Unknown categories get a per-field UNK bucket.  In particular, no value
    from the target split can create a train-time category, which keeps this
    helper safe for scoring a future split.  Optional fields are explicit
    user/item crosses used only by the experimental pairwise model.
    """

    supported_extra_fields = {
        "user_tab",
        "user_author",
        "user_video",
        "video_tab",
        "author_tab",
    }
    extra_fields = tuple(extra_fields)
    unknown_extra_fields = set(extra_fields) - supported_extra_fields
    if unknown_extra_fields:
        raise ValueError(
            "unsupported extra FM fields: " + ", ".join(sorted(unknown_extra_fields))
        )

    if train_rows:
        durations = np.asarray([row[5] for row in train_rows], dtype=np.float64)
        edges = np.quantile(durations, np.linspace(0.0, 1.0, 11)[1:-1])
    else:
        edges = np.empty(0, dtype=np.float64)

    def raw(row: KuaiRandRow) -> tuple[str, ...]:
        duration_bucket = int(np.searchsorted(edges, row[5]))
        values = [row[1], row[2], row[3], row[4], str(duration_bucket)]
        cross_values = {
            "user_tab": f"{row[1]}::{row[4]}",
            "user_author": f"{row[1]}::{row[3]}",
            "user_video": f"{row[1]}::{row[2]}",
            "video_tab": f"{row[2]}::{row[4]}",
            "author_tab": f"{row[3]}::{row[4]}",
        }
        values.extend(cross_values[field] for field in extra_fields)
        return tuple(values)

    field_count = len(FM_FIELDS) + len(extra_fields)
    vocabs: list[dict[str, int]] = [dict() for _ in range(field_count)]
    for row in train_rows:
        for field, value in enumerate(raw(row)):
            if value not in vocabs[field]:
                vocabs[field][value] = len(vocabs[field])

    unknown = [len(vocab) for vocab in vocabs]
    dimensions = [len(vocab) + 1 for vocab in vocabs]
    offsets = np.cumsum([0, *dimensions[:-1]]).astype(np.int32)

    def encode(rows: Sequence[KuaiRandRow]) -> np.ndarray:
        encoded = np.empty((len(rows), field_count), dtype=np.int32)
        for row_id, row in enumerate(rows):
            for field, value in enumerate(raw(row)):
                encoded[row_id, field] = (
                    vocabs[field].get(value, unknown[field]) + offsets[field]
                )
        return encoded

    return encode(train_rows), encode(other_rows), int(sum(dimensions))


class _FactorizationMachine:
    """Small numpy FM matching the starter kit's official baseline."""

    def __init__(
        self,
        dimension: int,
        *,
        factors: int,
        learning_rate: float,
        l2: float,
        seed: int,
    ) -> None:
        rng = np.random.default_rng(seed)
        self.v = rng.normal(0.0, 0.01, (dimension, factors)).astype(np.float32)
        self.w = np.zeros(dimension, dtype=np.float32)
        self.bias = np.float32(0.0)
        self.learning_rate = learning_rate
        self.l2 = l2
        self.m_v = np.zeros_like(self.v)
        self.s_v = np.zeros_like(self.v)
        self.m_w = np.zeros_like(self.w)
        self.s_w = np.zeros_like(self.w)
        self.step_count = 0

    def logits(self, features: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        embeddings = self.v[features]
        summed = embeddings.sum(axis=1)
        interactions = 0.5 * (
            (summed**2).sum(axis=1) - (embeddings**2).sum(axis=(1, 2))
        )
        return self.bias + self.w[features].sum(axis=1) + interactions, embeddings, summed

    def train_step(self, features: np.ndarray, labels: np.ndarray) -> float:
        if len(labels) == 0:
            return 0.0

        logits, embeddings, summed = self.logits(features)
        probabilities = _sigmoid(logits)
        gradient = ((probabilities - labels) / len(labels)).astype(np.float32)

        gradient_v = np.zeros_like(self.v)
        gradient_w = np.zeros_like(self.w)
        np.add.at(gradient_w, features, gradient[:, None])
        np.add.at(
            gradient_v,
            features,
            gradient[:, None, None] * (summed[:, None, :] - embeddings),
        )
        gradient_v += self.l2 * self.v
        gradient_w += self.l2 * self.w

        self.step_count += 1
        beta_1, beta_2, epsilon = 0.9, 0.999, 1e-8
        for parameter, grad, first, second in (
            (self.v, gradient_v, self.m_v, self.s_v),
            (self.w, gradient_w, self.m_w, self.s_w),
        ):
            first *= beta_1
            first += (1.0 - beta_1) * grad
            second *= beta_2
            second += (1.0 - beta_2) * (grad * grad)
            first_hat = first / (1.0 - beta_1**self.step_count)
            second_hat = second / (1.0 - beta_2**self.step_count)
            parameter -= self.learning_rate * first_hat / (np.sqrt(second_hat) + epsilon)
        self.bias -= self.learning_rate * gradient.sum()

        loss = -np.mean(
            labels * np.log(probabilities + 1e-9)
            + (1.0 - labels) * np.log(1.0 - probabilities + 1e-9)
        )
        return float(loss)

    def pairwise_step(
        self, positive_features: np.ndarray, negative_features: np.ndarray
    ) -> float:
        """Take one BPR/logistic pairwise step over same-user pairs."""

        if len(positive_features) == 0:
            return 0.0
        positive_logits, positive_embeddings, positive_summed = self.logits(
            positive_features
        )
        negative_logits, negative_embeddings, negative_summed = self.logits(
            negative_features
        )
        differences = positive_logits - negative_logits
        pair_probability = _sigmoid(-differences)
        scale = np.float32(1.0 / len(differences))
        positive_gradient = (-pair_probability * scale).astype(np.float32)
        negative_gradient = (pair_probability * scale).astype(np.float32)

        gradient_v = np.zeros_like(self.v)
        gradient_w = np.zeros_like(self.w)
        np.add.at(gradient_w, positive_features, positive_gradient[:, None])
        np.add.at(gradient_w, negative_features, negative_gradient[:, None])
        np.add.at(
            gradient_v,
            positive_features,
            positive_gradient[:, None, None]
            * (positive_summed[:, None, :] - positive_embeddings),
        )
        np.add.at(
            gradient_v,
            negative_features,
            negative_gradient[:, None, None]
            * (negative_summed[:, None, :] - negative_embeddings),
        )
        gradient_v += self.l2 * self.v
        gradient_w += self.l2 * self.w

        self.step_count += 1
        beta_1, beta_2, epsilon = 0.9, 0.999, 1e-8
        for parameter, grad, first, second in (
            (self.v, gradient_v, self.m_v, self.s_v),
            (self.w, gradient_w, self.m_w, self.s_w),
        ):
            first *= beta_1
            first += (1.0 - beta_1) * grad
            second *= beta_2
            second += (1.0 - beta_2) * (grad * grad)
            first_hat = first / (1.0 - beta_1**self.step_count)
            second_hat = second / (1.0 - beta_2**self.step_count)
            parameter -= self.learning_rate * first_hat / (np.sqrt(second_hat) + epsilon)

        return float(np.mean(np.logaddexp(0.0, -differences)))

    def predict(self, features: np.ndarray, batch_size: int = 200_000) -> np.ndarray:
        if len(features) == 0:
            return np.empty(0, dtype=np.float32)
        batches = [
            self.logits(features[start : start + batch_size])[0]
            for start in range(0, len(features), batch_size)
        ]
        return np.concatenate(batches)


def fm_scores(
    train_rows: Sequence[KuaiRandRow],
    target_rows: Sequence[KuaiRandRow],
    *,
    validation_rows: Sequence[KuaiRandRow] | None = None,
    factors: int = 16,
    learning_rate: float = 0.001,
    epochs: int = 40,
    batch_size: int = 8192,
    patience: int = 4,
    seed: int = 0,
) -> list[float]:
    """Return official-FM scores for ``target_rows``.

    Training uses only ``train_rows``.  If ``validation_rows`` is provided,
    it is used solely for early stopping/model selection, matching the
    starter-kit protocol.  Target rows never participate in fitting or model
    selection.
    """

    train = list(train_rows)
    target = list(target_rows)
    validation = list(validation_rows) if validation_rows is not None else None
    train_features, target_features, dimension = _encode_fm_rows(train, target)
    validation_features = None
    if validation is not None:
        _, validation_features, _ = _encode_fm_rows(train, validation)

    labels = np.asarray([row[6] for row in train], dtype=np.float32)
    model = _FactorizationMachine(
        dimension,
        factors=factors,
        learning_rate=learning_rate,
        l2=1e-6,
        seed=seed,
    )
    rng = np.random.default_rng(seed)
    best_state: tuple[np.ndarray, np.ndarray, np.float32] | None = None
    best_primary = -np.inf
    bad_epochs = 0

    for _ in range(epochs):
        order = rng.permutation(len(labels))
        for start in range(0, len(order), batch_size):
            batch = order[start : start + batch_size]
            model.train_step(train_features[batch], labels[batch])

        if validation is None or validation_features is None:
            continue
        from starter_kit.evaluate import evaluate

        validation_result = evaluate(
            [row[1] for row in validation],
            [row[6] for row in validation],
            model.predict(validation_features),
        )
        primary = float(validation_result["primary"])
        if primary > best_primary + 1e-5:
            best_primary = primary
            bad_epochs = 0
            best_state = (model.v.copy(), model.w.copy(), np.float32(model.bias))
        else:
            bad_epochs += 1
            if bad_epochs >= patience:
                break

    if best_state is not None:
        model.v, model.w, model.bias = best_state

    return [float(score) for score in model.predict(target_features)]


def _same_user_pair_indices(
    train_rows: Sequence[KuaiRandRow],
    rng: np.random.Generator,
    negatives_per_positive: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Sample train-only same-user negatives for each positive."""

    if negatives_per_positive < 1:
        raise ValueError("negatives_per_positive must be at least 1")

    positives: dict[str, list[int]] = collections.defaultdict(list)
    negatives: dict[str, list[int]] = collections.defaultdict(list)
    for row_id, row in enumerate(train_rows):
        (positives if row[6] else negatives)[row[1]].append(row_id)

    positive_indices: list[int] = []
    negative_indices: list[int] = []
    for user_id, user_positives in positives.items():
        user_negatives = negatives.get(user_id)
        if not user_negatives:
            continue
        positive_indices.extend(user_positives * negatives_per_positive)
        draws = rng.integers(
            0, len(user_negatives), size=len(user_positives) * negatives_per_positive
        )
        negative_indices.extend(user_negatives[int(index)] for index in draws)
    if not positive_indices:
        return np.empty(0, dtype=np.int32), np.empty(0, dtype=np.int32)
    order = rng.permutation(len(positive_indices))
    return (
        np.asarray(positive_indices, dtype=np.int32)[order],
        np.asarray(negative_indices, dtype=np.int32)[order],
    )


def fm_pairwise_scores(
    train_rows: Sequence[KuaiRandRow],
    target_rows: Sequence[KuaiRandRow],
    *,
    validation_rows: Sequence[KuaiRandRow] | None = None,
    factors: int = 8,
    learning_rate: float = 0.00025,
    epochs: int = 40,
    batch_size: int = 8192,
    patience: int = 4,
    seed: int = 0,
    negatives_per_positive: int = 1,
    extra_fields: Sequence[str] = (),
) -> list[float]:
    """Return FM scores trained on sampled within-user pairwise preferences."""

    train = list(train_rows)
    target = list(target_rows)
    validation = list(validation_rows) if validation_rows is not None else None
    train_features, target_features, dimension = _encode_fm_rows(
        train, target, extra_fields
    )
    validation_features = None
    if validation is not None:
        _, validation_features, _ = _encode_fm_rows(train, validation, extra_fields)

    model = _FactorizationMachine(
        dimension,
        factors=factors,
        learning_rate=learning_rate,
        l2=1e-6,
        seed=seed,
    )
    rng = np.random.default_rng(seed)
    best_state: tuple[np.ndarray, np.ndarray, np.float32] | None = None
    best_primary = -np.inf
    bad_epochs = 0

    for _ in range(epochs):
        positive_indices, negative_indices = _same_user_pair_indices(
            train, rng, negatives_per_positive
        )
        for start in range(0, len(positive_indices), batch_size):
            stop = start + batch_size
            model.pairwise_step(
                train_features[positive_indices[start:stop]],
                train_features[negative_indices[start:stop]],
            )

        if validation is None or validation_features is None:
            continue
        from starter_kit.evaluate import evaluate

        validation_result = evaluate(
            [row[1] for row in validation],
            [row[6] for row in validation],
            model.predict(validation_features),
        )
        primary = float(validation_result["primary"])
        if primary > best_primary + 1e-5:
            best_primary = primary
            bad_epochs = 0
            best_state = (model.v.copy(), model.w.copy(), np.float32(model.bias))
        else:
            bad_epochs += 1
            if bad_epochs >= patience:
                break

    if best_state is not None:
        model.v, model.w, model.bias = best_state
    return [float(score) for score in model.predict(target_features)]


def project_root() -> Path:
    """Return this child research repository root."""

    return Path(__file__).resolve().parents[1]


def default_data_dir() -> Path:
    """Return the local development data directory expected by this project."""

    return project_root() / "competition_data" / "data"


def load_dataset(data_dir: str | Path | None = None) -> dict[str, list[KuaiRandRow]]:
    selected = default_data_dir() if data_dir is None else Path(data_dir)
    curated = _load_curated_dataset(selected)
    if curated is not None:
        return curated
    raise FileNotFoundError(
        "expected the hidden-test-free curated data view with train and "
        f"public-validation CSVs under {selected}; refusing an uncurated "
        "starter-kit path"
    )


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


def score_rows_fm(
    train_rows: Sequence[KuaiRandRow],
    target_rows: Sequence[KuaiRandRow],
    *,
    validation_rows: Sequence[KuaiRandRow] | None = None,
    factors: int = 16,
    learning_rate: float = 0.001,
    epochs: int = 40,
    batch_size: int = 8192,
    patience: int = 4,
    seed: int = 0,
) -> list[ScoreRecord]:
    """Return submission-shaped records scored by the official five-field FM."""

    scores = fm_scores(
        train_rows,
        target_rows,
        validation_rows=validation_rows,
        factors=factors,
        learning_rate=learning_rate,
        epochs=epochs,
        batch_size=batch_size,
        patience=patience,
        seed=seed,
    )
    return [
        {
            "row_id": row_id,
            "user_id": row[1],
            "video_id": row[2],
            "score": score,
        }
        for row_id, (row, score) in enumerate(zip(target_rows, scores, strict=True))
    ]


def score_rows_fm_pairwise(
    train_rows: Sequence[KuaiRandRow],
    target_rows: Sequence[KuaiRandRow],
    *,
    validation_rows: Sequence[KuaiRandRow] | None = None,
    factors: int = 8,
    learning_rate: float = 0.00025,
    epochs: int = 40,
    batch_size: int = 8192,
    patience: int = 4,
    seed: int = 0,
    negatives_per_positive: int = 1,
    extra_fields: Sequence[str] = (),
) -> list[ScoreRecord]:
    """Return submission-shaped scores from the within-user pairwise FM."""

    scores = fm_pairwise_scores(
        train_rows,
        target_rows,
        validation_rows=validation_rows,
        factors=factors,
        learning_rate=learning_rate,
        epochs=epochs,
        batch_size=batch_size,
        patience=patience,
        seed=seed,
        negatives_per_positive=negatives_per_positive,
        extra_fields=extra_fields,
    )
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


def run_fm_baseline(
    data_dir: str | Path | None = None,
    *,
    split: str = "valid",
    factors: int = 16,
    learning_rate: float = 0.001,
    epochs: int = 40,
    batch_size: int = 8192,
    patience: int = 4,
    seed: int = 0,
) -> dict[str, float | int]:
    """Train and evaluate the organizer's FM on a local development split.

    Public validation is the only model-selection split.  When scoring the
    hidden/test-shaped split, the model is still selected on ``valid`` rather
    than using any target labels.
    """

    splits = load_dataset(data_dir)
    if split not in splits:
        available = ", ".join(sorted(splits))
        raise ValueError(f"unknown split {split!r}; available splits: {available}")
    validation = splits.get("valid") if split != "valid" else splits["valid"]
    scores = fm_scores(
        splits["train"],
        splits[split],
        validation_rows=validation,
        factors=factors,
        learning_rate=learning_rate,
        epochs=epochs,
        batch_size=batch_size,
        patience=patience,
        seed=seed,
    )
    return evaluate_scores(splits[split], scores)


def run_fm_pairwise_baseline(
    data_dir: str | Path | None = None,
    *,
    split: str = "valid",
    factors: int = 8,
    learning_rate: float = 0.00025,
    epochs: int = 40,
    batch_size: int = 8192,
    patience: int = 4,
    seed: int = 0,
    negatives_per_positive: int = 1,
    extra_fields: Sequence[str] = (),
) -> dict[str, float | int]:
    """Train and evaluate the within-user pairwise FM on local data."""

    splits = load_dataset(data_dir)
    if split not in splits:
        available = ", ".join(sorted(splits))
        raise ValueError(f"unknown split {split!r}; available splits: {available}")
    scores = fm_pairwise_scores(
        splits["train"],
        splits[split],
        validation_rows=splits["valid"],
        factors=factors,
        learning_rate=learning_rate,
        epochs=epochs,
        batch_size=batch_size,
        patience=patience,
        seed=seed,
        negatives_per_positive=negatives_per_positive,
        extra_fields=extra_fields,
    )
    return evaluate_scores(splits[split], scores)


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
