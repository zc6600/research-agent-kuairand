#!/usr/bin/env python3
"""FM ranker adapted to the managed KuaiRand-Pure development-only layout."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition_data" / "data"
sys.path.insert(0, str(ROOT / "starter_kit"))
from baseline import FM  # noqa: E402
from evaluate import evaluate  # noqa: E402


def medium_user(user_id: str) -> bool:
    return int(hashlib.blake2b(user_id.encode(), digest_size=4).hexdigest(), 16) % 4 == 0


def read_side_features():
    videos = {}
    with (DATA / "video_features_basic_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            videos[r["video_id"]] = (
                r["author_id"] or "UNK", r["video_type"] or "UNK",
                r["music_type"] or "UNK", r["tag"] or "UNK",
            )
    users = {}
    with (DATA / "user_features_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            users[r["user_id"]] = (
                r["user_active_degree"] or "UNK", r["follow_user_num_range"] or "UNK",
                r["fans_user_num_range"] or "UNK", r["friend_user_num_range"] or "UNK",
                r["register_days_range"] or "UNK",
            )
    return videos, users


def load_rows(videos, users):
    result = {}
    files = {
        "train": "log_standard_4_08_to_4_21_pure.csv",
        "valid": "log_public_4_22_to_4_28_pure.csv",
    }
    for split, filename in files.items():
        rows = []
        with (DATA / filename).open(newline="") as fh:
            for r in csv.DictReader(fh):
                author, vtype, mtype, tag = videos.get(r["video_id"], ("UNK",) * 4)
                profile = users.get(r["user_id"], ("UNK",) * 5)
                duration = float(r["duration_ms"] or 0)
                dur_bucket = str(int(np.searchsorted(
                    np.array([15000, 30000, 45000, 60000, 90000, 120000, 180000, 300000]),
                    duration,
                )))
                date = int(r["date"])
                rows.append({
                    "user_id": r["user_id"], "video_id": r["video_id"], "author_id": author,
                    "tab": r["tab"] or "UNK", "dur_bucket": dur_bucket,
                    "hour": str(int(r["hourmin"] or 0) // 100),
                    "weekday": str((date - 20220404) % 7),
                    "video_type": vtype, "music_type": mtype, "tag": tag,
                    "active": profile[0], "follow_range": profile[1], "fans_range": profile[2],
                    "friend_range": profile[3], "register_range": profile[4],
                    "label": 0 if r["long_view"] == "0" else 1,
                })
        result[split] = rows
    return result


FIELD_SETS = {
    "base": ["user_id", "video_id", "author_id", "tab", "dur_bucket"],
    "video": [
        "user_id", "video_id", "author_id", "tab", "dur_bucket", "hour", "weekday",
        "video_type", "music_type", "tag",
    ],
    "profile": [
        "user_id", "video_id", "author_id", "tab", "dur_bucket", "active", "follow_range",
        "fans_range", "friend_range", "register_range",
    ],
    "rich": [
        "user_id", "video_id", "author_id", "tab", "dur_bucket", "hour", "weekday",
        "video_type", "music_type", "tag", "active", "follow_range", "fans_range",
        "friend_range", "register_range",
    ],
}


def encode(rows, fields):
    vocabs = [dict() for _ in fields]
    for row in rows["train"]:
        for i, name in enumerate(fields):
            value = row[name]
            if value not in vocabs[i]:
                vocabs[i][value] = len(vocabs[i])
    unknown = [len(v) for v in vocabs]
    dimensions = [len(v) + 1 for v in vocabs]
    offsets = np.cumsum([0] + dimensions[:-1]).astype(np.int32)
    encoded = {}
    for split, split_rows in rows.items():
        x = np.empty((len(split_rows), len(fields)), dtype=np.int32)
        y = np.empty(len(split_rows), dtype=np.float32)
        user_ids = []
        for n, row in enumerate(split_rows):
            for i, name in enumerate(fields):
                x[n, i] = vocabs[i].get(row[name], unknown[i]) + offsets[i]
            y[n] = row["label"]
            user_ids.append(row["user_id"])
        encoded[split] = (x, y, user_ids)
    return encoded, sum(dimensions)


def run(rows, representation, epochs, seed):
    fields = FIELD_SETS[representation]
    encoded, dim = encode(rows, fields)
    xtr, ytr, _ = encoded["train"]
    xva, yva, uva = encoded["valid"]
    mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    xmed, ymed = xva[mask], yva[mask]
    umed = [u for u, keep in zip(uva, mask) if keep]
    model = FM(dim, k=16, lr=0.001, seed=seed)
    rng = np.random.default_rng(seed)
    best = (-1.0, None, 0)
    history = []
    bad = 0
    for epoch in range(1, epochs + 1):
        order = rng.permutation(len(ytr))
        losses = []
        for start in range(0, len(order), 8192):
            idx = order[start:start + 8192]
            losses.append(model.step(xtr[idx], ytr[idx]))
        metrics = evaluate(umed, ymed, model.predict(xmed))
        history.append({
            "epoch": epoch, "loss": float(np.mean(losses)),
            **{key: int(value) if key in ("users", "rows") else float(value)
               for key, value in metrics.items()},
        })
        print(representation, history[-1], flush=True)
        if metrics["primary"] > best[0] + 1e-5:
            best = (metrics["primary"], (model.V.copy(), model.W.copy(), np.float32(model.b)), epoch)
            bad = 0
        else:
            bad += 1
            if bad >= 4:
                break
    model.V, model.W, model.b = best[1]
    return model, encoded, {
        "representation": representation, "fields": fields, "dimension": dim,
        "best_medium_epoch": best[2], "medium": history[best[2] - 1], "history": history,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--representation", choices=tuple(FIELD_SETS) + ("all",), default="all")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--full", action="store_true", help="evaluate one selected representation on full public validation")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.full and args.representation == "all":
        parser.error("--full requires one preselected representation")
    started = time.time()
    videos, users = read_side_features()
    rows = load_rows(videos, users)
    names = list(FIELD_SETS) if args.representation == "all" else [args.representation]
    results = {}
    for name in names:
        model, encoded, detail = run(rows, name, args.epochs, args.seed)
        if args.full:
            xva, yva, uva = encoded["valid"]
            detail["full"] = {
                key: int(value) if key in ("users", "rows") else float(value)
                for key, value in evaluate(uva, yva, model.predict(xva)).items()
            }
        results[name] = detail
    payload = {
        "experiment": "fm_representation_ablation", "seed": args.seed,
        "full_evaluation": args.full, "results": results,
        "elapsed_seconds": time.time() - started,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
