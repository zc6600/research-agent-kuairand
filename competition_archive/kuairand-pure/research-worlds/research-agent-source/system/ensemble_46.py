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


def read_base_features():
    videos = {}
    with (DATA / "video_features_basic_pure.csv").open(newline="") as fh:
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


def build_historical_user_profiles(videos, recent_days=0, top_author=False, second_preferences=False, last_tag=False, last_tab=False):
    u_tags = defaultdict(lambda: defaultdict(int))
    u_tabs = defaultdict(lambda: defaultdict(int))
    u_authors = defaultdict(lambda: defaultdict(int))
    u_longview = defaultdict(int)
    u_total = defaultdict(int)
    recent_tags = defaultdict(lambda: defaultdict(int))
    recent_tabs = defaultdict(lambda: defaultdict(int))
    recent_longview = defaultdict(int)
    recent_total = defaultdict(int)
    last_tags = {}
    last_tabs = {}

    with (DATA / "log_standard_4_08_to_4_21_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            u = r["user_id"]
            v = r["video_id"]
            t = r["tab"]
            vmeta = videos.get(v, {"author_id": "UNK", "tag": "UNK"})
            u_tags[u][vmeta["tag"]] += 1
            if last_tag:
                last_tags[u] = vmeta["tag"]
            if last_tab:
                last_tabs[u] = t
            u_tabs[u][t] += 1
            if top_author:
                u_authors[u][vmeta.get("author_id", "UNK")] += 1
            u_total[u] += 1
            if r["long_view"] == "1":
                u_longview[u] += 1
            if recent_days and int(r["date"]) >= 20220421 - recent_days + 1:
                recent_tags[u][vmeta["tag"]] += 1
                recent_tabs[u][t] += 1
                recent_total[u] += 1
                if r["long_view"] == "1":
                    recent_longview[u] += 1

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
        if second_preferences:
            tag_order = sorted(u_tags[u].items(), key=lambda x: (-x[1], x[0]))
            tab_order = sorted(u_tabs[u].items(), key=lambda x: (-x[1], x[0]))
            profiles[u]["u_second_tag"] = tag_order[1][0] if len(tag_order) > 1 else "UNK"
            profiles[u]["u_second_tab"] = tab_order[1][0] if len(tab_order) > 1 else "UNK"
        if last_tag:
            profiles[u]["u_last_tag"] = last_tags.get(u, "UNK")
        if last_tab:
            profiles[u]["u_last_tab"] = last_tabs.get(u, "UNK")
        if top_author:
            profiles[u]["u_top_author"] = max(u_authors[u].items(), key=lambda x: x[1])[0] if u_authors[u] else "UNK"
        if recent_days:
            rtot = recent_total[u]
            rtag = max(recent_tags[u].items(), key=lambda x: x[1])[0] if recent_tags[u] else "UNK"
            rtab = max(recent_tabs[u].items(), key=lambda x: x[1])[0] if recent_tabs[u] else "UNK"
            rrate = recent_longview[u] / rtot if rtot > 0 else 0.0
            profiles[u].update({
                "u_recent_top_tag": rtag,
                "u_recent_top_tab": rtab,
                "u_recent_rate_bucket": str(int(min(rrate * 10, 9))),
            })
    return profiles


def build_item_profiles():
    counts = defaultdict(int)
    positives = defaultdict(int)
    with (DATA / "log_standard_4_08_to_4_21_pure.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            v = r["video_id"]
            counts[v] += 1
            if r["long_view"] == "1":
                positives[v] += 1
    profiles = {}
    for v, total in counts.items():
        rate = positives[v] / total if total else 0.0
        count_bucket = "0" if total <= 5 else ("1" if total <= 20 else ("2" if total <= 50 else ("3" if total <= 100 else "4")))
        profiles[v] = {
            "item_count_bucket": count_bucket,
            "item_rate_bucket": str(int(min(rate * 10, 9))),
        }
    return profiles


def load_data_46(recent_days=0, top_author=False, second_preferences=False, item_stats=False, last_tag=False, last_tab=False):
    videos, users = read_base_features()
    profiles = build_historical_user_profiles(videos, recent_days=recent_days, top_author=top_author, second_preferences=second_preferences, last_tag=last_tag, last_tab=last_tab)
    item_profiles = build_item_profiles() if item_stats else {}

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
                vfeat = videos.get(v, {"author_id": "UNK", "video_type": "UNK", "upload_type": "UNK", "music_type": "UNK", "music_id": "UNK", "tag": "UNK", "tag2": "UNK", "aspect": "UNK", "upload_dt": "2022-04-10"})
                ufeat = users.get(u, {"active": "UNK", "is_lowactive": "UNK", "is_live_streamer": "UNK", "is_video_author": "UNK", "follow_range": "UNK", "fans_range": "UNK", "friend_range": "UNK", "register_range": "UNK", **{f"onehot_{i}": "UNK" for i in range(18)}})
                dur = float(r["duration_ms"] or 0)
                dur_bucket = str(int(np.searchsorted(dur_cuts, dur)))
                date = int(r["date"])
                weekday = str((date - 20220404) % 7)
                hour = str(int(r["hourmin"] or 0) // 100)
                tab = r["tab"] or "UNK"

                u_prof = profiles.get(u, {"u_top_tag": "UNK", "u_top_tab": "UNK", "u_rate_bucket": "UNK", "u_count_bucket": "UNK", "u_top_author": "UNK", "u_second_tag": "UNK", "u_second_tab": "UNK", "u_last_tag": "UNK"})
                i_prof = item_profiles.get(v, {"item_count_bucket": "UNK", "item_rate_bucket": "UNK"})

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
                    "label": 1 if r["long_view"] == "1" else 0,
                }
                if second_preferences:
                    feat_dict["u_second_tag"] = u_prof.get("u_second_tag", "UNK")
                    feat_dict["u_second_tab"] = u_prof.get("u_second_tab", "UNK")
                    feat_dict["match_second_tag"] = "1" if (vfeat["tag"] != "UNK" and vfeat["tag"] == u_prof.get("u_second_tag", "UNK")) else "0"
                    feat_dict["match_second_tab"] = "1" if (tab != "UNK" and tab == u_prof.get("u_second_tab", "UNK")) else "0"
                if last_tag:
                    feat_dict["u_last_tag"] = u_prof.get("u_last_tag", "UNK")
                    feat_dict["match_last_tag"] = "1" if (vfeat["tag"] != "UNK" and vfeat["tag"] == u_prof.get("u_last_tag", "UNK")) else "0"
                if last_tab:
                    feat_dict["u_last_tab"] = u_prof.get("u_last_tab", "UNK")
                    feat_dict["match_last_tab"] = "1" if (tab != "UNK" and tab == u_prof.get("u_last_tab", "UNK")) else "0"
                if item_stats:
                    feat_dict["item_count_bucket"] = i_prof["item_count_bucket"]
                    feat_dict["item_rate_bucket"] = i_prof["item_rate_bucket"]
                if top_author:
                    feat_dict["u_top_author"] = u_prof.get("u_top_author", "UNK")
                    feat_dict["match_author"] = "1" if (vfeat["author_id"] != "UNK" and vfeat["author_id"] == u_prof.get("u_top_author", "UNK")) else "0"
                if recent_days:
                    feat_dict.update({
                        "u_recent_top_tag": u_prof.get("u_recent_top_tag", "UNK"),
                        "u_recent_top_tab": u_prof.get("u_recent_top_tab", "UNK"),
                        "u_recent_rate_bucket": u_prof.get("u_recent_rate_bucket", "UNK"),
                        "recent_match_tag": "1" if (vfeat["tag"] != "UNK" and vfeat["tag"] == u_prof.get("u_recent_top_tag", "UNK")) else "0",
                        "recent_match_tab": "1" if (tab != "UNK" and tab == u_prof.get("u_recent_top_tab", "UNK")) else "0",
                    })
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

    return encoded, dim, field_names


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

    return model, {
        "seed": seed,
        "best_epoch": best_epoch,
        "best_medium": history[best_epoch - 1],
        "med_preds": med_preds,
        "full_preds": full_preds,
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
    parser.add_argument("--recent-days", type=int, default=0, help="Add profiles computed from the last N training days")
    parser.add_argument("--top-author", action="store_true", help="Add leak-free historical top-author affinity fields")
    parser.add_argument("--second-preferences", action="store_true", help="Add leak-free second-ranked historical tag/tab preferences and matches")
    parser.add_argument("--item-stats", action="store_true", help="Add training-window video exposure and long-view-rate buckets")
    parser.add_argument("--last-tag", action="store_true", help="Add last historical tag and candidate match fields")
    parser.add_argument("--last-tab", action="store_true", help="Add last historical tab and candidate match fields")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    started = time.time()
    encoded, dim, actual_fields = load_data_46(recent_days=args.recent_days, top_author=args.top_author, second_preferences=args.second_preferences, item_stats=args.item_stats, last_tag=args.last_tag, last_tab=args.last_tab)
    print(f"Loaded {len(actual_fields)} fields: dimension={dim}")

    xva, yva, uva = encoded["valid"]
    mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    umed = [u for u, keep in zip(uva, mask) if keep]
    ymed = yva[mask]

    seed_details = []
    med_preds_list = []
    full_preds_list = []

    for s in args.seeds:
        model, detail = train_single_seed(
            encoded, dim, actual_fields, seed=s,
            k=args.k, lr=args.lr, l2=args.l2,
            epochs=args.epochs, patience=args.patience,
        )
        med_preds_list.append(detail.pop("med_preds"))
        full_preds_list.append(detail.pop("full_preds"))
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
        "seed_details": seed_details,
        "elapsed_seconds": time.time() - started,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
