"""Pairwise BPR and User-Centered Ranking Trainer for KuaiRand-Pure."""

from __future__ import annotations

import csv
import math
import os
import time
from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from starter_kit.evaluate import evaluate

LABEL = 'long_view'
SPLITS = {'train': (20220408, 20220421), 'valid': (20220422, 20220428)}


def load_ranking_data(data_dir: str = "competition_data/data"):
    # 1. Video metadata
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

    # 2. Logs
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
                    'is_like': 1 if r.get('is_like', '0') != '0' else 0,
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
        click = np.empty(len(rws), dtype=np.float32)
        u_raw = []
        u_idx = np.empty(len(rws), dtype=np.int64)
        u_vocab = vocabs[0]
        for j, x in enumerate(rws):
            for i, v in enumerate(get_cats(x)):
                X[j, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            y[j] = x['label']
            click[j] = x['is_click']
            u_raw.append(x['user_id'])
            u_idx[j] = u_vocab.get(x['user_id'], unk[0])

        return X, y, click, u_raw, u_idx

    Xtr, ytr, clktr, utr_raw, utr_idx = encode_split(train_rows)
    Xva, yva, clkva, uva_raw, uva_idx = encode_split(valid_rows)

    return (
        (torch.from_numpy(Xtr), torch.from_numpy(ytr), torch.from_numpy(clktr), utr_raw, torch.from_numpy(utr_idx)),
        (torch.from_numpy(Xva), torch.from_numpy(yva), torch.from_numpy(clkva), uva_raw, torch.from_numpy(uva_idx)),
        int(sum(field_dims)),
        n_f
    )


class PyTorchRankingFM(nn.Module):
    """Clean, high-performance PyTorch Factorization Machine."""

    def __init__(self, total_vocab: int, num_fields: int, k: int = 16):
        super().__init__()
        self.num_fields = num_fields
        self.k = k
        
        self.w = nn.Embedding(total_vocab, 1)
        nn.init.zeros_(self.w.weight)
        
        self.v = nn.Embedding(total_vocab, k)
        nn.init.normal_(self.v.weight, std=0.01)
        
        self.b = nn.Parameter(torch.zeros(1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, num_fields)
        # Linear:
        lin = self.b + self.w(x).sum(dim=1).squeeze(-1)  # (B,)
        
        # FM 2nd-order:
        emb = self.v(x)  # (B, F, K)
        sum_e = emb.sum(dim=1)  # (B, K)
        sum_sq = (emb ** 2).sum(dim=1)  # (B, K)
        sq_sum = sum_e ** 2  # (B, K)
        inter = 0.5 * (sq_sum - sum_sq).sum(dim=1)  # (B,)
        
        return lin + inter


def train_ranking_model(
    train_data,
    valid_data,
    total_vocab: int,
    num_fields: int,
    k: int = 16,
    lr: float = 1e-3,
    weight_decay: float = 1e-5,
    bce_weight: float = 1.0,
    pair_weight: float = 0.5,
    epochs: int = 20,
    batch_size: int = 8192,
    patience: int = 4,
    device_name: str = "cpu",
    verbose: bool = True
):
    device = torch.device(device_name)
    Xtr, ytr, clktr, utr_raw, utr_idx = train_data
    Xva, yva, clkva, uva_raw, uva_idx = valid_data

    model = PyTorchRankingFM(total_vocab, num_fields, k=k).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs * (len(ytr) // batch_size + 1), eta_min=1e-5)

    dataset = torch.utils.data.TensorDataset(Xtr, ytr, clktr, utr_idx)
    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

    bce_loss_fn = nn.BCEWithLogitsLoss()

    best_prim = -1.0
    best_state = None
    best_metrics = {}
    bad = 0

    for ep in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        n_b = 0
        t0 = time.time()

        for bx, by, bclk, bu in loader:
            bx = bx.to(device)
            by = by.to(device)
            bu = bu.to(device)

            optimizer.zero_grad()
            logits = model(bx)

            # Pointwise BCE
            loss = bce_weight * bce_loss_fn(logits, by)

            # Within-batch Pairwise BPR
            if pair_weight > 0:
                pos_mask = (by > 0.5)
                neg_mask = (by < 0.5)
                pos_l = logits[pos_mask]
                neg_l = logits[neg_mask]
                if len(pos_l) > 0 and len(neg_l) > 0:
                    n_pairs = min(len(pos_l), len(neg_l), 4096)
                    p_loss = -torch.mean(F.logsigmoid(pos_l[:n_pairs] - neg_l[:n_pairs]))
                    loss = loss + pair_weight * p_loss

            loss.backward()
            optimizer.step()
            scheduler.step()

            total_loss += loss.item()
            n_b += 1

        # Validation evaluation
        model.eval()
        with torch.no_grad():
            va_scores = []
            for i in range(0, len(yva), 65536):
                vx = Xva[i:i + 65536].to(device)
                va_scores.append(torch.sigmoid(model(vx)).cpu().numpy())
            all_scores = np.concatenate(va_scores)
            va_res = evaluate(uva_raw, yva.numpy().tolist(), all_scores.tolist())

        elapsed = time.time() - t0
        if verbose:
            print(f"Ep {ep:2d} | loss {total_loss/n_b:.4f} | valid GAUC {va_res['GAUC']:.4f} nDCG@5 {va_res['nDCG@5']:.4f} primary {va_res['primary']:.4f} | {elapsed:.1f}s")

        if va_res['primary'] > best_prim + 1e-5:
            best_prim = va_res['primary']
            best_metrics = va_res
            bad = 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                if verbose:
                    print(f"Early stop at epoch {ep} (best primary {best_prim:.4f})")
                break

    model.load_state_dict(best_state)
    return best_metrics, model


if __name__ == '__main__':
    t0 = time.time()
    tr_d, va_d, total_vocab, n_f = load_ranking_data()
    print(f"Loaded ranking data in {time.time()-t0:.1f}s. Vocab: {total_vocab}, Fields: {n_f}")

    experiments = [
        # (bce_w, pair_w, lr, wd, desc)
        (1.0, 0.0, 1e-3, 3e-5, "Pointwise BCE only (pair_w=0.0)"),
        (1.0, 0.1, 1e-3, 3e-5, "BCE + Pairwise BPR (pair_w=0.1)"),
        (1.0, 0.2, 1e-3, 3e-5, "BCE + Pairwise BPR (pair_w=0.2)"),
        (1.0, 0.5, 1e-3, 3e-5, "BCE + Pairwise BPR (pair_w=0.5)"),
        (0.5, 1.0, 1e-3, 3e-5, "Ranking Focused (bce_w=0.5, pair_w=1.0)"),
    ]

    for bce_w, pair_w, lr, wd, desc in experiments:
        print(f"\n--- {desc} ---")
        best_m, _ = train_ranking_model(
            tr_d, va_d, total_vocab, n_f,
            k=16, lr=lr, weight_decay=wd,
            bce_weight=bce_w, pair_weight=pair_w,
            epochs=20, patience=4, device_name="cpu"
        )
        print(f"Best Result: GAUC {best_m['GAUC']:.4f} | nDCG@5 {best_m['nDCG@5']:.4f} | primary {best_m['primary']:.4f}")
