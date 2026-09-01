#!/usr/bin/env python3
"""46-Field Rich Factorization Machine and Field-weighted FM Ensemble for KuaiRand-Pure.

Features: 46 fields (38 demographic/video baseline + 8 historical user preference/match & video metadata fields)
Total Dimension: 42,705
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


def read_base_features(data_dir=DATA):
    videos = {}
    with (data_dir / "video_features_basic_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            tag_raw = (r["tag"] or "UNK").split(",")
            primary_tag = tag_raw[0] if len(tag_raw) > 0 and tag_raw[0] else "UNK"
            second_tag = tag_raw[1] if len(tag_raw) > 1 and tag_raw[1] else "UNK"
            w = float(r["server_width"] or 0)
            h = float(r["server_height"] or 0)
            aspect = "vert" if (h > 0 and w / h < 0.8) else "horiz"
            upload_dt = r["upload_dt"] or "2022-04-10"
            videos[r["video_id"]] = {
                "author_id": r["author_id"] or "UNK",
                "video_type": r["video_type"] or "UNK",
                "upload_type": r["upload_type"] or "UNK",
                "music_type": r["music_type"] or "UNK",
                "music_id": r["music_id"] or "UNK",
                "tag": primary_tag,
                "tag2": second_tag,
                "aspect": aspect,
                "upload_dt": upload_dt,
            }
    users = {}
    with (data_dir / "user_features_pure.csv").open(newline="") as fh:
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


def build_historical_user_profiles(videos, data_dir=DATA):
    u_tags = defaultdict(lambda: defaultdict(int))
    u_tabs = defaultdict(lambda: defaultdict(int))
    u_longview = defaultdict(int)
    u_total = defaultdict(int)

    with (data_dir / "log_standard_4_08_to_4_21_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            u = r["user_id"]
            v = r["video_id"]
            t = r["tab"]
            vmeta = videos.get(v, {"author_id": "UNK", "tag": "UNK"})
            u_tags[u][vmeta["tag"]] += 1
            u_tabs[u][t] += 1
            u_total[u] += 1
            if r["long_view"] == "1":
                u_longview[u] += 1

    profiles = {}
    for u, tot in u_total.items():
        top_tag = max(u_tags[u].items(), key=lambda x: x[1])[0] if u_tags[u] else "UNK"
        top_tab = max(u_tabs[u].items(), key=lambda x: x[1])[0] if u_tabs[u] else "UNK"
        pos_rate = u_longview[u] / tot if tot > 0 else 0.0
        rate_bucket = str(int(min(pos_rate * 10, 9)))
        count_bucket = "0" if tot <= 5 else ("1" if tot <= 20 else ("2" if tot <= 50 else ("3" if tot <= 100 else "4")))
        profiles[u] = {
            "u_top_tag": top_tag,
            "u_top_tab": top_tab,
            "u_rate_bucket": rate_bucket,
            "u_count_bucket": count_bucket,
        }
    return profiles


def load_data_46(data_dir=DATA, include_test=False):
    videos, users = read_base_features(data_dir)
    profiles = build_historical_user_profiles(videos, data_dir)

    dur_cuts = np.array([15000, 30000, 45000, 60000, 90000, 120000, 180000, 300000])
    full_evaluation = data_dir / "log_standard_4_22_to_5_08_pure.csv"
    if full_evaluation.exists():
        files = {
            "train": ("log_standard_4_08_to_4_21_pure.csv", 20220408, 20220421),
            "valid": ("log_standard_4_22_to_5_08_pure.csv", 20220422, 20220428),
        }
        if include_test:
            files["test"] = ("log_standard_4_22_to_5_08_pure.csv", 20220429, 20220508)
    else:
        files = {
            "train": ("log_standard_4_08_to_4_21_pure.csv", 20220408, 20220421),
            "valid": ("log_public_4_22_to_4_28_pure.csv", 20220422, 20220428),
        }
        if include_test:
            raise FileNotFoundError(
                "submission generation requires log_standard_4_22_to_5_08_pure.csv"
            )
    raw = {}
    for split, (fname, first_date, last_date) in files.items():
        rows = []
        with (data_dir / fname).open(newline="") as fh:
            for r in csv.DictReader(fh):
                date = int(r["date"])
                if not first_date <= date <= last_date:
                    continue
                u = r["user_id"]
                v = r["video_id"]
                vfeat = videos.get(v, {"author_id": "UNK", "video_type": "UNK", "upload_type": "UNK", "music_type": "UNK", "music_id": "UNK", "tag": "UNK", "tag2": "UNK", "aspect": "UNK", "upload_dt": "2022-04-10"})
                ufeat = users.get(u, {"active": "UNK", "is_lowactive": "UNK", "is_live_streamer": "UNK", "is_video_author": "UNK", "follow_range": "UNK", "fans_range": "UNK", "friend_range": "UNK", "register_range": "UNK", **{f"onehot_{i}": "UNK" for i in range(18)}})
                dur = float(r["duration_ms"] or 0)
                dur_bucket = str(int(np.searchsorted(dur_cuts, dur)))
                weekday = str((date - 20220404) % 7)
                hour = str(int(r["hourmin"] or 0) // 100)
                tab = r["tab"] or "UNK"

                u_prof = profiles.get(u, {"u_top_tag": "UNK", "u_top_tab": "UNK", "u_rate_bucket": "UNK", "u_count_bucket": "UNK"})

                try:
                    up_parts = vfeat["upload_dt"].split("-")
                    up_int = int(up_parts[0]) * 10000 + int(up_parts[1]) * 100 + int(up_parts[2])
                    age_days = max(0, date - up_int)
                    video_age = str(min(age_days, 15))
                except Exception:
                    video_age = "UNK"

                feat_dict = {
                    "user_id": u, "video_id": v, "author_id": vfeat["author_id"],
                    "tab": tab, "dur_bucket": dur_bucket, "hour": hour, "weekday": weekday,
                    "video_type": vfeat["video_type"], "upload_type": vfeat["upload_type"],
                    "music_type": vfeat["music_type"], "tag": vfeat["tag"], "aspect": vfeat["aspect"],
                    **ufeat,
                    "tag2": vfeat["tag2"],
                    "video_age": video_age,
                    "u_top_tag": u_prof["u_top_tag"],
                    "u_top_tab": u_prof["u_top_tab"],
                    "u_rate_bucket": u_prof["u_rate_bucket"],
                    "u_count_bucket": u_prof["u_count_bucket"],
                    "match_tag": "1" if (vfeat["tag"] != "UNK" and vfeat["tag"] == u_prof["u_top_tag"]) else "0",
                    "match_tab": "1" if (tab != "UNK" and tab == u_prof["u_top_tab"]) else "0",
                    # The frozen model never reads test labels during final prediction.
                    "label": 0 if split == "test" else (1 if r["long_view"] == "1" else 0),
                }
                rows.append(feat_dict)
        raw[split] = rows

    ignore_cols = {"label"}
    field_names = [k for k in raw["train"][0].keys() if k not in ignore_cols]

    # Encode
    vocabs = [{} for _ in field_names]
    for r in raw["train"]:
        for i, f in enumerate(field_names):
            val = r[f]
            if val not in vocabs[i]:
                vocabs[i][val] = len(vocabs[i])

    dimensions = [len(v) + 1 for v in vocabs]
    offsets = np.cumsum([0] + dimensions[:-1]).astype(np.int32)
    dim = sum(dimensions)

    encoded = {}
    for split, srows in raw.items():
        n = len(srows)
        x = np.empty((n, len(field_names)), dtype=np.int32)
        y = np.empty(n, dtype=np.float32)
        u_list = []
        for row_idx, r in enumerate(srows):
            for i, f in enumerate(field_names):
                unk = len(vocabs[i])
                x[row_idx, i] = vocabs[i].get(r[f], unk) + offsets[i]
            y[row_idx] = r["label"]
            u_list.append(r["user_id"])
        encoded[split] = (x, y, u_list)

    submission_ids = {
        split: [(row["user_id"], row["video_id"]) for row in rows]
        for split, rows in raw.items()
    }
    return encoded, dim, field_names, submission_ids


class FastFM:
    def __init__(self, dim, k=16, lr=0.001, l2=1e-5, seed=0):
        rng = np.random.default_rng(seed)
        self.dim = dim
        self.k = k
        self.lr = lr
        self.l2 = l2
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W = np.zeros(dim, dtype=np.float32)
        self.b = np.float32(0.0)

        # Adam
        self.mV = np.zeros_like(self.V)
        self.vV = np.zeros_like(self.V)
        self.mW = np.zeros_like(self.W)
        self.vW = np.zeros_like(self.W)
        self.t = 0

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

        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        for P, G, M, Vv in ((self.V, gV, self.mV, self.vV), (self.W, gW, self.mW, self.vW)):
            M *= b1
            M += (1 - b1) * G
            Vv *= b2
            Vv += (1 - b2) * (G * G)
            P -= self.lr * (M / (1 - b1 ** self.t)) / (np.sqrt(Vv / (1 - b2 ** self.t)) + eps)

        self.b -= self.lr * g.sum()
        loss = float(-np.mean(y * np.log(p + 1e-9) + (1 - y) * np.log(1 - p + 1e-9)))
        return loss

    def predict(self, X, bs=200_000):
        preds = []
        for i in range(0, len(X), bs):
            z, _, _ = self.logits(X[i:i + bs])
            preds.append(z)
        return np.concatenate(preds)


def train_single_seed(encoded, dim, actual_fields, seed, k=16, lr=0.001, l2=1e-5, epochs=25, patience=4):
    xtr, ytr, _ = encoded["train"]
    xva, yva, uva = encoded["valid"]

    mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    xmed, ymed = xva[mask], yva[mask]
    umed = [u for u, keep in zip(uva, mask) if keep]

    model = FastFM(dim, k=k, lr=lr, l2=l2, seed=seed)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_state = None
    best_epoch = 0
    history = []
    bad = 0

    print(f"--- Training 46-field seed {seed} (k={k}, lr={lr}, l2={l2}) ---")
    for ep in range(1, epochs + 1):
        order = rng.permutation(len(ytr))
        losses = []
        t0 = time.time()
        for start in range(0, len(order), 8192):
            idx = order[start:start + 8192]
            losses.append(model.step(xtr[idx], ytr[idx]))

        preds_med = model.predict(xmed)
        med_m = clean_metrics(evaluate(umed, ymed, preds_med))
        dur = time.time() - t0
        history.append({
            "epoch": ep, "loss": float(np.mean(losses)), "duration": dur, **med_m,
        })
        print(f"  Seed {seed} Ep {ep:2d} | loss {np.mean(losses):.4f} | Med GAUC {med_m['GAUC']:.5f} nDCG@5 {med_m['nDCG@5']:.5f} primary {med_m['primary']:.5f} | {dur:.1f}s", flush=True)

        if med_m["primary"] > best_primary + 1e-5:
            best_primary = med_m["primary"]
            best_epoch = ep
            best_state = (model.V.copy(), model.W.copy(), np.float32(model.b))
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                print(f"  Seed {seed} early stopped at epoch {ep}")
                break

    model.V, model.W, model.b = best_state
    med_preds = model.predict(xmed)
    full_preds = model.predict(xva)
    test_preds = model.predict(encoded["test"][0]) if "test" in encoded else None

    return model, {
        "seed": seed,
        "best_epoch": best_epoch,
        "best_medium": history[best_epoch - 1],
        "med_preds": med_preds,
        "full_preds": full_preds,
        "test_preds": test_preds,
        "history": history,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4, 5, 6, 7])
    parser.add_argument("--k", type=int, default=16)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--l2", type=float, default=1e-5)
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--submission", type=Path, help="Write final test scores in Starter Kit CSV schema")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    started = time.time()
    encoded, dim, actual_fields, submission_ids = load_data_46(
        data_dir=args.data_dir,
        include_test=args.submission is not None,
    )
    print(f"Loaded 46 fields: {len(actual_fields)}, dimension={dim}")

    xva, yva, uva = encoded["valid"]
    mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    umed = [u for u, keep in zip(uva, mask) if keep]
    ymed = yva[mask]

    seed_details = []
    med_preds_list = []
    full_preds_list = []
    test_preds_list = []

    for s in args.seeds:
        model, detail = train_single_seed(
            encoded, dim, actual_fields, seed=s,
            k=args.k, lr=args.lr, l2=args.l2,
            epochs=args.epochs, patience=args.patience,
        )
        med_preds_list.append(detail.pop("med_preds"))
        full_preds_list.append(detail.pop("full_preds"))
        test_preds = detail.pop("test_preds")
        if test_preds is not None:
            test_preds_list.append(test_preds)
        seed_details.append(detail)

    # Individual scores
    individual_med_scores = []
    for i, s in enumerate(args.seeds):
        m_score = clean_metrics(evaluate(umed, ymed, med_preds_list[i]))
        individual_med_scores.append({"seed": s, **m_score})
        print(f"Seed {s} Medium Score: GAUC {m_score['GAUC']:.5f} nDCG@5 {m_score['nDCG@5']:.5f} primary {m_score['primary']:.5f}")

    # Ensemble Medium Score
    ens_med_preds = np.mean(med_preds_list, axis=0)
    ens_med_score = clean_metrics(evaluate(umed, ymed, ens_med_preds))
    print(f"\n=== Ensemble ({len(args.seeds)} seeds) Medium Score ===")
    print(f"GAUC: {ens_med_score['GAUC']:.7f}, nDCG@5: {ens_med_score['nDCG@5']:.7f}, primary: {ens_med_score['primary']:.7f}")

    ens_full_score = None
    individual_full_scores = []
    if args.full:
        for i, s in enumerate(args.seeds):
            f_score = clean_metrics(evaluate(uva, yva, full_preds_list[i]))
            individual_full_scores.append({"seed": s, **f_score})
            print(f"Seed {s} Full Score: GAUC {f_score['GAUC']:.7f} nDCG@5 {f_score['nDCG@5']:.7f} primary {f_score['primary']:.7f}")

        ens_full_preds = np.mean(full_preds_list, axis=0)
        ens_full_score = clean_metrics(evaluate(uva, yva, ens_full_preds))
        print(f"\n=== Ensemble ({len(args.seeds)} seeds) Full Validation Score ===")
        print(f"GAUC: {ens_full_score['GAUC']:.7f}, nDCG@5: {ens_full_score['nDCG@5']:.7f}, primary: {ens_full_score['primary']:.7f}")
        # Official baseline deltas
        base_gauc, base_ndcg, base_primary = 0.6674, 0.5357, 0.6016
        print(f"Delta vs baseline: GAUC {ens_full_score['GAUC'] - base_gauc:+.7f}, nDCG@5 {ens_full_score['nDCG@5'] - base_ndcg:+.7f}, primary {ens_full_score['primary'] - base_primary:+.7f}")
        # Delta versus the earlier eight-seed 38-field ensemble.
        prior_gauc, prior_ndcg, prior_primary = 0.6712176, 0.5376403, 0.6044289
        print(f"Delta vs prior ensemble: GAUC {ens_full_score['GAUC'] - prior_gauc:+.7f}, nDCG@5 {ens_full_score['nDCG@5'] - prior_ndcg:+.7f}, primary {ens_full_score['primary'] - prior_primary:+.7f}")

    if args.submission:
        test_scores = np.mean(test_preds_list, axis=0)
        test_ids = submission_ids["test"]
        if len(test_scores) != len(test_ids):
            raise RuntimeError("test prediction count does not match test row count")
        args.submission.parent.mkdir(parents=True, exist_ok=True)
        with args.submission.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["row_id", "user_id", "video_id", "score"])
            for row_id, ((user_id, video_id), score) in enumerate(zip(test_ids, test_scores)):
                writer.writerow([row_id, user_id, video_id, f"{float(score):.10g}"])
        print(f"Wrote test submission: {args.submission} ({len(test_ids):,d} rows)")

    payload = {
        "experiment": "rich46_fm_ensemble",
        "seeds": args.seeds,
        "k": args.k,
        "lr": args.lr,
        "l2": args.l2,
        "num_fields": len(actual_fields),
        "dim": dim,
        "fields": actual_fields,
        "individual_medium_scores": individual_med_scores,
        "ensemble_medium_score": ens_med_score,
        "individual_full_scores": individual_full_scores if args.full else None,
        "ensemble_full_score": ens_full_score,
        "submission_rows": len(submission_ids.get("test", [])) if args.submission else 0,
        "seed_details": seed_details,
        "elapsed_seconds": time.time() - started,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
