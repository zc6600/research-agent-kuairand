#!/usr/bin/env python3
"""CatBoost ranker for KuaiRand-Pure with native categorical handling and group ranking."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from catboost import CatBoostClassifier, CatBoostRanker, Pool

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition_data" / "data"
sys.path.insert(0, str(ROOT / "starter_kit"))
from evaluate import evaluate  # noqa: E402


def medium_user(user_id: str) -> bool:
    return int(hashlib.blake2b(user_id.encode(), digest_size=4).hexdigest(), 16) % 4 == 0


def clean_metrics(metrics: dict) -> dict:
    return {k: int(v) if k in ("users", "rows") else float(v) for k, v in metrics.items()}


def load_data():
    # 1. Load user side features
    user_features = {}
    with (DATA / "user_features_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            u = r["user_id"]
            user_features[u] = {
                "active_degree": r["user_active_degree"] or "UNK",
                "is_lowactive": r["is_lowactive_period"] or "UNK",
                "is_live_streamer": r["is_live_streamer"] or "UNK",
                "is_video_author": r["is_video_author"] or "UNK",
                "follow_range": r["follow_user_num_range"] or "UNK",
                "fans_range": r["fans_user_num_range"] or "UNK",
                "friend_range": r["friend_user_num_range"] or "UNK",
                "register_range": r["register_days_range"] or "UNK",
                **{f"onehot_{i}": r[f"onehot_feat{i}"] or "UNK" for i in range(18)},
            }

    # 2. Load video side features
    video_features = {}
    with (DATA / "video_features_basic_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            v = r["video_id"]
            tag_raw = r["tag"] or "UNK"
            primary_tag = tag_raw.split(",")[0] if tag_raw else "UNK"
            w = float(r["server_width"] or 0)
            h = float(r["server_height"] or 0)
            aspect_ratio = (w / h) if h > 0 else 0.0
            video_features[v] = {
                "author_id": r["author_id"] or "UNK",
                "video_type": r["video_type"] or "UNK",
                "upload_type": r["upload_type"] or "UNK",
                "music_type": r["music_type"] or "UNK",
                "primary_tag": primary_tag,
                "aspect_ratio": aspect_ratio,
            }

    dur_cuts = np.array([15000, 30000, 45000, 60000, 90000, 120000, 180000, 300000])
    files = {
        "train": "log_standard_4_08_to_4_21_pure.csv",
        "valid": "log_public_4_22_to_4_28_pure.csv",
    }

    feature_names = [
        "user_id", "video_id", "author_id", "tab", "dur_bucket",
        "hour", "weekday", "video_type", "upload_type", "music_type", "primary_tag",
        "active_degree", "is_lowactive", "is_live_streamer", "is_video_author",
        "follow_range", "fans_range", "friend_range", "register_range",
        *[f"onehot_{i}" for i in range(18)],
        "duration_log", "aspect_ratio",
    ]
    cat_feature_names = [
        "user_id", "video_id", "author_id", "tab", "dur_bucket",
        "hour", "weekday", "video_type", "upload_type", "music_type", "primary_tag",
        "active_degree", "is_lowactive", "is_live_streamer", "is_video_author",
        "follow_range", "fans_range", "friend_range", "register_range",
        *[f"onehot_{i}" for i in range(18)],
    ]

    splits = {}
    for split, filename in files.items():
        rows = []
        labels = []
        user_ids = []
        durations = []
        with (DATA / filename).open(newline="") as fh:
            for r in csv.DictReader(fh):
                u = r["user_id"]
                v = r["video_id"]
                vfeat = video_features.get(v, {
                    "author_id": "UNK", "video_type": "UNK", "upload_type": "UNK",
                    "music_type": "UNK", "primary_tag": "UNK", "aspect_ratio": 0.0,
                })
                ufeat = user_features.get(u, {
                    "active_degree": "UNK", "is_lowactive": "UNK", "is_live_streamer": "UNK",
                    "is_video_author": "UNK", "follow_range": "UNK", "fans_range": "UNK",
                    "friend_range": "UNK", "register_range": "UNK",
                    **{f"onehot_{i}": "UNK" for i in range(18)},
                })
                dur = float(r["duration_ms"] or 0)
                dur_bucket = str(int(np.searchsorted(dur_cuts, dur)))
                date = int(r["date"])
                weekday = str((date - 20220404) % 7)
                hour = str(int(r["hourmin"] or 0) // 100)
                tab = r["tab"] or "UNK"

                row = [
                    u, v, vfeat["author_id"], tab, dur_bucket,
                    hour, weekday, vfeat["video_type"], vfeat["upload_type"],
                    vfeat["music_type"], vfeat["primary_tag"],
                    ufeat["active_degree"], ufeat["is_lowactive"], ufeat["is_live_streamer"],
                    ufeat["is_video_author"], ufeat["follow_range"], ufeat["fans_range"],
                    ufeat["friend_range"], ufeat["register_range"],
                    *[ufeat[f"onehot_{i}"] for i in range(18)],
                    np.log1p(dur), vfeat["aspect_ratio"],
                ]
                rows.append(row)
                labels.append(1 if r["long_view"] == "1" else 0)
                user_ids.append(u)
        splits[split] = {
            "X": rows,
            "y": labels,
            "users": user_ids,
        }

    return splits, feature_names, cat_feature_names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=300)
    parser.add_argument("--learning_rate", type=float, default=0.1)
    parser.add_argument("--depth", type=int, default=6)
    parser.add_argument("--loss", choices=("Logloss", "PairLogit", "YetiRank"), default="Logloss")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    started = time.time()
    splits, feature_names, cat_feature_names = load_data()
    print(f"Loaded {len(splits['train']['y'])} train rows, {len(splits['valid']['y'])} valid rows.")

    # Medium filter
    uva = splits["valid"]["users"]
    yva = splits["valid"]["y"]
    xva = splits["valid"]["X"]
    med_mask = [medium_user(u) for u in uva]
    xmed = [x for x, keep in zip(xva, med_mask) if keep]
    ymed = [y for y, keep in zip(yva, med_mask) if keep]
    umed = [u for u, keep in zip(uva, med_mask) if keep]

    train_pool = Pool(
        data=splits["train"]["X"],
        label=splits["train"]["y"],
        cat_features=cat_feature_names,
        feature_names=feature_names,
    )
    med_pool = Pool(
        data=xmed,
        label=ymed,
        cat_features=cat_feature_names,
        feature_names=feature_names,
    )

    print(f"Training CatBoost with loss={args.loss}, iters={args.iterations}, lr={args.learning_rate}...")
    model = CatBoostClassifier(
        iterations=args.iterations,
        learning_rate=args.learning_rate,
        depth=args.depth,
        loss_function=args.loss,
        random_seed=args.seed,
        task_type="CPU",
        thread_count=4,
        verbose=50,
    )
    model.fit(train_pool, eval_set=med_pool, early_stopping_rounds=40)

    # Evaluate on Medium
    med_preds = model.predict_proba(med_pool)[:, 1]
    med_metrics = clean_metrics(evaluate(umed, ymed, med_preds))
    print(f"Medium score: {med_metrics}")

    full_metrics = None
    if args.full:
        full_pool = Pool(
            data=xva,
            label=yva,
            cat_features=cat_feature_names,
            feature_names=feature_names,
        )
        full_preds = model.predict_proba(full_pool)[:, 1]
        full_metrics = clean_metrics(evaluate(uva, yva, full_preds))
        print(f"Full score: {full_metrics}")

    payload = {
        "model": "CatBoost",
        "iterations": args.iterations,
        "learning_rate": args.learning_rate,
        "depth": args.depth,
        "loss": args.loss,
        "best_iteration": model.get_best_iteration(),
        "medium": med_metrics,
        "full": full_metrics,
        "elapsed_seconds": time.time() - started,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
