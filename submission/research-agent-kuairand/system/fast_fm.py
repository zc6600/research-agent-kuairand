#!/usr/bin/env python3
"""Systematic optimization and ablation for FM on KuaiRand-Pure.

Features:
- rich_all (38 fields)
- rich_cross (rich_all + pairwise categorical crosses: user_tab, item_tab, author_tab, tag_tab, hour_weekday)
- hyperparameter tuning for k, lr, l2, optimizer, and ensemble blending.
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

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition_data" / "data"
sys.path.insert(0, str(ROOT / "starter_kit"))
from evaluate import evaluate  # noqa: E402


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def medium_user(user_id: str) -> bool:
    return int(hashlib.blake2b(user_id.encode(), digest_size=4).hexdigest(), 16) % 4 == 0


def clean_metrics(metrics: dict) -> dict:
    return {k: int(v) if k in ("users", "rows") else float(v) for k, v in metrics.items()}


def read_features():
    videos = {}
    with (DATA / "video_features_basic_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            tag_raw = r["tag"] or "UNK"
            primary_tag = tag_raw.split(",")[0] if tag_raw else "UNK"
            w = float(r["server_width"] or 0)
            h = float(r["server_height"] or 0)
            aspect = "vert" if (h > 0 and w / h < 0.8) else "horiz"
            videos[r["video_id"]] = {
                "author_id": r["author_id"] or "UNK",
                "video_type": r["video_type"] or "UNK",
                "upload_type": r["upload_type"] or "UNK",
                "music_type": r["music_type"] or "UNK",
                "music_id": r["music_id"] or "UNK",
                "tag": primary_tag,
                "aspect": aspect,
            }
    users = {}
    with (DATA / "user_features_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            users[r["user_id"]] = {
                "active": r["user_active_degree"] or "UNK",
                "is_lowactive": r["is_lowactive_period"] or "UNK",
                "is_live_streamer": r["is_live_streamer"] or "UNK",
                "is_video_author": r["is_video_author"] or "UNK",
                "follow_range": r["follow_user_num_range"] or "UNK",
                "fans_range": r["fans_user_num_range"] or "UNK",
                "friend_range": r["friend_user_num_range"] or "UNK",
                "register_range": r["register_days_range"] or "UNK",
                **{f"onehot_{i}": r[f"onehot_feat{i}"] or "UNK" for i in range(18)},
            }
    return videos, users


def load_data(fields: list[str], include_crosses: bool = False):
    videos, users = read_features()
    dur_cuts = np.array([15000, 30000, 45000, 60000, 90000, 120000, 180000, 300000])
    files = {
        "train": "log_standard_4_08_to_4_21_pure.csv",
        "valid": "log_public_4_22_to_4_28_pure.csv",
    }
    raw = {}
    for split, fname in files.items():
        rows = []
        with (DATA / fname).open(newline="") as fh:
            for r in csv.DictReader(fh):
                u = r["user_id"]
                v = r["video_id"]
                vfeat = videos.get(v, {"author_id": "UNK", "video_type": "UNK", "upload_type": "UNK", "music_type": "UNK", "music_id": "UNK", "tag": "UNK", "aspect": "UNK"})
                ufeat = users.get(u, {"active": "UNK", "is_lowactive": "UNK", "is_live_streamer": "UNK", "is_video_author": "UNK", "follow_range": "UNK", "fans_range": "UNK", "friend_range": "UNK", "register_range": "UNK", **{f"onehot_{i}": "UNK" for i in range(18)}})
                dur = float(r["duration_ms"] or 0)
                dur_bucket = str(int(np.searchsorted(dur_cuts, dur)))
                date = int(r["date"])
                weekday = str((date - 20220404) % 7)
                hour = str(int(r["hourmin"] or 0) // 100)
                tab = r["tab"] or "UNK"

                feat_dict = {
                    "user_id": u, "video_id": v, "author_id": vfeat["author_id"],
                    "tab": tab, "dur_bucket": dur_bucket, "hour": hour, "weekday": weekday,
                    "video_type": vfeat["video_type"], "upload_type": vfeat["upload_type"],
                    "music_type": vfeat["music_type"], "music_id": vfeat["music_id"],
                    "tag": vfeat["tag"], "aspect": vfeat["aspect"],
                    **ufeat,
                    "label": 1 if r["long_view"] == "1" else 0,
                    "click": 1 if r.get("is_click", "0") == "1" else 0,
                }
                if include_crosses:
                    feat_dict["item_tab"] = f"{v}_{tab}"
                    feat_dict["author_tab"] = f"{vfeat['author_id']}_{tab}"
                    feat_dict["tag_tab"] = f"{vfeat['tag']}_{tab}"
                    feat_dict["hour_weekday"] = f"{weekday}_{hour}"
                    feat_dict["active_dur"] = f"{ufeat['active']}_{dur_bucket}"

                rows.append(feat_dict)
        raw[split] = rows

    actual_fields = [f for f in fields if f in raw["train"][0]]

    # Encode
    vocabs = [{} for _ in actual_fields]
    for r in raw["train"]:
        for i, f in enumerate(actual_fields):
            val = r[f]
            if val not in vocabs[i]:
                vocabs[i][val] = len(vocabs[i])

    dimensions = [len(v) + 1 for v in vocabs]
    offsets = np.cumsum([0] + dimensions[:-1]).astype(np.int32)
    dim = sum(dimensions)

    encoded = {}
    for split, srows in raw.items():
        n = len(srows)
        x = np.empty((n, len(actual_fields)), dtype=np.int32)
        y = np.empty(n, dtype=np.float32)
        u_list = []
        for row_idx, r in enumerate(srows):
            for i, f in enumerate(actual_fields):
                unk = len(vocabs[i])
                x[row_idx, i] = vocabs[i].get(r[f], unk) + offsets[i]
            y[row_idx] = r["label"]
            u_list.append(r["user_id"])
        encoded[split] = (x, y, u_list)

    return encoded, dim, actual_fields


class FastFM:
    def __init__(self, dim, k=16, lr=0.001, l2=1e-5, optimizer="adam", seed=0):
        rng = np.random.default_rng(seed)
        self.dim = dim
        self.k = k
        self.lr = lr
        self.l2 = l2
        self.optimizer = optimizer
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W = np.zeros(dim, dtype=np.float32)
        self.b = np.float32(0.0)

        # Optimizer accumulators
        if optimizer == "adam":
            self.mV = np.zeros_like(self.V)
            self.vV = np.zeros_like(self.V)
            self.mW = np.zeros_like(self.W)
            self.vW = np.zeros_like(self.W)
            self.t = 0
        elif optimizer == "adagrad":
            self.gV_acc = np.zeros_like(self.V)
            self.gW_acc = np.zeros_like(self.W)

    def logits(self, X):
        E = self.V[X]  # (B, F, k)
        S = E.sum(1)   # (B, k)
        inter = 0.5 * ((S ** 2).sum(1) - (E ** 2).sum((1, 2)))
        return self.b + self.W[X].sum(1) + inter, E, S

    def step(self, X, y):
        B = len(y)
        z, E, S = self.logits(X)
        p = sigmoid(z)
        g = ((p - y) / B).astype(np.float32)

        gV = np.zeros_like(self.V)
        gW = np.zeros_like(self.W)
        np.add.at(gW, X, g[:, None])
        np.add.at(gV, X, g[:, None, None] * (S[:, None, :] - E))

        if self.l2 > 0:
            gV += self.l2 * self.V
            gW += self.l2 * self.W

        if self.optimizer == "adam":
            self.t += 1
            b1, b2, eps = 0.9, 0.999, 1e-8
            for P, G, M, Vv in ((self.V, gV, self.mV, self.vV), (self.W, gW, self.mW, self.vW)):
                M *= b1
                M += (1 - b1) * G
                Vv *= b2
                Vv += (1 - b2) * (G * G)
                P -= self.lr * (M / (1 - b1 ** self.t)) / (np.sqrt(Vv / (1 - b2 ** self.t)) + eps)
        elif self.optimizer == "adagrad":
            eps = 1e-8
            self.gV_acc += gV * gV
            self.gW_acc += gW * gW
            self.V -= self.lr * gV / (np.sqrt(self.gV_acc) + eps)
            self.W -= self.lr * gW / (np.sqrt(self.gW_acc) + eps)
        elif self.optimizer == "sgd":
            self.V -= self.lr * gV
            self.W -= self.lr * gW

        self.b -= self.lr * g.sum()
        loss = float(-np.mean(y * np.log(p + 1e-9) + (1 - y) * np.log(1 - p + 1e-9)))
        return loss

    def predict(self, X, bs=200_000):
        preds = []
        for i in range(0, len(X), bs):
            z, _, _ = self.logits(X[i:i + bs])
            preds.append(z)
        return np.concatenate(preds)


def run_experiment(
    fields: list[str],
    include_crosses: bool = False,
    k: int = 16,
    lr: float = 0.001,
    l2: float = 1e-5,
    optimizer: str = "adam",
    batch_size: int = 8192,
    epochs: int = 25,
    patience: int = 4,
    seed: int = 0,
    full_eval: bool = False,
):
    t0 = time.time()
    encoded, dim, actual_fields = load_data(fields, include_crosses)
    xtr, ytr, _ = encoded["train"]
    xva, yva, uva = encoded["valid"]

    # Medium partition
    mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    xmed, ymed = xva[mask], yva[mask]
    umed = [u for u, keep in zip(uva, mask) if keep]

    model = FastFM(dim, k=k, lr=lr, l2=l2, optimizer=optimizer, seed=seed)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_state = None
    best_epoch = 0
    history = []
    bad = 0

    print(f"--- Running: opt={optimizer}, lr={lr}, l2={l2}, k={k}, bs={batch_size}, fields={len(actual_fields)} (dim={dim}), seed={seed} ---")

    for ep in range(1, epochs + 1):
        order = rng.permutation(len(ytr))
        losses = []
        ep_t0 = time.time()
        for start in range(0, len(order), batch_size):
            idx = order[start:start + batch_size]
            losses.append(model.step(xtr[idx], ytr[idx]))

        preds_med = model.predict(xmed)
        med_m = clean_metrics(evaluate(umed, ymed, preds_med))
        ep_dur = time.time() - ep_t0

        history.append({
            "epoch": ep, "loss": float(np.mean(losses)),
            "duration": ep_dur,
            **med_m,
        })
        print(f"Ep {ep:2d} | loss {np.mean(losses):.4f} | Med GAUC {med_m['GAUC']:.5f} nDCG@5 {med_m['nDCG@5']:.5f} primary {med_m['primary']:.5f} | {ep_dur:.1f}s", flush=True)

        if med_m["primary"] > best_primary + 1e-5:
            best_primary = med_m["primary"]
            best_epoch = ep
            best_state = (model.V.copy(), model.W.copy(), np.float32(model.b))
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                print(f"Early stopped at epoch {ep}")
                break

    model.V, model.W, model.b = best_state
    full_m = None
    if full_eval:
        preds_full = model.predict(xva)
        full_m = clean_metrics(evaluate(uva, yva, preds_full))
        print("=== Full Validation Score ===")
        print(f"GAUC: {full_m['GAUC']:.7f}, nDCG@5: {full_m['nDCG@5']:.7f}, primary: {full_m['primary']:.7f}")

    return model, encoded, {
        "fields": actual_fields,
        "num_fields": len(actual_fields),
        "dim": dim,
        "k": k,
        "lr": lr,
        "l2": l2,
        "optimizer": optimizer,
        "seed": seed,
        "best_epoch": best_epoch,
        "best_medium": history[best_epoch - 1],
        "history": history,
        "full": full_m,
        "elapsed_seconds": time.time() - t0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", choices=("rich15", "rich_all", "rich_cross"), default="rich_all")
    parser.add_argument("--k", type=int, default=16)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--l2", type=float, default=1e-5)
    parser.add_argument("--optimizer", default="adam")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    fields_15 = [
        "user_id", "video_id", "author_id", "tab", "dur_bucket", "hour", "weekday",
        "video_type", "music_type", "tag", "active", "follow_range", "fans_range",
        "friend_range", "register_range",
    ]
    fields_all = [
        "user_id", "video_id", "author_id", "tab", "dur_bucket", "hour", "weekday",
        "video_type", "upload_type", "music_type", "tag", "aspect",
        "active", "is_lowactive", "is_live_streamer", "is_video_author",
        "follow_range", "fans_range", "friend_range", "register_range",
        *[f"onehot_{i}" for i in range(18)],
    ]
    fields_cross = fields_all + ["item_tab", "author_tab", "tag_tab", "hour_weekday", "active_dur"]

    if args.preset == "rich15":
        target_fields = fields_15
        include_crosses = False
    elif args.preset == "rich_all":
        target_fields = fields_all
        include_crosses = False
    elif args.preset == "rich_cross":
        target_fields = fields_cross
        include_crosses = True

    model, encoded, res = run_experiment(
        target_fields,
        include_crosses=include_crosses,
        k=args.k,
        lr=args.lr,
        l2=args.l2,
        optimizer=args.optimizer,
        seed=args.seed,
        full_eval=args.full,
    )

    rendered = json.dumps(res, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
