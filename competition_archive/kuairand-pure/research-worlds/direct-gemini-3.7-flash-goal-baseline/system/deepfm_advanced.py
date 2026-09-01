"""Advanced Compact DeepFM with Multi-Task Learning, EMA, and Multi-Seed Ensembling."""

from __future__ import annotations

import csv
import math
import os
import time
from typing import Any, Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from starter_kit.evaluate import evaluate
from system.deep_high_signal import load_dataset, CompactDeepFM

LABEL = 'long_view'
SPLITS = {'train': (20220408, 20220421), 'valid': (20220422, 20220428)}


class MultiTaskCompactDeepFM(nn.Module):
    """Compact DeepFM with multi-task prediction for long_view and click."""

    def __init__(
        self,
        total_vocab: int,
        num_fields: int,
        k: int = 16,
        mlp_dim: int = 64,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.num_fields = num_fields
        self.k = k

        # Linear weights
        self.w = nn.Embedding(total_vocab, 1)
        nn.init.zeros_(self.w.weight)
        self.b_lv = nn.Parameter(torch.zeros(1))
        self.b_clk = nn.Parameter(torch.zeros(1))

        # FM embeddings
        self.v = nn.Embedding(total_vocab, k)
        nn.init.normal_(self.v.weight, std=0.01)

        # Shared MLP backbone
        in_dim = num_fields * k
        self.shared_mlp = nn.Sequential(
            nn.Linear(in_dim, mlp_dim),
            nn.LayerNorm(mlp_dim),
            nn.GELU(),
            nn.Dropout(dropout)
        )

        # Task heads
        self.head_lv = nn.Linear(mlp_dim, 1)
        self.head_clk = nn.Linear(mlp_dim, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # Linear
        lin_feat = self.w(x).sum(dim=1).squeeze(-1)
        lin_lv = self.b_lv + lin_feat
        lin_clk = self.b_clk + lin_feat

        # FM 2nd-order
        emb = self.v(x)  # (B, F, K)
        sum_e = emb.sum(dim=1)
        sum_sq = (emb ** 2).sum(dim=1)
        inter = 0.5 * (sum_e ** 2 - sum_sq).sum(dim=1)

        # Shared MLP
        flat = emb.view(emb.size(0), -1)
        feat = self.shared_mlp(flat)

        out_lv = lin_lv + inter + self.head_lv(feat).squeeze(-1)
        out_clk = lin_clk + inter + self.head_clk(feat).squeeze(-1)

        return out_lv, out_clk


class ModelEMA:
    """Exponential Moving Average of model parameters."""

    def __init__(self, model: nn.Module, decay: float = 0.999):
        self.model = model
        self.decay = decay
        self.shadow = {k: v.clone().detach() for k, v in model.state_dict().items()}

    def update(self):
        with torch.no_grad():
            for k, v in self.model.state_dict().items():
                if v.dtype.is_floating_point:
                    self.shadow[k].mul_(self.decay).add_(v, alpha=1.0 - self.decay)
                else:
                    self.shadow[k].copy_(v)

    def apply_shadow(self):
        self.model.load_state_dict(self.shadow)


def train_mt_deepfm(
    model: nn.Module,
    Xtr: torch.Tensor,
    ytr: torch.Tensor,
    clktr: torch.Tensor,
    Xva: torch.Tensor,
    yva: torch.Tensor,
    uva: List[str],
    lr: float = 5e-4,
    weight_decay: float = 5e-5,
    click_loss_weight: float = 0.3,
    epochs: int = 15,
    batch_size: int = 8192,
    patience: int = 4,
    use_ema: bool = True,
    device: str = "cpu",
    desc: str = ""
):
    dev = torch.device(device)
    model.to(dev)

    dataset = torch.utils.data.TensorDataset(Xtr, ytr, clktr)
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs * len(loader), eta_min=1e-5)
    bce = nn.BCEWithLogitsLoss()

    ema = ModelEMA(model, decay=0.995) if use_ema else None

    best_prim = -1.0
    best_state = None
    best_metrics = {}
    bad = 0

    print(f"\n--- Running: {desc} ---")
    for ep in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        n_b = 0
        t0 = time.time()

        for bx, by, bclk in loader:
            bx, by, bclk = bx.to(dev), by.to(dev), bclk.to(dev)
            optimizer.zero_grad()
            out_lv, out_clk = model(bx)
            loss = bce(out_lv, by) + click_loss_weight * bce(out_clk, bclk)
            loss.backward()
            optimizer.step()
            scheduler.step()
            if ema is not None:
                ema.update()
            total_loss += loss.item()
            n_b += 1

        # Validation (evaluating with EMA weights if enabled)
        eval_model = model
        if ema is not None:
            # create temp evaluation state
            current_state = {k: v.clone() for k, v in model.state_dict().items()}
            ema.apply_shadow()

        eval_model.eval()
        with torch.no_grad():
            va_scores = []
            for i in range(0, len(yva), 65536):
                vx = Xva[i:i + 65536].to(dev)
                out_lv, _ = eval_model(vx)
                va_scores.append(torch.sigmoid(out_lv).cpu().numpy())
            all_scores = np.concatenate(va_scores)
            va_res = evaluate(uva, yva.numpy().tolist(), all_scores.tolist())

        if ema is not None:
            model.load_state_dict(current_state)

        elapsed = time.time() - t0
        print(f"Ep {ep:2d} | loss {total_loss/n_b:.4f} | valid GAUC {va_res['GAUC']:.4f} nDCG@5 {va_res['nDCG@5']:.4f} primary {va_res['primary']:.4f} | {elapsed:.1f}s")

        if va_res['primary'] > best_prim + 1e-5:
            best_prim = va_res['primary']
            best_metrics = va_res
            bad = 0
            best_state = {k: v.cpu().clone() for k, v in (ema.shadow if ema else model.state_dict()).items()}
        else:
            bad += 1
            if bad >= patience:
                print(f"Early stopping at epoch {ep} (best primary {best_prim:.4f})")
                break

    model.load_state_dict(best_state)
    return best_metrics, model


def run_suite():
    data_dir = "competition_data/data"
    vid2meta = {}
    with open(os.path.join(data_dir, 'video_features_basic_pure.csv')) as fh:
        for r in csv.DictReader(fh):
            tag_str = r.get('tag', '')
            primary_tag = tag_str.split(',')[0] if tag_str else '0'
            vid2meta[r['video_id']] = {
                'author_id': r.get('author_id', 'UNK'),
                'tag': primary_tag,
            }

    rows = []
    for f in ('log_standard_4_08_to_4_21_pure.csv', 'log_public_4_22_to_4_28_pure.csv'):
        path = os.path.join(data_dir, f)
        if not os.path.exists(path):
            path = os.path.join(data_dir, 'log_standard_4_22_to_5_08_pure.csv')
        with open(path) as fh:
            for r in csv.DictReader(fh):
                vid = r['video_id']
                meta = vid2meta.get(vid, {})
                d_int = int(r['date'])
                dur = float(r['duration_ms']) if r.get('duration_ms') else 1.0
                hour = str(int(r['hourmin']) // 100) if r.get('hourmin') else '0'
                dow = str((d_int % 100) % 7)
                rows.append({
                    'date': d_int,
                    'user_id': r['user_id'],
                    'video_id': vid,
                    'author_id': meta.get('author_id', 'UNK'),
                    'tag': meta.get('tag', '0'),
                    'tab': r.get('tab', '0'),
                    'hour': hour,
                    'dow': dow,
                    'duration_ms': dur,
                    'label': 1 if r.get(LABEL, '0') != '0' else 0,
                    'is_click': 1 if r.get('is_click', '0') != '0' else 0,
                })

    train_rows = [x for x in rows if SPLITS['train'][0] <= x['date'] <= SPLITS['train'][1]]
    valid_rows = [x for x in rows if SPLITS['valid'][0] <= x['date'] <= SPLITS['valid'][1]]

    fields = ['user_id', 'video_id', 'author_id', 'tag', 'tab', 'hour', 'dow', 'dur_bucket']
    dur_edges = np.quantile([x['duration_ms'] for x in train_rows], np.linspace(0, 1, 11)[1:-1])

    def get_cats(x):
        return [
            x['user_id'], x['video_id'], x['author_id'], x['tag'], x['tab'],
            x['hour'], x['dow'], str(int(np.searchsorted(dur_edges, x['duration_ms'])))
        ]

    n_f = len(fields)
    vocabs = [dict() for _ in range(n_f)]
    for x in train_rows:
        for i, v in enumerate(get_cats(x)):
            if v not in vocabs[i]:
                vocabs[i][v] = len(vocabs[i])

    unk = [len(v) for v in vocabs]
    field_dims = [len(v) + 1 for v in vocabs]
    offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int64)

    def encode_split(rws):
        X = np.empty((len(rws), n_f), dtype=np.int64)
        y = np.empty(len(rws), dtype=np.float32)
        clk = np.empty(len(rws), dtype=np.float32)
        u_raw = []
        for j, x in enumerate(rws):
            for i, v in enumerate(get_cats(x)):
                X[j, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            y[j] = x['label']
            clk[j] = x['is_click']
            u_raw.append(x['user_id'])
        return torch.from_numpy(X), torch.from_numpy(y), torch.from_numpy(clk), u_raw

    Xtr, ytr, clktr, utr = encode_split(train_rows)
    Xva, yva, clkva, uva = encode_split(valid_rows)
    total_vocab = int(sum(field_dims))

    # 1. Multi-Task DeepFM with lr=5e-4, wd=5e-5, EMA
    mt_model = MultiTaskCompactDeepFM(total_vocab, n_f, k=16, mlp_dim=64, dropout=0.2)
    res_mt, trained_mt = train_mt_deepfm(
        mt_model, Xtr, ytr, clktr, Xva, yva, uva,
        lr=5e-4, weight_decay=5e-5, click_loss_weight=0.2, epochs=15, use_ema=True, desc="MT-DeepFM (k=16, EMA)"
    )
    print(f"\n>>> Best MT-DeepFM: GAUC {res_mt['GAUC']:.4f} | nDCG@5 {res_mt['nDCG@5']:.4f} | primary {res_mt['primary']:.4f}")

    # 2. 5-Seed Ensemble of MT-DeepFM
    print("\n--- Training 5-Seed MT-DeepFM Ensemble ---")
    seeds = [0, 1, 2, 3, 4]
    all_preds = []
    for s in seeds:
        torch.manual_seed(s)
        np.random.seed(s)
        m = MultiTaskCompactDeepFM(total_vocab, n_f, k=16, mlp_dim=64, dropout=0.2)
        res_s, trained_s = train_mt_deepfm(
            m, Xtr, ytr, clktr, Xva, yva, uva,
            lr=5e-4, weight_decay=5e-5, click_loss_weight=0.2, epochs=15, use_ema=True, desc=f"Seed {s}"
        )
        trained_s.eval()
        with torch.no_grad():
            p_s = []
            for i in range(0, len(yva), 65536):
                vx = Xva[i:i + 65536]
                out_lv, _ = trained_s(vx)
                p_s.append(torch.sigmoid(out_lv).numpy())
            p_s = np.concatenate(p_s)
        all_preds.append(p_s)
        print(f"Seed {s} standalone: GAUC {res_s['GAUC']:.4f} | nDCG@5 {res_s['nDCG@5']:.4f} | primary {res_s['primary']:.4f}")

    ens_preds = np.mean(all_preds, axis=0)
    ens_res = evaluate(uva, yva.numpy().tolist(), ens_preds.tolist())
    print(f"\n=======================================================")
    print(f">>> 5-Seed MT-DeepFM Ensemble Result on Valid:")
    print(f"    GAUC:    {ens_res['GAUC']:.4f}")
    print(f"    nDCG@5:  {ens_res['nDCG@5']:.4f}")
    print(f"    primary: {ens_res['primary']:.4f}")
    print(f"=======================================================")


if __name__ == '__main__':
    run_suite()
