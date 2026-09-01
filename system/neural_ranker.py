#!/usr/bin/env python3
"""Multi-task deep ranking network (Multi-Task DeepFM + Pairwise Ranking) for KuaiRand-Pure.

Features:
- 39 categorical fields with embedding lookup (user profile, video metadata, context).
- 12 normalized continuous / historical Bayesian shrinkage rates computed strictly on train log.
- Multi-Task heads: Long View (primary), Completion Rate (dense supervision), Click.
- Loss: Pointwise BCE + Multi-Task Auxiliary BCE + Within-batch Pairwise BPR Ranking Loss.
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
    return int(hashlib.blake2b(user_id.encode(), digest_size=4).hexdigest(), 16) % 4 == 0


def clean_metrics(metrics: dict) -> dict:
    return {k: int(v) if k in ("users", "rows") else float(v) for k, v in metrics.items()}


def extract_features():
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

    # 3. Compute historical stats strictly from training log
    item_stats = defaultdict(lambda: [0, 0, 0])  # [imp, long_view, click]
    author_stats = defaultdict(lambda: [0, 0, 0])
    user_stats = defaultdict(lambda: [0, 0, 0])
    tag_stats = defaultdict(lambda: [0, 0, 0])
    tab_stats = defaultdict(lambda: [0, 0, 0])
    total_imp = total_long = total_click = 0

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


def load_dataset():
    user_features, video_features, hist_data = extract_features()

    dur_cuts = np.array([15000, 30000, 45000, 60000, 90000, 120000, 180000, 300000])
    files = {
        "train": "log_standard_4_08_to_4_21_pure.csv",
        "valid": "log_public_4_22_to_4_28_pure.csv",
    }

    cat_cols = [
        "user_id", "video_id", "author_id", "tab", "dur_bucket",
        "hour", "weekday", "video_type", "upload_type", "music_type", "primary_tag", "aspect_bucket",
        "active_degree", "is_lowactive", "is_live_streamer", "is_video_author",
        "follow_range", "fans_range", "friend_range", "register_range",
        *[f"onehot_{i}" for i in range(18)],
    ]
    num_cols = [
        "duration_log",
        "item_imp_log", "item_lv_rate", "item_clk_rate",
        "author_imp_log", "author_lv_rate", "author_clk_rate",
        "user_imp_log", "user_lv_rate", "user_clk_rate",
        "tag_lv_rate", "tab_lv_rate",
    ]

    raw_splits = {}
    gl_lv = hist_data["global_long_rate"]
    gl_clk = hist_data["global_click_rate"]

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

                # Targets
                lv = 1.0 if r["long_view"] == "1" else 0.0
                clk = 1.0 if r.get("is_click", "0") == "1" else 0.0
                p_ms = float(r.get("play_time_ms", "0") or 0)
                d_ms = max(dur, 1000.0)
                comp = min(1.0, max(0.0, p_ms / d_ms))

                # Numerical features
                i_s = hist_data["item"].get(v, [0, 0, 0])
                a_s = hist_data["author"].get(vfeat["author_id"], [0, 0, 0])
                u_s = hist_data["user"].get(u, [0, 0, 0])
                t_s = hist_data["tag"].get(vfeat["primary_tag"], [0, 0, 0])
                tb_s = hist_data["tab"].get(tab, [0, 0, 0])

                row_num = [
                    math.log1p(dur),
                    math.log1p(i_s[0]),
                    (i_s[1] + 20.0 * gl_lv) / (i_s[0] + 20.0),
                    (i_s[2] + 20.0 * gl_clk) / (i_s[0] + 20.0),
                    math.log1p(a_s[0]),
                    (a_s[1] + 50.0 * gl_lv) / (a_s[0] + 50.0),
                    (a_s[2] + 50.0 * gl_clk) / (a_s[0] + 50.0),
                    math.log1p(u_s[0]),
                    (u_s[1] + 10.0 * gl_lv) / (u_s[0] + 10.0),
                    (u_s[2] + 10.0 * gl_clk) / (u_s[0] + 10.0),
                    (t_s[1] + 100.0 * gl_lv) / (t_s[0] + 100.0),
                    (tb_s[1] + 300.0 * gl_lv) / (tb_s[0] + 300.0),
                ]

                rows.append({
                    "cat": [row_cat.get(k, "UNK") for k in cat_cols],
                    "num": row_num,
                    "label": lv,
                    "comp": comp,
                    "click": clk,
                    "user_id_raw": u,
                })
            raw_splits[split] = rows

    # Vocabularies
    vocabs = [{} for _ in cat_cols]
    for row in raw_splits["train"]:
        for i, val in enumerate(row["cat"]):
            if val not in vocabs[i]:
                vocabs[i][val] = len(vocabs[i])

    vocab_sizes = [len(v) + 1 for v in vocabs]

    # Pre-encode as NumPy arrays
    encoded = {}
    for split, split_rows in raw_splits.items():
        n = len(split_rows)
        cat_arr = np.empty((n, len(cat_cols)), dtype=np.int64)
        for j in range(len(cat_cols)):
            unk_idx = len(vocabs[j])
            vocab_map = vocabs[j]
            cat_arr[:, j] = [vocab_map.get(r["cat"][j], unk_idx) for r in split_rows]

        num_arr = np.array([r["num"] for r in split_rows], dtype=np.float32)
        # Normalize continuous features with train mean and std
        if split == "train":
            num_mean = num_arr.mean(axis=0, keepdims=True)
            num_std = num_arr.std(axis=0, keepdims=True) + 1e-6

        labels = np.array([r["label"] for r in split_rows], dtype=np.float32)
        comps = np.array([r["comp"] for r in split_rows], dtype=np.float32)
        clicks = np.array([r["click"] for r in split_rows], dtype=np.float32)
        users = [r["user_id_raw"] for r in split_rows]

        encoded[split] = {
            "cat": cat_arr,
            "num": (num_arr - num_mean) / num_std,
            "label": labels,
            "comp": comps,
            "click": clicks,
            "users": users,
        }

    return encoded, cat_cols, num_cols, vocab_sizes


# --- Multi-Task DeepFM Architecture ---

class MultiTaskDeepFM(nn.Module):
    def __init__(
        self,
        vocab_sizes: list[int],
        num_continuous: int,
        embed_dim: int = 16,
        hidden_dims: list[int] = (512, 256, 128),
        dropout: float = 0.1,
    ):
        super().__init__()
        self.num_fields = len(vocab_sizes)
        self.embed_dim = embed_dim
        self.num_continuous = num_continuous

        # 1. Linear component
        self.linear_embeddings = nn.ModuleList([
            nn.Embedding(size, 1) for size in vocab_sizes
        ])
        for emb in self.linear_embeddings:
            nn.init.zeros_(emb.weight)
        self.linear_bias = nn.Parameter(torch.zeros(1))
        self.linear_num = nn.Linear(num_continuous, 1, bias=False)
        nn.init.zeros_(self.linear_num.weight)

        # 2. FM 2nd-order embeddings
        self.embeddings = nn.ModuleList([
            nn.Embedding(size, embed_dim) for size in vocab_sizes
        ])
        for emb in self.embeddings:
            nn.init.normal_(emb.weight, mean=0.0, std=0.01)

        # 3. Deep MLP Trunk
        mlp_in = self.num_fields * embed_dim + num_continuous
        layers = []
        prev_dim = mlp_in
        for hdim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hdim))
            layers.append(nn.LayerNorm(hdim))
            layers.append(nn.GELU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hdim
        self.trunk = nn.Sequential(*layers)

        # 4. Multi-Task Heads
        self.head_long_view = nn.Linear(prev_dim, 1)
        self.head_completion = nn.Linear(prev_dim, 1)
        self.head_click = nn.Linear(prev_dim, 1)

    def forward(self, x_cat: torch.Tensor, x_num: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        B = x_cat.shape[0]

        # 1. Linear
        linear_terms = [self.linear_embeddings[i](x_cat[:, i]) for i in range(self.num_fields)]
        linear_out = torch.stack(linear_terms, dim=1).sum(dim=1) + self.linear_bias + self.linear_num(x_num)  # (B, 1)

        # 2. FM 2nd order
        embed_terms = [self.embeddings[i](x_cat[:, i]) for i in range(self.num_fields)]
        E = torch.stack(embed_terms, dim=1)  # (B, F, D)
        sum_E = E.sum(dim=1)  # (B, D)
        sum_sq_E = (E ** 2).sum(dim=1)  # (B, D)
        fm_out = 0.5 * ((sum_E ** 2) - sum_sq_E).sum(dim=1, keepdim=True)  # (B, 1)

        # 3. Deep Trunk
        deep_in = torch.cat([E.view(B, -1), x_num], dim=1)
        feat = self.trunk(deep_in)  # (B, H)

        # 4. Heads
        base_logit = linear_out + fm_out
        out_long = (base_logit + self.head_long_view(feat)).squeeze(1)
        out_comp = (base_logit + self.head_completion(feat)).squeeze(1)
        out_click = (base_logit + self.head_click(feat)).squeeze(1)

        return out_long, out_comp, out_click


# --- Pairwise Ranking Loss ---

def compute_pairwise_loss(logits: torch.Tensor, labels: torch.Tensor, user_ids: torch.Tensor = None) -> torch.Tensor:
    """Efficient sampled pairwise BPR loss between positive and negative samples in the mini-batch."""
    pos_mask = (labels > 0.5)
    neg_mask = (labels < 0.5)
    pos_logits = logits[pos_mask]
    neg_logits = logits[neg_mask]

    if len(pos_logits) == 0 or len(neg_logits) == 0:
        return torch.tensor(0.0, device=logits.device)

    # Randomly sample pairs to keep computation O(N)
    n_pairs = min(len(pos_logits), len(neg_logits), 4096)
    idx_p = torch.randint(0, len(pos_logits), (n_pairs,), device=logits.device)
    idx_n = torch.randint(0, len(neg_logits), (n_pairs,), device=logits.device)

    diff = pos_logits[idx_p] - neg_logits[idx_n]
    return F.softplus(-diff).mean()


# --- Fast Tensor Dataset ---

class FastTensorDataset(Dataset):
    def __init__(self, cat, num, label, comp, click):
        self.cat = torch.from_numpy(cat)
        self.num = torch.from_numpy(num)
        self.label = torch.from_numpy(label)
        self.comp = torch.from_numpy(comp)
        self.click = torch.from_numpy(click)

    def __len__(self):
        return len(self.label)

    def __getitem__(self, idx):
        return self.cat[idx], self.num[idx], self.label[idx], self.comp[idx], self.click[idx]


def evaluate_fast(model: nn.Module, cat: np.ndarray, num: np.ndarray, label: np.ndarray, users: list[str], device: torch.device, batch_size: int = 65536):
    model.eval()
    preds = []
    with torch.no_grad():
        for i in range(0, len(label), batch_size):
            x_c = torch.from_numpy(cat[i:i + batch_size]).to(device)
            x_n = torch.from_numpy(num[i:i + batch_size]).to(device)
            out_long, _, _ = model(x_c, x_n)
            preds.append(out_long.cpu().numpy())
    scores = np.concatenate(preds)
    return evaluate(users, label, scores)


def train_neural_ranker(
    embed_dim: int = 16,
    hidden_dims: list[int] = (512, 256, 128),
    lr: float = 1e-3,
    weight_decay: float = 1e-5,
    dropout: float = 0.1,
    batch_size: int = 4096,
    epochs: int = 15,
    patience: int = 4,
    w_comp: float = 0.3,
    w_click: float = 0.2,
    w_pair: float = 0.2,
    full_eval: bool = False,
    seed: int = 0,
):
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    encoded, cat_cols, num_cols, vocab_sizes = load_dataset()

    # Medium validation partition
    uva = encoded["valid"]["users"]
    yva = encoded["valid"]["label"]
    xva_c = encoded["valid"]["cat"]
    xva_n = encoded["valid"]["num"]
    med_mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    umed = [u for u, keep in zip(uva, med_mask) if keep]
    ymed = yva[med_mask]
    xmed_c = xva_c[med_mask]
    xmed_n = xva_n[med_mask]

    model = MultiTaskDeepFM(
        vocab_sizes=vocab_sizes,
        num_continuous=len(num_cols),
        embed_dim=embed_dim,
        hidden_dims=hidden_dims,
        dropout=dropout,
    ).to(device)

    train_ds = FastTensorDataset(
        encoded["train"]["cat"],
        encoded["train"]["num"],
        encoded["train"]["label"],
        encoded["train"]["comp"],
        encoded["train"]["click"],
    )
    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        drop_last=False,
        num_workers=0,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    bce = nn.BCEWithLogitsLoss()

    best_primary = -1.0
    best_weights = None
    best_epoch = 0
    history = []
    bad_epochs = 0

    print(f"Training MultiTaskDeepFM (dim={embed_dim}, feats={len(cat_cols)}+{len(num_cols)}, w_comp={w_comp}, w_clk={w_click}, w_pair={w_pair}) on {device}...")

    for ep in range(1, epochs + 1):
        model.train()
        losses = []
        t0 = time.time()
        for x_c, x_n, y_lv, y_comp, y_clk in train_loader:
            x_c = x_c.to(device)
            x_n = x_n.to(device)
            y_lv = y_lv.to(device)
            y_comp = y_comp.to(device)
            y_clk = y_clk.to(device)

            optimizer.zero_grad()
            out_lv, out_comp, out_clk = model(x_c, x_n)

            l_lv = bce(out_lv, y_lv)
            l_comp = bce(out_comp, y_comp)
            l_clk = bce(out_clk, y_clk)
            l_pair = compute_pairwise_loss(out_lv, y_lv)

            loss = l_lv + w_comp * l_comp + w_click * l_clk + w_pair * l_pair
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        scheduler.step()
        # Evaluate on Medium slice
        med_res = clean_metrics(evaluate_fast(model, xmed_c, xmed_n, ymed, umed, device))
        dur = time.time() - t0
        med_primary = med_res["primary"]
        history.append({
            "epoch": ep,
            "train_loss": float(np.mean(losses)),
            "duration": dur,
            **med_res,
        })
        print(f"Epoch {ep:2d} | loss {np.mean(losses):.4f} | Med GAUC {med_res['GAUC']:.5f} nDCG@5 {med_res['nDCG@5']:.5f} primary {med_primary:.5f} | {dur:.1f}s", flush=True)

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
        full_res = clean_metrics(evaluate_fast(model, xva_c, xva_n, yva, uva, device))
        print(f"=== Full Validation Score ===")
        print(f"GAUC: {full_res['GAUC']:.7f}, nDCG@5: {full_res['nDCG@5']:.7f}, primary: {full_res['primary']:.7f}")

    return {
        "model_type": "MultiTaskDeepFM",
        "embed_dim": embed_dim,
        "hidden_dims": list(hidden_dims),
        "lr": lr,
        "weight_decay": weight_decay,
        "dropout": dropout,
        "w_comp": w_comp,
        "w_click": w_click,
        "w_pair": w_pair,
        "best_epoch": best_epoch,
        "best_medium": history[best_epoch - 1],
        "history": history,
        "full": full_res,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--embed_dim", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight_decay", type=float, default=1e-5)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--w_comp", type=float, default=0.3)
    parser.add_argument("--w_click", type=float, default=0.2)
    parser.add_argument("--w_pair", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    started = time.time()
    res = train_neural_ranker(
        embed_dim=args.embed_dim,
        lr=args.lr,
        weight_decay=args.weight_decay,
        dropout=args.dropout,
        epochs=args.epochs,
        patience=args.patience,
        w_comp=args.w_comp,
        w_click=args.w_click,
        w_pair=args.w_pair,
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
