"""
Variant v3: Full CWM-13 Joint Feature Representation (13 fields)
Model: Factorization Machine (FM)
Embedding dim k: 16
Learning rate: 0.001
Batch size: 8192
Max epochs: 25
Patience: 4
L2 reg: 1e-6

Strict Data Boundary:
- Train: competition_data/data/log_standard_4_08_to_4_21_pure.csv (2022-04-08 to 2022-04-21)
- Valid: competition_data/data/log_public_4_22_to_4_28_pure.csv (2022-04-22 to 2022-04-28)
- Video Features: competition_data/data/video_features_basic_pure.csv
- User Features: competition_data/data/user_features_pure.csv
"""

import csv
import os
import sys
import time
import math
import collections
import numpy as np

# Set fixed random seeds for reproducibility
SEED = 0

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
DATA_DIR = os.path.join(BASE_DIR, "competition_data/data")

# Control baseline metrics for comparison
CONTROL_METRICS = {
    'GAUC': 0.6671,
    'nDCG@5': 0.5358,
    'primary': 0.6015
}

# 13 Fields definition
USER_FIELDS = [
    'user_active_degree',
    'follow_user_num_range',
    'fans_user_num_range',
    'friend_user_num_range',
    'register_days_range'
]

VIDEO_FIELDS = [
    'author_id',
    'music_id',
    'video_type',
    'upload_type'
]

ALL_FIELDS = [
    'user_id',
    'video_id',
    'tab',
    'dur_bucket',
    'author_id',
    'music_id',
    'video_type',
    'upload_type',
    'user_active_degree',
    'follow_user_num_range',
    'fans_user_num_range',
    'friend_user_num_range',
    'register_days_range'
]

# ----------------- Evaluation Metrics (Starter Kit Official Semantics) -----------------
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
    """labels must be sorted in descending order of predicted score."""
    disc = [math.log2(i + 2) for i in range(k)]
    dcg = sum(((2 ** t) - 1) / disc[i] for i, t in enumerate(labels[:k]))
    ideal = sorted(labels, reverse=True)[:k]
    idcg = sum(((2 ** t) - 1) / disc[i] for i, t in enumerate(ideal))
    return 0.0 if idcg == 0 else dcg / idcg

def evaluate(user_ids, labels, scores, k=5):
    """Computes GAUC, nDCG@5, and primary = mean(GAUC, nDCG@5)."""
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

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

# ----------------- Factorization Machine Model -----------------
class FactorizationMachine:
    def __init__(self, dim, k=16, lr=0.001, l2=1e-6, seed=SEED):
        rng = np.random.default_rng(seed)
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W = np.zeros(dim, dtype=np.float32)
        self.b = np.float32(0.0)
        self.lr = lr
        self.l2 = l2
        self.mV = np.zeros_like(self.V)
        self.vV = np.zeros_like(self.V)
        self.mW = np.zeros_like(self.W)
        self.vW = np.zeros_like(self.W)
        self.t = 0

    def logits(self, X):
        # X: (B, F)
        E = self.V[X]                                    # (B, F, k)
        S = E.sum(1)                                     # (B, k)
        inter = 0.5 * ((S ** 2).sum(1) - (E ** 2).sum((1, 2)))
        return self.b + self.W[X].sum(1) + inter, E, S

    def step(self, X, y):
        B = len(y)
        z, E, S = self.logits(X)
        p = sigmoid(z)
        g = ((p - y) / B).astype(np.float32)            # (B,)
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
        loss = float(-np.mean(y * np.log(p + 1e-9) + (1 - y) * np.log(1 - p + 1e-9)))
        return loss

    def predict(self, X, bs=200_000):
        if len(X) == 0:
            return np.empty(0, dtype=np.float32)
        preds = []
        for i in range(0, len(X), bs):
            z, _, _ = self.logits(X[i:i + bs])
            preds.append(z)
        return np.concatenate(preds)

