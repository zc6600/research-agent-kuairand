#!/usr/bin/env python3
"""
Round 01 - Variant v1: Video Metadata Extension (8 fields)
Fields: user_id, video_id, author_id, music_id, video_type, upload_type, tab, dur_bucket
Model: Factorization Machine (FM) with k=16, lr=0.001, batch=8192, max_epochs=25, patience=4
Target dataset: KuaiRand-Pure
"""

import argparse
import csv
import math
import os
import sys
import time
import collections
import numpy as np

# ---------------- Evaluator (Official starter_kit/evaluate.py Semantics) ----------------
def auc(labels, scores):
    """Mann-Whitney U with tie correction, equivalent to sklearn.metrics.roc_auc_score."""
    pairs = sorted(zip(scores, labels))
    ranks = [0.0] * len(pairs)
    i = 0
    while i < len(pairs):
        j = i
        while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    npos = sum(l for _, l in pairs)
    nneg = len(pairs) - npos
    if npos == 0 or nneg == 0:
        return 0.5
    srank = sum(r for r, (_, l) in zip(ranks, pairs) if l == 1)
    return (srank - npos * (npos + 1) / 2.0) / (npos * nneg)

def ndcg_at_k(labels, k=5):
    """labels ranked by descending predicted scores."""
    disc = [math.log2(i + 2) for i in range(k)]
    dcg = sum(((2 ** t) - 1) / disc[i] for i, t in enumerate(labels[:k]))
    ideal = sorted(labels, reverse=True)[:k]
    idcg = sum(((2 ** t) - 1) / disc[i] for i, t in enumerate(ideal))
    return 0.0 if idcg == 0 else dcg / idcg

def evaluate(user_ids, labels, scores, k=5):
    """Returns {'GAUC': ..., 'nDCG@5': ..., 'primary': ..., 'users': ..., 'rows': ...}."""
    byu = collections.defaultdict(list)
    for u, y, s in zip(user_ids, labels, scores):
        byu[u].append((s, y))
    gnum = gden = 0.0
    nd = []
    for u, lst in byu.items():
        lst.sort(key=lambda x: -x[0])
        labs = [y for _, y in lst]
        npos = sum(labs)
        if 0 < npos < len(labs):
            gnum += npos * auc(labs, [s for s, _ in lst])
            gden += npos
        nd.append(ndcg_at_k(labs, k))
    gauc = gnum / gden if gden else 0.5
    ndcg = sum(nd) / len(nd) if nd else 0.0
    return {
        'GAUC': gauc,
        f'nDCG@{k}': ndcg,
        'primary': (gauc + ndcg) / 2.0,
        'users': len(byu),
        'rows': len(labels)
    }

# ---------------- Model: Factorization Machine ----------------
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

class FM:
    def __init__(self, dim, k=16, lr=0.001, l2=1e-6, seed=0):
        rng = np.random.default_rng(seed)
        self.dim = dim
        self.k = k
        self.lr = lr
        self.l2 = l2
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W = np.zeros(dim, dtype=np.float32)
        self.b = np.float32(0.0)
        self.mV = np.zeros_like(self.V)
        self.vV = np.zeros_like(self.V)
        self.mW = np.zeros_like(self.W)
        self.vW = np.zeros_like(self.W)
        self.t = 0

    def logits(self, X):
        # X: (B, F)
        E = self.V[X]                                   # (B, F, k)
        S = E.sum(axis=1)                               # (B, k)
        inter = 0.5 * ((S ** 2).sum(axis=1) - (E ** 2).sum(axis=(1, 2))) # (B,)
        linear = self.W[X].sum(axis=1)                  # (B,)
        return self.b + linear + inter, E, S

    def step(self, X, y):
        B = len(y)
        z, E, S = self.logits(X)
        pred = sigmoid(z)
        g = ((pred - y) / B).astype(np.float32)         # (B,)
        gV = np.zeros_like(self.V)
        gW = np.zeros_like(self.W)
        np.add.at(gW, X, g[:, None])
        np.add.at(gV, X, g[:, None, None] * (S[:, None, :] - E))
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
        loss = -np.mean(y * np.log(pred + 1e-9) + (1 - y) * np.log(1 - pred + 1e-9))
        return float(loss)

    def predict(self, X, bs=200_000):
        if len(X) == 0:
            return np.empty(0, dtype=np.float32)
        preds = []
        for i in range(0, len(X), bs):
            z, _, _ = self.logits(X[i:i + bs])
            preds.append(z)
        return np.concatenate(preds)

# ---------------- Data Loading and Feature Engineering ----------------
FIELDS = ['user_id', 'video_id', 'author_id', 'music_id', 'video_type', 'upload_type', 'tab', 'dur_bucket']

