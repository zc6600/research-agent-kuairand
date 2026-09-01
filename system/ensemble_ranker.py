#!/usr/bin/env python3
"""Medium-selected blend of the rich FM and content target encoder."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from fm_ranker import evaluate, load_rows, medium_user, read_side_features, run
from train_evaluate import VARIANTS, load_video_features, score_rows, train_stats


def standardized(values, mean=None, std=None):
    arr = np.asarray(values, dtype=np.float64)
    mean = float(arr.mean()) if mean is None else mean
    std = float(arr.std()) if std is None else std
    return (arr - mean) / max(std, 1e-8), mean, std


def clean(metrics):
    return {k: int(v) if k in ("users", "rows") else float(v) for k, v in metrics.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    started = time.time()

    videos, users = read_side_features()
    rows = load_rows(videos, users)
    model, encoded, fm_detail = run(rows, "rich", 30, args.seed)
    xva, yva, uva = encoded["valid"]
    fm_all = model.predict(xva)

    te_videos = load_video_features()
    config = VARIANTS["content"]
    stats, global_rate, _ = train_stats(te_videos, config.keys())
    te_users, te_labels, te_all = score_rows(te_videos, stats, global_rate, config, "full")
    if te_users != uva or not np.array_equal(np.asarray(te_labels), yva):
        raise RuntimeError("FM and target-encoder validation rows are not aligned")

    mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    fm_med, fm_mean, fm_std = standardized(fm_all[mask])
    te_med, te_mean, te_std = standardized(np.asarray(te_all)[mask])
    medium_results = {}
    for alpha in (0.0, 0.05, 0.10, 0.20, 0.30):
        score = (1 - alpha) * fm_med + alpha * te_med
        medium_results[str(alpha)] = clean(evaluate(
            [u for u, keep in zip(uva, mask) if keep], yva[mask], score,
        ))
    selected = max(medium_results, key=lambda a: medium_results[a]["primary"])
    alpha = float(selected)
    fm_full, _, _ = standardized(fm_all, fm_mean, fm_std)
    te_full, _, _ = standardized(te_all, te_mean, te_std)
    full = clean(evaluate(uva, yva, (1 - alpha) * fm_full + alpha * te_full))
    payload = {
        "experiment": "fm_content_blend", "seed": args.seed,
        "fm_medium_best_epoch": fm_detail["best_medium_epoch"],
        "normalization_fitted_on": "stable 25% complete-user Medium slice",
        "medium_results": medium_results, "selected_alpha": alpha, "full": full,
        "elapsed_seconds": time.time() - started,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(rendered)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
