#!/usr/bin/env python3
"""Leakage-safe historical target-encoding ranker for curated KuaiRand-Pure.

The script reads only the managed training and public-validation files. It uses
the organizer's evaluator unchanged and preserves validation row order.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition_data" / "data"
sys.path.insert(0, str(ROOT / "starter_kit"))
from evaluate import evaluate  # noqa: E402


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def medium_user(user_id: str) -> bool:
    """Stable 25% user sample, preserving complete evaluator groups."""
    return int(hashlib.blake2b(user_id.encode(), digest_size=4).hexdigest(), 16) % 4 == 0


def load_video_features() -> dict[str, tuple[str, str, str, str]]:
    out = {}
    with (DATA / "video_features_basic_pure.csv").open(newline="") as fh:
        for row in csv.DictReader(fh):
            out[row["video_id"]] = (
                row["author_id"] or "UNK",
                row["video_type"] or "UNK",
                row["music_type"] or "UNK",
                row["tag"] or "UNK",
            )
    return out


def duration_bucket(value: str) -> str:
    # Fixed log-scale boundaries avoid learning preprocessing from validation.
    ms = max(float(value or 0), 1.0)
    return str(min(19, max(0, int(math.log2(ms / 5000.0) * 3 + 6))))


def row_features(row: dict[str, str], videos: dict[str, tuple[str, str, str, str]]):
    user, video = row["user_id"], row["video_id"]
    author, video_type, music_type, tag = videos.get(video, ("UNK",) * 4)
    tab = row["tab"] or "UNK"
    dur = duration_bucket(row["duration_ms"])
    hour = str(int(row["hourmin"] or 0) // 100)
    return {
        "item": video,
        "author": author,
        "duration": dur,
        "tab": tab,
        "hour": hour,
        "tag": tag,
        "video_type": video_type,
        "music_type": music_type,
        "user_item": (user, video),
        "user_author": (user, author),
        "user_duration": (user, dur),
        "user_tab": (user, tab),
        "item_tab": (video, tab),
        "author_tab": (author, tab),
    }


VARIANTS = {
    # weights multiply deviations from the global log-odds; priors are pseudo-counts.
    "content": {
        "item": (1.00, 20), "author": (0.45, 50), "duration": (0.80, 300),
        "tab": (0.35, 300), "hour": (0.15, 500), "tag": (0.20, 100),
        "video_type": (0.15, 500), "music_type": (0.10, 500),
    },
    "interactions": {
        "item": (0.85, 20), "author": (0.35, 50), "duration": (0.70, 300),
        "tab": (0.25, 300), "hour": (0.10, 500), "tag": (0.15, 100),
        "user_item": (0.80, 4), "user_author": (0.55, 8),
        "user_duration": (0.65, 10), "user_tab": (0.25, 12),
    },
    "crosses": {
        "item": (0.70, 20), "author": (0.25, 50), "duration": (0.65, 300),
        "tab": (0.20, 300), "hour": (0.10, 500), "tag": (0.12, 100),
        "user_item": (0.85, 4), "user_author": (0.60, 8),
        "user_duration": (0.70, 10), "user_tab": (0.25, 12),
        "item_tab": (0.35, 10), "author_tab": (0.20, 20),
    },
    "personal": {
        "item": (0.55, 20), "author": (0.20, 50), "duration": (0.50, 300),
        "tab": (0.15, 300), "hour": (0.08, 500),
        "user_item": (1.10, 3), "user_author": (0.75, 6),
        "user_duration": (0.85, 8), "user_tab": (0.35, 10),
        "item_tab": (0.30, 8),
    },
}


def train_stats(videos, fields):
    stats = {name: defaultdict(lambda: [0, 0]) for name in fields}
    positives = rows = 0
    path = DATA / "log_standard_4_08_to_4_21_pure.csv"
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            y = 0 if row["long_view"] == "0" else 1
            feats = row_features(row, videos)
            positives += y
            rows += 1
            for name in fields:
                cell = stats[name][feats[name]]
                cell[0] += y
                cell[1] += 1
    return stats, positives / rows, rows


def score_rows(videos, stats, global_rate, config, mode):
    users, labels, scores = [], [], []
    base = logit(global_rate)
    path = DATA / "log_public_4_22_to_4_28_pure.csv"
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            if mode == "medium" and not medium_user(row["user_id"]):
                continue
            feats = row_features(row, videos)
            score = base
            for name, (weight, prior) in config.items():
                pos, count = stats[name].get(feats[name], (0, 0))
                rate = (pos + prior * global_rate) / (count + prior)
                score += weight * (logit(rate) - base)
            users.append(row["user_id"])
            labels.append(0 if row["long_view"] == "0" else 1)
            scores.append(score)
    return users, labels, scores


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("medium", "full"), default="medium")
    parser.add_argument("--variant", choices=tuple(VARIANTS) + ("all",), default="all")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.mode == "full" and args.variant == "all":
        parser.error("Full evaluation requires one preselected --variant")

    started = time.time()
    videos = load_video_features()
    names = list(VARIANTS) if args.variant == "all" else [args.variant]
    fields = set().union(*(VARIANTS[name].keys() for name in names))
    stats, global_rate, train_rows = train_stats(videos, fields)
    results = {}
    for name in names:
        users, labels, scores = score_rows(videos, stats, global_rate, VARIANTS[name], args.mode)
        results[name] = evaluate(users, labels, scores)
    payload = {
        "experiment": "historical_target_encoding_ranker",
        "mode": args.mode,
        "variant": args.variant,
        "train_rows": train_rows,
        "train_positive_rate": global_rate,
        "validation_selection": "stable blake2b 25% complete-user sample" if args.mode == "medium" else "all public validation rows",
        "results": results,
        "config": {name: VARIANTS[name] for name in names},
        "elapsed_seconds": time.time() - started,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