def load_data(data_dir):
    print(f"Loading video features from {os.path.join(data_dir, 'video_features_basic_pure.csv')}...")
    vid2meta = {}
    with open(os.path.join(data_dir, 'video_features_basic_pure.csv')) as fh:
        for r in csv.DictReader(fh):
            vid2meta[r['video_id']] = (
                r.get('author_id', 'UNK') or 'UNK',
                r.get('music_id', 'UNK') or 'UNK',
                r.get('video_type', 'UNK') or 'UNK',
                r.get('upload_type', 'UNK') or 'UNK'
            )
    print(f"Loaded metadata for {len(vid2meta)} videos.")

    def parse_log(filename):
        filepath = os.path.join(data_dir, filename)
        print(f"Loading log file {filepath}...")
        rows = []
        with open(filepath) as fh:
            for r in csv.DictReader(fh):
                uid = r['user_id']
                vid = r['video_id']
                tab = r['tab']
                dur = float(r['duration_ms'])
                label = 1.0 if r['long_view'] != '0' else 0.0
                meta = vid2meta.get(vid, ('UNK', 'UNK', 'UNK', 'UNK'))
                rows.append((uid, vid, meta[0], meta[1], meta[2], meta[3], tab, dur, label))
        print(f"Loaded {len(rows)} interactions from {filename}.")
        return rows

    train_raw = parse_log('log_standard_4_08_to_4_21_pure.csv')
    valid_raw = parse_log('log_public_4_22_to_4_28_pure.csv')
    return train_raw, valid_raw

def encode_data(train_raw, valid_raw, n_dur_buckets=10):
    print("Computing duration quantile buckets strictly on training split...")
    train_durations = [x[7] for x in train_raw]
    edges = np.quantile(np.asarray(train_durations), np.linspace(0, 1, n_dur_buckets + 1)[1:-1])

    def get_features(x):
        # x: (uid, vid, author_id, music_id, video_type, upload_type, tab, dur, label)
        dur_b = str(int(np.searchsorted(edges, x[7])))
        return [x[0], x[1], x[2], x[3], x[4], x[5], x[6], dur_b]

    print("Building field vocabularies strictly on training split...")
    vocabs = [dict() for _ in FIELDS]
    for x in train_raw:
        feats = get_features(x)
        for i, val in enumerate(feats):
            if val not in vocabs[i]:
                vocabs[i][val] = len(vocabs[i])

    unk_indices = [len(v) for v in vocabs]
    field_dims = [len(v) + 1 for v in vocabs]
    total_dim = int(sum(field_dims))
    offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int32)

    print(f"Field summary ({len(FIELDS)} fields):")
    for fname, dim, unk_idx in zip(FIELDS, field_dims, unk_indices):
        print(f"  Field '{fname}': {dim} unique categories (including UNK at slot {unk_idx})")
    print(f"Total vocabulary dimension: {total_dim}")

    def transform(raw_dataset, name="split"):
        N = len(raw_dataset)
        X = np.empty((N, len(FIELDS)), dtype=np.int32)
        y = np.empty(N, dtype=np.float32)
        users = []
        for j, x in enumerate(raw_dataset):
            feats = get_features(x)
            for i, val in enumerate(feats):
                X[j, i] = vocabs[i].get(val, unk_indices[i]) + offsets[i]
            y[j] = x[8]
            users.append(x[0])
        return X, y, users

    print("Transforming training dataset...")
    Xtr, ytr, utr = transform(train_raw, "train")
    print("Transforming validation dataset...")
    Xva, yva, uva = transform(valid_raw, "valid")

    return (Xtr, ytr, utr), (Xva, yva, uva), total_dim, field_dims

# ---------------- Training Routine ----------------
def train_and_eval(train_data, valid_data, total_dim, k=16, lr=0.001, batch_size=8192,
                   max_epochs=25, patience=4, seed=0):
    Xtr, ytr, utr = train_data
    Xva, yva, uva = valid_data

    print(f"\nInitializing FM model (dim={total_dim}, k={k}, lr={lr}, batch_size={batch_size}, seed={seed})...")
    m = FM(total_dim, k=k, lr=lr, seed=seed)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_va_metrics = None
    best_epoch = 0
    best_state = None
    bad_epochs = 0

    print(f"Beginning training (max_epochs={max_epochs}, patience={patience})...\n")
    t_start = time.time()
    epoch_logs = []

    for ep in range(1, max_epochs + 1):
        t0 = time.time()
        perm = rng.permutation(len(ytr))
        batch_losses = []
        for i in range(0, len(perm), batch_size):
            b_idx = perm[i:i + batch_size]
            loss = m.step(Xtr[b_idx], ytr[b_idx])
            batch_losses.append(loss)
        
        train_loss = float(np.mean(batch_losses))
        val_preds = m.predict(Xva)
        va = evaluate(uva, yva, val_preds)
        ep_duration = time.time() - t0

        log_str = (f"Epoch {ep:2d}/{max_epochs:2d} | Train Loss: {train_loss:.4f} | "
                   f"Val GAUC: {va['GAUC']:.4f} | Val nDCG@5: {va['nDCG@5']:.4f} | "
                   f"Val Primary: {va['primary']:.4f} | Time: {ep_duration:.2f}s")
        print(log_str)
        epoch_logs.append({
            'epoch': ep,
            'train_loss': train_loss,
            'gauc': va['GAUC'],
            'ndcg5': va['nDCG@5'],
            'primary': va['primary'],
            'time': ep_duration
        })

        if va['primary'] > best_primary + 1e-5:
            best_primary = va['primary']
            best_va_metrics = va
            best_epoch = ep
            best_state = (m.V.copy(), m.W.copy(), np.float32(m.b))
            bad_epochs = 0
        else:
            bad_epochs += 1
            if bad_epochs >= patience:
                print(f"\nEarly stopping triggered after {ep} epochs (no primary improvement for {patience} consecutive epochs).")
                break

    total_time = time.time() - t_start
    print(f"\nTraining completed in {total_time:.2f}s.")
    print(f"Restoring best checkpoint from Epoch {best_epoch} with Primary = {best_primary:.4f}...")
    m.V, m.W, m.b = best_state

    # Final evaluation on restored best model
    final_preds = m.predict(Xva)
    final_metrics = evaluate(uva, yva, final_preds)

    return final_metrics, best_epoch, epoch_logs, total_time

