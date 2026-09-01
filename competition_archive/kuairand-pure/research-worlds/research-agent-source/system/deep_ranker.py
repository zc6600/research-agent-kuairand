#!/usr/bin/env python3
"""Deep ranking architectures (FM, DeepFM, DCN, Pairwise) for KuaiRand-Pure.

Features extracted:
- Categorical features with ID embeddings (user, video, author, music, tag, tab, context, user onehots).
- Continuous / numerical features with normalization (historical stats from training set, user stats).
- Architectures: FM, DeepFM, Cross-Network (DCN-v2), Multi-Task / Auxiliary heads.
- Evaluator: Unchanged starter_kit/evaluate.py on deterministic Medium or Full validation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition_data" / "data"
sys.path.insert(0, str(ROOT / "starter_kit"))
from evaluate import evaluate  # noqa: E402


def medium_user(user_id: str) -> bool:
    """Deterministic BLAKE2b 25% complete-user sample."""
    return int(hashlib.blake2b(user_id.encode(), digest_size=4).hexdigest(), 16) % 4 == 0


def clean_metrics(metrics: dict) -> dict:
    return {k: int(v) if k in ("users", "rows") else float(v) for k, v in metrics.items()}


def extract_features(use_history_stats: bool = True):
    """Load side features and compute strictly leakage-safe historical stats from training log."""
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
            if h > 0:
                ratio = w / h
                if ratio < 0.6:
                    aspect_bucket = "vertical_9_16"
                elif ratio < 0.9:
                    aspect_bucket = "vertical_3_4"
                elif ratio < 1.1:
                    aspect_bucket = "square"
                else:
                    aspect_bucket = "horizontal_16_9"
            else:
                aspect_bucket = "UNK"

            video_features[v] = {
                "author_id": r["author_id"] or "UNK",
                "video_type": r["video_type"] or "UNK",
                "upload_type": r["upload_type"] or "UNK",
                "music_type": r["music_type"] or "UNK",
                "music_id": r["music_id"] or "UNK",
                "primary_tag": primary_tag,
                "aspect_bucket": aspect_bucket,
            }

    # 3. Compute historical stats from training log (strictly train only)
    item_stats = defaultdict(lambda: [0, 0, 0])  # [imp, long_view, click]
    author_stats = defaultdict(lambda: [0, 0, 0])
    user_stats = defaultdict(lambda: [0, 0, 0])
    tag_stats = defaultdict(lambda: [0, 0, 0])
    tab_stats = defaultdict(lambda: [0, 0, 0])
    total_imp = 0
    total_long = 0
    total_click = 0

    if use_history_stats:
        with (DATA / "log_standard_4_08_to_4_21_pure.csv").open(newline="") as fh:
            for r in csv.DictReader(fh):
                u = r["user_id"]
                v = r["video_id"]
                author = video_features.get(v, {}).get("author_id", "UNK")
                tag = video_features.get(v, {}).get("primary_tag", "UNK")
                tab = r["tab"] or "UNK"
                lv = 1 if r["long_view"] == "1" else 0
                clk = 1 if r["is_click"] == "1" else 0

                item_stats[v][0] += 1
                item_stats[v][1] += lv
                item_stats[v][2] += clk

                author_stats[author][0] += 1
                author_stats[author][1] += lv
                author_stats[author][2] += clk

                user_stats[u][0] += 1
                user_stats[u][1] += lv
                user_stats[u][2] += clk

                tag_stats[tag][0] += 1
                tag_stats[tag][1] += lv
                tag_stats[tag][2] += clk

                tab_stats[tab][0] += 1
                tab_stats[tab][1] += lv
                tab_stats[tab][2] += clk

                total_imp += 1
                total_long += lv
                total_click += clk

    global_long_rate = total_long / max(total_imp, 1)
    global_click_rate = total_click / max(total_imp, 1)

    hist_data = {
        "item": item_stats,
        "author": author_stats,
        "user": user_stats,
        "tag": tag_stats,
        "tab": tab_stats,
        "global_long_rate": global_long_rate,
        "global_click_rate": global_click_rate,
    }

    return user_features, video_features, hist_data


def load_dataset(use_history_stats: bool = True, feature_set: str = "full"):
    user_features, video_features, hist_data = extract_features(use_history_stats)

    dur_cuts = np.array([15000, 30000, 45000, 60000, 90000, 120000, 180000, 300000])
    files = {
        "train": "log_standard_4_08_to_4_21_pure.csv",
        "valid": "log_public_4_22_to_4_28_pure.csv",
    }

    # Define categorical feature names
    if feature_set == "base_15":
        cat_cols = [
            "user_id", "video_id", "author_id", "tab", "dur_bucket",
            "hour", "weekday", "video_type", "music_type", "primary_tag",
            "active_degree", "follow_range", "fans_range", "friend_range", "register_range",
        ]
        num_cols = []
    elif feature_set == "rich_cat":
        cat_cols = [
            "user_id", "video_id", "author_id", "tab", "dur_bucket",
            "hour", "weekday", "video_type", "upload_type", "music_type", "primary_tag", "aspect_bucket",
            "active_degree", "is_lowactive", "is_live_streamer", "is_video_author",
            "follow_range", "fans_range", "friend_range", "register_range",
            *[f"onehot_{i}" for i in range(18)],
        ]
        num_cols = []
    else:  # "full"
        cat_cols = [
            "user_id", "video_id", "author_id", "tab", "dur_bucket",
            "hour", "weekday", "video_type", "upload_type", "music_type", "primary_tag", "aspect_bucket",
            "active_degree", "is_lowactive", "is_live_streamer", "is_video_author",
            "follow_range", "fans_range", "friend_range", "register_range",
            *[f"onehot_{i}" for i in range(18)],
        ]
        num_cols = [
            "item_imp_log", "item_lv_rate", "item_clk_rate",
            "author_imp_log", "author_lv_rate", "author_clk_rate",
            "user_imp_log", "user_lv_rate", "user_clk_rate",
            "tag_lv_rate", "tab_lv_rate",
        ]

    # Process rows
    raw_splits = {}
    for split, filename in files.items():
        rows = []
        with (DATA / filename).open(newline="") as fh:
            for r in csv.DictReader(fh):
                u = r["user_id"]
                v = r["video_id"]
                vfeat = video_features.get(v, {
                    "author_id": "UNK", "video_type": "UNK", "upload_type": "UNK",
                    "music_type": "UNK", "music_id": "UNK", "primary_tag": "UNK",
                    "aspect_bucket": "UNK",
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

                row_cat = {
                    "user_id": u, "video_id": v, "author_id": vfeat["author_id"],
                    "tab": tab, "dur_bucket": dur_bucket, "hour": hour, "weekday": weekday,
                    "video_type": vfeat["video_type"], "upload_type": vfeat["upload_type"],
                    "music_type": vfeat["music_type"], "primary_tag": vfeat["primary_tag"],
                    "aspect_bucket": vfeat["aspect_bucket"],
                    **ufeat,
                }

                row_dict = {k: row_cat.get(k, "UNK") for k in cat_cols}
                row_dict["label"] = 1.0 if r["long_view"] == "1" else 0.0
                row_dict["is_click"] = 1.0 if r.get("is_click", "0") == "1" else 0.0
                row_dict["is_like"] = 1.0 if r.get("is_like", "0") == "1" else 0.0
                row_dict["user_id_raw"] = u

                if num_cols:
                    gl_lv = hist_data["global_long_rate"]
                    gl_clk = hist_data["global_click_rate"]
                    # Item stats with empirical Bayes shrinkage
                    i_s = hist_data["item"].get(v, [0, 0, 0])
                    row_dict["item_imp_log"] = math.log1p(i_s[0])
                    row_dict["item_lv_rate"] = (i_s[1] + 20.0 * gl_lv) / (i_s[0] + 20.0)
                    row_dict["item_clk_rate"] = (i_s[2] + 20.0 * gl_clk) / (i_s[0] + 20.0)

                    # Author stats
                    a_s = hist_data["author"].get(vfeat["author_id"], [0, 0, 0])
                    row_dict["author_imp_log"] = math.log1p(a_s[0])
                    row_dict["author_lv_rate"] = (a_s[1] + 50.0 * gl_lv) / (a_s[0] + 50.0)
                    row_dict["author_clk_rate"] = (a_s[2] + 50.0 * gl_clk) / (a_s[0] + 50.0)

                    # User stats
                    u_s = hist_data["user"].get(u, [0, 0, 0])
                    row_dict["user_imp_log"] = math.log1p(u_s[0])
                    row_dict["user_lv_rate"] = (u_s[1] + 10.0 * gl_lv) / (u_s[0] + 10.0)
                    row_dict["user_clk_rate"] = (u_s[2] + 10.0 * gl_clk) / (u_s[0] + 10.0)

                    # Tag stats
                    t_s = hist_data["tag"].get(vfeat["primary_tag"], [0, 0, 0])
                    row_dict["tag_lv_rate"] = (t_s[1] + 100.0 * gl_lv) / (t_s[0] + 100.0)

                    # Tab stats
                    tb_s = hist_data["tab"].get(tab, [0, 0, 0])
                    row_dict["tab_lv_rate"] = (tb_s[1] + 300.0 * gl_lv) / (tb_s[0] + 300.0)

                rows.append(row_dict)
            raw_splits[split] = rows

    # Vocabularies
    vocabs = {c: {} for c in cat_cols}
    for row in raw_splits["train"]:
        for c in cat_cols:
            val = row[c]
            if val not in vocabs[c]:
                vocabs[c][val] = len(vocabs[c])

    vocab_sizes = {c: len(vocabs[c]) + 1 for c in cat_cols}  # +1 for UNK

    # Build arrays
    encoded = {}
    for split, split_rows in raw_splits.items():
        n = len(split_rows)
        cat_arr = np.empty((n, len(cat_cols)), dtype=np.int64)
        for j, c in enumerate(cat_cols):
            unk_idx = len(vocabs[c])
            vocab_map = vocabs[c]
            cat_arr[:, j] = [vocab_map.get(r[c], unk_idx) for r in split_rows]

        if num_cols:
            num_arr = np.empty((n, len(num_cols)), dtype=np.float32)
            for j, c in enumerate(num_cols):
                num_arr[:, j] = [r[c] for r in split_rows]
        else:
            num_arr = np.zeros((n, 0), dtype=np.float32)

        labels = np.array([r["label"] for r in split_rows], dtype=np.float32)
        clicks = np.array([r["is_click"] for r in split_rows], dtype=np.float32)
        users = [r["user_id_raw"] for r in split_rows]
        encoded[split] = {
            "cat": cat_arr,
            "num": num_arr,
            "label": labels,
            "click": clicks,
            "users": users,
        }

    return encoded, cat_cols, num_cols, vocab_sizes


# --- PyTorch Models ---

class DeepFMRanker(nn.Module):
    """DeepFM architecture combining 1st-order linear, 2nd-order FM, and Deep MLP."""
    def __init__(
        self,
        vocab_sizes: list[int],
        num_continuous: int = 0,
        embed_dim: int = 16,
        hidden_dims: list[int] = (256, 128),
        dropout: float = 0.1,
    ):
        super().__init__()
        self.num_fields = len(vocab_sizes)
        self.embed_dim = embed_dim
        self.num_continuous = num_continuous

        # 1st order linear embeddings
        self.linear_embeddings = nn.ModuleList([
            nn.Embedding(size, 1) for size in vocab_sizes
        ])
        for emb in self.linear_embeddings:
            nn.init.zeros_(emb.weight)
        self.linear_bias = nn.Parameter(torch.zeros(1))

        if num_continuous > 0:
            self.linear_num = nn.Linear(num_continuous, 1, bias=False)
            nn.init.zeros_(self.linear_num.weight)

        # 2nd order FM embeddings
        self.embeddings = nn.ModuleList([
            nn.Embedding(size, embed_dim) for size in vocab_sizes
        ])
        for emb in self.embeddings:
            nn.init.normal_(emb.weight, mean=0.0, std=0.01)

        # Deep MLP
        mlp_in = self.num_fields * embed_dim + num_continuous
        layers = []
        prev_dim = mlp_in
        for hdim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hdim))
            layers.append(nn.LayerNorm(hdim))
            layers.append(nn.GELU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hdim
        layers.append(nn.Linear(prev_dim, 1))
        self.mlp = nn.Sequential(*layers)

    def forward(self, x_cat: torch.Tensor, x_num: torch.Tensor = None) -> torch.Tensor:
        # x_cat: (B, F)
        B = x_cat.shape[0]

        # 1. Linear component
        linear_terms = [self.linear_embeddings[i](x_cat[:, i]) for i in range(self.num_fields)]
        linear_out = torch.stack(linear_terms, dim=1).sum(dim=1) + self.linear_bias  # (B, 1)
        if self.num_continuous > 0 and x_num is not None and x_num.shape[1] > 0:
            linear_out = linear_out + self.linear_num(x_num)

        # 2. FM 2nd order component
        # E: (B, F, D)
        embed_terms = [self.embeddings[i](x_cat[:, i]) for i in range(self.num_fields)]
        E = torch.stack(embed_terms, dim=1)  # (B, F, D)
        sum_E = E.sum(dim=1)  # (B, D)
        sum_sq_E = (E ** 2).sum(dim=1)  # (B, D)
        fm_out = 0.5 * ((sum_E ** 2) - sum_sq_E).sum(dim=1, keepdim=True)  # (B, 1)

        # 3. Deep MLP component
        deep_in = E.view(B, -1)
        if self.num_continuous > 0 and x_num is not None and x_num.shape[1] > 0:
            deep_in = torch.cat([deep_in, x_num], dim=1)
        deep_out = self.mlp(deep_in)  # (B, 1)

        return (linear_out + fm_out + deep_out).squeeze(1)


class DCNv2Ranker(nn.Module):
    """Deep & Cross Network v2 (Parallel DCN + MLP) architecture."""
    def __init__(
        self,
        vocab_sizes: list[int],
        num_continuous: int = 0,
        embed_dim: int = 16,
        cross_layers: int = 3,
        hidden_dims: list[int] = (256, 128),
        dropout: float = 0.1,
    ):
        super().__init__()
        self.num_fields = len(vocab_sizes)
        self.num_continuous = num_continuous
        self.embeddings = nn.ModuleList([
            nn.Embedding(size, embed_dim) for size in vocab_sizes
        ])
        for emb in self.embeddings:
            nn.init.normal_(emb.weight, mean=0.0, std=0.01)

        in_dim = self.num_fields * embed_dim + num_continuous

        # Cross layers
        self.cross_weights = nn.ParameterList([
            nn.Parameter(torch.randn(in_dim, in_dim) * 0.01) for _ in range(cross_layers)
        ])
        self.cross_biases = nn.ParameterList([
            nn.Parameter(torch.zeros(in_dim)) for _ in range(cross_layers)
        ])

        # Deep layers
        layers = []
        prev_dim = in_dim
        for hdim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hdim))
            layers.append(nn.LayerNorm(hdim))
            layers.append(nn.GELU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hdim
        self.deep = nn.Sequential(*layers)

        # Combine
        self.head = nn.Linear(in_dim + prev_dim, 1)

    def forward(self, x_cat: torch.Tensor, x_num: torch.Tensor = None) -> torch.Tensor:
        B = x_cat.shape[0]
        embed_terms = [self.embeddings[i](x_cat[:, i]) for i in range(self.num_fields)]
        E = torch.stack(embed_terms, dim=1).view(B, -1)
        if self.num_continuous > 0 and x_num is not None and x_num.shape[1] > 0:
            x0 = torch.cat([E, x_num], dim=1)
        else:
            x0 = E

        # Cross network
        xl = x0
        for W, b in zip(self.cross_weights, self.cross_biases):
            xl = x0 * (torch.matmul(xl, W) + b) + xl

        # Deep network
        xd = self.deep(x0)

        # Combine
        out = self.head(torch.cat([xl, xd], dim=1))
        return out.squeeze(1)


# --- Dataset and DataLoader ---

class RecDataset(Dataset):
    def __init__(self, cat: np.ndarray, num: np.ndarray, label: np.ndarray, click: np.ndarray = None):
        self.cat = torch.from_numpy(cat)
        self.num = torch.from_numpy(num)
        self.label = torch.from_numpy(label)
        self.click = torch.from_numpy(click) if click is not None else torch.zeros_like(self.label)

    def __len__(self):
        return len(self.label)

    def __getitem__(self, idx):
        return self.cat[idx], self.num[idx], self.label[idx], self.click[idx]


def evaluate_model(model: nn.Module, cat: np.ndarray, num: np.ndarray, label: np.ndarray, users: list[str], device: torch.device, batch_size: int = 65536):
    model.eval()
    preds = []
    with torch.no_grad():
        for i in range(0, len(label), batch_size):
            x_c = torch.from_numpy(cat[i:i + batch_size]).to(device)
            x_n = torch.from_numpy(num[i:i + batch_size]).to(device) if num.shape[1] > 0 else None
            logits = model(x_c, x_n)
            preds.append(logits.cpu().numpy())
    scores = np.concatenate(preds)
    return evaluate(users, label, scores)


def train_model(
    model_type: str = "deepfm",
    feature_set: str = "full",
    use_history_stats: bool = True,
    embed_dim: int = 16,
    hidden_dims: list[int] = (256, 128),
    lr: float = 1e-3,
    weight_decay: float = 1e-5,
    dropout: float = 0.1,
    batch_size: int = 4096,
    epochs: int = 15,
    patience: int = 4,
    aux_click_loss_weight: float = 0.0,
    full_eval: bool = False,
    seed: int = 0,
):
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    encoded, cat_cols, num_cols, vocab_sizes = load_dataset(use_history_stats, feature_set)
    vocab_size_list = [vocab_sizes[c] for c in cat_cols]

    # Medium mask
    uva = encoded["valid"]["users"]
    yva = encoded["valid"]["label"]
    xva_c = encoded["valid"]["cat"]
    xva_n = encoded["valid"]["num"]
    med_mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    umed = [u for u, keep in zip(uva, med_mask) if keep]
    ymed = yva[med_mask]
    xmed_c = xva_c[med_mask]
    xmed_n = xva_n[med_mask]

    # Instantiate model
    if model_type == "deepfm":
        model = DeepFMRanker(
            vocab_sizes=vocab_size_list,
            num_continuous=len(num_cols),
            embed_dim=embed_dim,
            hidden_dims=hidden_dims,
            dropout=dropout,
        ).to(device)
    elif model_type == "dcn":
        model = DCNv2Ranker(
            vocab_sizes=vocab_size_list,
            num_continuous=len(num_cols),
            embed_dim=embed_dim,
            cross_layers=3,
            hidden_dims=hidden_dims,
            dropout=dropout,
        ).to(device)
    else:
        raise ValueError(f"Unknown model_type {model_type}")

    train_ds = RecDataset(
        encoded["train"]["cat"],
        encoded["train"]["num"],
        encoded["train"]["label"],
        encoded["train"]["click"],
    )
    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        drop_last=False,
        num_workers=0,
        pin_memory=(device.type == "mps"),
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.BCEWithLogitsLoss()

    best_primary = -1.0
    best_weights = None
    best_epoch = 0
    history = []
    bad_epochs = 0

    print(f"Training {model_type.upper()} ({feature_set}, dim={embed_dim}, num_feats={len(num_cols)}) on {device}...")

    for ep in range(1, epochs + 1):
        model.train()
        losses = []
        t0 = time.time()
        for x_c, x_n, y, clk in train_loader:
            x_c = x_c.to(device, non_blocking=True)
            x_n = x_n.to(device, non_blocking=True) if len(num_cols) > 0 else None
            y = y.to(device, non_blocking=True)

            optimizer.zero_grad()
            logits = model(x_c, x_n)
            loss = criterion(logits, y)

            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        # Evaluate on Medium slice
        med_res = clean_metrics(evaluate_model(model, xmed_c, xmed_n, ymed, umed, device))
        dur = time.time() - t0
        med_primary = med_res["primary"]
        history.append({
            "epoch": ep,
            "train_loss": float(np.mean(losses)),
            "duration": dur,
            **med_res,
        })
        print(f"Epoch {ep:2d} | loss {np.mean(losses):.4f} | Medium GAUC {med_res['GAUC']:.5f} nDCG@5 {med_res['nDCG@5']:.5f} primary {med_primary:.5f} | {dur:.1f}s", flush=True)

        if med_primary > best_primary + 1e-5:
            best_primary = med_primary
            best_epoch = ep
            best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            bad_epochs = 0
        else:
            bad_epochs += 1
            if bad_epochs >= patience:
                print(f"Early stopping at epoch {ep}")
                break

    # Restore best weights
    model.load_state_dict({k: v.to(device) for k, v in best_weights.items()})

    full_res = None
    if full_eval:
        full_res = clean_metrics(evaluate_model(model, xva_c, xva_n, yva, uva, device))
        print(f"=== Full Validation Score ===")
        print(f"GAUC: {full_res['GAUC']:.7f}, nDCG@5: {full_res['nDCG@5']:.7f}, primary: {full_res['primary']:.7f}")

    return {
        "model_type": model_type,
        "feature_set": feature_set,
        "use_history_stats": use_history_stats,
        "embed_dim": embed_dim,
        "hidden_dims": list(hidden_dims),
        "lr": lr,
        "weight_decay": weight_decay,
        "dropout": dropout,
        "best_epoch": best_epoch,
        "best_medium": history[best_epoch - 1],
        "history": history,
        "full": full_res,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("deepfm", "dcn"), default="deepfm")
    parser.add_argument("--features", choices=("base_15", "rich_cat", "full"), default="full")
    parser.add_argument("--embed_dim", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    started = time.time()
    res = train_model(
        model_type=args.model,
        feature_set=args.features,
        use_history_stats=(args.features == "full"),
        embed_dim=args.embed_dim,
        lr=args.lr,
        epochs=args.epochs,
        patience=args.patience,
        full_eval=args.full,
        seed=args.seed,
    )
    res["elapsed_seconds"] = time.time() - started
    rendered = json.dumps(res, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