# ----------------- Data Loading & Feature Engineering -----------------
def load_and_preprocess():
    print(f"Loading data from {DATA_DIR} ...")
    t0 = time.time()
    
    # 1. Load User features
    user_feat = {}
    with open(os.path.join(DATA_DIR, 'user_features_pure.csv'), mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            user_feat[r['user_id']] = [r.get(k, 'UNK') for k in USER_FIELDS]
    print(f"Loaded user features for {len(user_feat)} users.")

    # 2. Load Video features
    video_feat = {}
    with open(os.path.join(DATA_DIR, 'video_features_basic_pure.csv'), mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            video_feat[r['video_id']] = [r.get(k, 'UNK') for k in VIDEO_FIELDS]
    print(f"Loaded video features for {len(video_feat)} videos.")

    # 3. Load interaction logs
    # Train: 20220408 to 20220421
    train_rows = []
    with open(os.path.join(DATA_DIR, 'log_standard_4_08_to_4_21_pure.csv'), mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            train_rows.append({
                'date': int(r['date']),
                'user_id': r['user_id'],
                'video_id': r['video_id'],
                'tab': r['tab'],
                'duration_ms': float(r['duration_ms']),
                'label': 1 if r['long_view'] != '0' else 0
            })
    print(f"Loaded {len(train_rows)} train rows (2022-04-08 to 2022-04-21).")

    # Valid: 20220422 to 20220428
    valid_rows = []
    with open(os.path.join(DATA_DIR, 'log_public_4_22_to_4_28_pure.csv'), mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            valid_rows.append({
                'date': int(r['date']),
                'user_id': r['user_id'],
                'video_id': r['video_id'],
                'tab': r['tab'],
                'duration_ms': float(r['duration_ms']),
                'label': 1 if r['long_view'] != '0' else 0
            })
    print(f"Loaded {len(valid_rows)} valid rows (2022-04-22 to 2022-04-28).")

    # 4. Duration quantile bucket edges computed strictly from train split
    train_durations = [r['duration_ms'] for r in train_rows]
    dur_edges = np.quantile(train_durations, np.linspace(0, 1, 11)[1:-1])
    print(f"Duration quantile edges (10 buckets) computed from train: {dur_edges}")

    UNK_USER = ['UNK'] * len(USER_FIELDS)
    UNK_VIDEO = ['UNK'] * len(VIDEO_FIELDS)

    def extract_raw_features(row):
        uid = row['user_id']
        vid = row['video_id']
        tab = row['tab']
        dur_bucket = str(int(np.searchsorted(dur_edges, row['duration_ms'])))
        vf = video_feat.get(vid, UNK_VIDEO)
        uf = user_feat.get(uid, UNK_USER)
        # Order: user_id, video_id, tab, dur_bucket, author_id, music_id, video_type, upload_type,
        #        user_active_degree, follow_user_num_range, fans_user_num_range, friend_user_num_range, register_days_range
        return [uid, vid, tab, dur_bucket] + vf + uf

    # 5. Build vocabularies strictly from train split
    num_fields = len(ALL_FIELDS)
    vocabs = [dict() for _ in range(num_fields)]
    for r in train_rows:
        raw_feats = extract_raw_features(r)
        for i, val in enumerate(raw_feats):
            if val not in vocabs[i]:
                vocabs[i][val] = len(vocabs[i])

    unk_indices = [len(v) for v in vocabs]
    field_dims = [len(v) + 1 for v in vocabs]
    offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int32)
    total_dim = int(sum(field_dims))

    print(f"Field dimensions: {dict(zip(ALL_FIELDS, field_dims))}")
    print(f"Total one-hot/embedding dimension: {total_dim}")

    # 6. Encode train and valid matrices
    def encode_split(rows):
        X = np.empty((len(rows), num_fields), dtype=np.int32)
        y = np.empty(len(rows), dtype=np.float32)
        users = []
        for j, r in enumerate(rows):
            raw_feats = extract_raw_features(r)
            for i, val in enumerate(raw_feats):
                X[j, i] = vocabs[i].get(val, unk_indices[i]) + offsets[i]
            y[j] = r['label']
            users.append(r['user_id'])
        return X, y, users

    Xtr, ytr, utr = encode_split(train_rows)
    Xva, yva, uva = encode_split(valid_rows)

    print(f"Encoded train: X shape {Xtr.shape}, pos_rate {np.mean(ytr):.4f}")
    print(f"Encoded valid: X shape {Xva.shape}, pos_rate {np.mean(yva):.4f}")
    print(f"Data preparation complete in {time.time() - t0:.2f}s")

    return (Xtr, ytr, utr), (Xva, yva, uva), total_dim

# ----------------- Training Pipeline -----------------
def run_experiment(k=16, lr=0.001, l2=1e-6, batch_size=8192, max_epochs=25, patience=4, seed=SEED):
    print("=" * 70)
    print(f"Variant v3 Experiment: CWM-13 Joint Features FM Model")
    print(f"Hyperparameters: k={k}, lr={lr}, l2={l2}, batch_size={batch_size}, max_epochs={max_epochs}, patience={patience}, seed={seed}")
    print("=" * 70)

    start_time = time.time()
    (Xtr, ytr, utr), (Xva, yva, uva), total_dim = load_and_preprocess()

    model = FactorizationMachine(total_dim, k=k, lr=lr, l2=l2, seed=seed)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_va_metrics = None
    best_state = None
    bad_epochs = 0

    print("\n--- Starting Training ---")
    for epoch in range(1, max_epochs + 1):
        ep_t0 = time.time()
        idx = rng.permutation(len(ytr))
        batch_losses = []
        for i in range(0, len(idx), batch_size):
            b_idx = idx[i:i + batch_size]
            loss = model.step(Xtr[b_idx], ytr[b_idx])
            batch_losses.append(loss)
        
        train_loss = np.mean(batch_losses)
        val_preds = model.predict(Xva)
        va_metrics = evaluate(uva, yva, val_preds)
        ep_duration = time.time() - ep_t0

        print(f"Epoch {epoch:2d}/{max_epochs:2d} | Train Loss: {train_loss:.4f} | "
              f"Valid GAUC: {va_metrics['GAUC']:.4f} | nDCG@5: {va_metrics['nDCG@5']:.4f} | "
              f"Primary: {va_metrics['primary']:.4f} | Time: {ep_duration:.2f}s")

        if va_metrics['primary'] > best_primary + 1e-5:
            best_primary = va_metrics['primary']
            best_va_metrics = va_metrics
            bad_epochs = 0
            best_state = (model.V.copy(), model.W.copy(), np.float32(model.b))
            print(f"  --> New best primary score: {best_primary:.4f} (Saved checkpoint)")
        else:
            bad_epochs += 1
            print(f"  --> No improvement for {bad_epochs} epoch(s) (patience: {patience})")
            if bad_epochs >= patience:
                print(f"\n[Early Stopping Triggered] at epoch {epoch}. Stopping training.")
                break

    # Restore best checkpoint
    model.V, model.W, model.b = best_state
    final_val_preds = model.predict(Xva)
    final_metrics = evaluate(uva, yva, final_val_preds)
    total_elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("FINAL VALIDATION RESULTS (Best Checkpoint Restored)")
    print("=" * 70)
    print(f"Validation GAUC:    {final_metrics['GAUC']:.4f} (Control: {CONTROL_METRICS['GAUC']:.4f}, Delta: {final_metrics['GAUC'] - CONTROL_METRICS['GAUC']:+.4f})")
    print(f"Validation nDCG@5:  {final_metrics['nDCG@5']:.4f} (Control: {CONTROL_METRICS['nDCG@5']:.4f}, Delta: {final_metrics['nDCG@5'] - CONTROL_METRICS['nDCG@5']:+.4f})")
    print(f"Validation Primary: {final_metrics['primary']:.4f} (Control: {CONTROL_METRICS['primary']:.4f}, Delta: {final_metrics['primary'] - CONTROL_METRICS['primary']:+.4f})")
    print(f"Total Execution Time: {total_elapsed:.2f}s")
    print("=" * 70)

    return {
        'metrics': final_metrics,
        'deltas': {
            'GAUC': final_metrics['GAUC'] - CONTROL_METRICS['GAUC'],
            'nDCG@5': final_metrics['nDCG@5'] - CONTROL_METRICS['nDCG@5'],
            'primary': final_metrics['primary'] - CONTROL_METRICS['primary']
        },
        'elapsed_seconds': total_elapsed,
        'epochs_trained': epoch,
        'best_primary': best_primary
    }

if __name__ == '__main__':
    run_experiment()