# ---------------- Main Entry Point ----------------
def main():
    parser = argparse.ArgumentParser(description="Run Variant v1: 8-field Video Metadata Extension FM")
    parser.add_argument('--data_dir', default='competition_data/data', help="Path to data directory")
    parser.add_argument('--k', type=int, default=16, help="Embedding dimension")
    parser.add_argument('--lr', type=float, default=0.001, help="Learning rate")
    parser.add_argument('--batch_size', type=int, default=8192, help="Batch size")
    parser.add_argument('--max_epochs', type=int, default=25, help="Maximum epochs")
    parser.add_argument('--patience', type=int, default=4, help="Early stopping patience")
    parser.add_argument('--seed', type=int, default=0, help="Random seed")
    args = parser.parse_args()

    print("=" * 70)
    print("KuaiRand-Pure Research: Round 01 - Variant v1")
    print("Focus: Video Metadata Extension (8 fields: user_id, video_id, author_id, music_id, video_type, upload_type, tab, dur_bucket)")
    print(f"Hyperparameters: k={args.k}, lr={args.lr}, batch_size={args.batch_size}, max_epochs={args.max_epochs}, patience={args.patience}, seed={args.seed}")
    print("=" * 70)

    t0_all = time.time()
    train_raw, valid_raw = load_data(args.data_dir)
    train_data, valid_data, total_dim, field_dims = encode_data(train_raw, valid_raw)

    final_metrics, best_epoch, epoch_logs, train_time = train_and_eval(
        train_data, valid_data, total_dim,
        k=args.k, lr=args.lr, batch_size=args.batch_size,
        max_epochs=args.max_epochs, patience=args.patience, seed=args.seed
    )
    total_elapsed = time.time() - t0_all

    print("\n" + "=" * 70)
    print("FINAL OFFICIAL PUBLIC VALIDATION METRICS (Variant v1 - 8 fields)")
    print("=" * 70)
    print(f"Validation Users : {final_metrics['users']}")
    print(f"Validation Rows  : {final_metrics['rows']}")
    print(f"Best Epoch       : {best_epoch}")
    print(f"Validation GAUC  : {final_metrics['GAUC']:.6f} ({final_metrics['GAUC']:.4f})")
    print(f"Validation nDCG@5: {final_metrics['nDCG@5']:.6f} ({final_metrics['nDCG@5']:.4f})")
    print(f"Validation Primary: {final_metrics['primary']:.6f} ({final_metrics['primary']:.4f})")
    print(f"Training Time    : {train_time:.2f} s")
    print(f"Total Run Time   : {total_elapsed:.2f} s")
    print("=" * 70)

    # Control comparison
    ctrl_gauc, ctrl_ndcg, ctrl_pri = 0.6671, 0.5358, 0.6015
    delta_gauc = final_metrics['GAUC'] - ctrl_gauc
    delta_ndcg = final_metrics['nDCG@5'] - ctrl_ndcg
    delta_pri = final_metrics['primary'] - ctrl_pri

    print("\nDELTA VS CONTROL (Official 5-field FM Baseline):")
    print(f"  GAUC    : {final_metrics['GAUC']:.4f} vs {ctrl_gauc:.4f} (Delta: {delta_gauc:+.4f})")
    print(f"  nDCG@5  : {final_metrics['nDCG@5']:.4f} vs {ctrl_ndcg:.4f} (Delta: {delta_ndcg:+.4f})")
    print(f"  Primary : {final_metrics['primary']:.4f} vs {ctrl_pri:.4f} (Delta: {delta_pri:+.4f})")
    print("=" * 70)

if __name__ == '__main__':
    main()
