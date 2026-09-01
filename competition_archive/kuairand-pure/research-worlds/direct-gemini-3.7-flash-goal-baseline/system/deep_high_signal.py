"""Targeted DeepFM and Neural Ranking Models on High-Signal Fields."""

from __future__ import annotations

import csv
import math
import os
import time
from collections import Counter
from typing import Any, Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from starter_kit.evaluate import evaluate

LABEL = 'long_view'
SPLITS = {'train': (20220408, 20220421), 'valid': (20220422, 20220428)}


def load_dataset(data_dir: str = "competition_data/data"):
    vid2meta = {}
    v_path = os.path.join(data_dir, 'video_features_basic_pure.csv')
    with open(v_path) as fh:
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
        u_raw = []
        for j, x in enumerate(rws):
            for i, v in enumerate(get_cats(x)):
                X[j, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            y[j] = x['label']
            u_raw.append(x['user_id'])
        return torch.from_numpy(X), torch.from_numpy(y), u_raw

    Xtr, ytr, utr_raw = encode_split(train_rows)
    Xva, yva, uva_raw = encode_split(valid_rows)

    return (Xtr, ytr, utr_raw), (Xva, yva, uva_raw), int(sum(field_dims)), n_f


class CompactDeepFM(nn.Module):
    """DeepFM restricted to high-signal fields with strong regularized MLP."""

    def __init__(
        self,
        total_vocab: int,
        num_fields: int,
        k: int = 16,
        mlp_dims: Tuple[int, ...] = (128, 64),
        dropout: float = 0.2,
        use_mlp: bool = True
    ):
        super().__init__()
        self.num_fields = num_fields
        self.k = k
        self.use_mlp = use_mlp

        # Linear weights
        self.w = nn.Embedding(total_vocab, 1)
        nn.init.zeros_(self.w.weight)
        self.b = nn.Parameter(torch.zeros(1))

        # FM embeddings
        self.v = nn.Embedding(total_vocab, k)
        nn.init.normal_(self.v.weight, std=0.01)

        # Deep MLP
        if use_mlp:
            in_dim = num_fields * k
            layers = []
            for h in mlp_dims:
                layers.append(nn.Linear(in_dim, h))
                layers.append(nn.LayerNorm(h))
                layers.append(nn.GELU())
                if dropout > 0:
                    layers.append(nn.Dropout(dropout))
                in_dim = h
            layers.append(nn.Linear(in_dim, 1))
            self.mlp = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Linear
        lin = self.b + self.w(x).sum(dim=1).squeeze(-1)  # (B,)

        # FM 2nd-order
        emb = self.v(x)  # (B, F, K)
        sum_e = emb.sum(dim=1)  # (B, K)
        sum_sq = (emb ** 2).sum(dim=1)  # (B, K)
        sq_sum = sum_e ** 2
        inter = 0.5 * (sq_sum - sum_sq).sum(dim=1)  # (B,)

        logits = lin + inter
        if self.use_mlp:
            flat = emb.view(emb.size(0), -1)  # (B, F*K)
            mlp_out = self.mlp(flat).squeeze(-1)
            logits = logits + mlp_out

        return logits


def train_and_eval(
    model: nn.Module,
    Xtr: torch.Tensor,
    ytr: torch.Tensor,
    Xva: torch.Tensor,
    yva: torch.Tensor,
    uva: List[str],
    lr: float = 1e-3,
    weight_decay: float = 2e-5,
    epochs: int = 15,
    batch_size: int = 8192,
    patience: int = 4,
    device: str = "cpu",
    desc: str = ""
):
    dev = torch.device(device)
    model.to(dev)

    dataset = torch.utils.data.TensorDataset(Xtr, ytr)
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs * len(loader), eta_min=1e-5)
    criterion = nn.BCEWithLogitsLoss()

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

        for bx, by in loader:
            bx, by = bx.to(dev), by.to(dev)
            optimizer.zero_grad()
            logits = model(bx)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()
            scheduler.step()
            total_loss += loss.item()
            n_b += 1

        # Validation
        model.eval()
        with torch.no_grad():
            va_scores = []
            for i in range(0, len(yva), 65536):
                vx = Xva[i:i + 65536].to(dev)
                va_scores.append(torch.sigmoid(model(vx)).cpu().numpy())
            all_scores = np.concatenate(va_scores)
            va_res = evaluate(uva, yva.numpy().tolist(), all_scores.tolist())

        elapsed = time.time() - t0
        print(f"Ep {ep:2d} | loss {total_loss/n_b:.4f} | valid GAUC {va_res['GAUC']:.4f} nDCG@5 {va_res['nDCG@5']:.4f} primary {va_res['primary']:.4f} | {elapsed:.1f}s")

        if va_res['primary'] > best_prim + 1e-5:
            best_prim = va_res['primary']
            best_metrics = va_res
            bad = 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                print(f"Early stopping at epoch {ep} (best primary {best_prim:.4f})")
                break

    model.load_state_dict(best_state)
    return best_metrics, model


def run_experiments():
    (Xtr, ytr, utr), (Xva, yva, uva), total_vocab, n_f = load_dataset()
    print(f"Loaded dataset: Vocab {total_vocab}, Fields {n_f}")

    configs = [
        # (use_mlp, k, mlp_dims, dropout, lr, wd, desc)
        (False, 16, (), 0.0, 1e-3, 3e-5, "FM (k=16, wd=3e-5)"),
        (False, 24, (), 0.0, 1e-3, 3e-5, "FM (k=24, wd=3e-5)"),
        (True, 16, (64,), 0.2, 1e-3, 3e-5, "DeepFM (k=16, MLP [64], drop=0.2)"),
        (True, 16, (128, 64), 0.2, 1e-3, 3e-5, "DeepFM (k=16, MLP [128,64], drop=0.2)"),
        (True, 24, (128, 64), 0.3, 1e-3, 5e-5, "DeepFM (k=24, MLP [128,64], drop=0.3, wd=5e-5)"),
    ]

    for use_mlp, k, mlp_dims, drop, lr, wd, desc in configs:
        model = CompactDeepFM(total_vocab, n_f, k=k, mlp_dims=mlp_dims, dropout=drop, use_mlp=use_mlp)
        res, _ = train_and_eval(model, Xtr, ytr, Xva, yva, uva, lr=lr, weight_decay=wd, epochs=15, desc=desc)
        print(f">>> Result for {desc}: GAUC {res['GAUC']:.4f} | nDCG@5 {res['nDCG@5']:.4f} | primary {res['primary']:.4f}")


if __name__ == '__main__':
    run_experiments()
