"""Round 02 - Variant v3: High Capacity with Strong Regularization (k=64, L2=1e-5)
10 Fields:
- user_id
- video_id
- author_id
- tab
- dur_bucket
- user_active_degree
- follow_user_num_range
- fans_user_num_range
- friend_user_num_range
- register_days_range

Model: Factorization Machine (FM)
Hyperparameters: k=64, lr=0.001, l2=1e-5, batch_size=8192, max_epochs=25, patience=4, seed=0
Data: KuaiRand-Pure standard train (4/08-4/21) + public valid (4/22-4/28)
"""

import csv
import os
import sys
import time
import json
import numpy as np

# Add project root to sys.path to access starter_kit
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from starter_kit.evaluate import evaluate

LABEL = 'long_view'
SPLITS = {
    'train': (20220408, 20220421),
    'valid': (20220422, 20220428)
}

USER_FE = [
    'user_active_degree',
    'follow_user_num_range',
    'fans_user_num_range',
    'friend_user_num_range',
    'register_days_range'
]

FIELDS = [
    'user_id',
    'video_id',
    'author_id',
    'tab',
    'dur_bucket',
    'user_active_degree',
    'follow_user_num_range',
    'fans_user_num_range',
    'friend_user_num_range',
    'register_days_range'
]

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

class FM:
    def __init__(self, dim, k=64, lr=0.001, l2=1e-5, seed=0):
        rng = np.random.default_rng(seed)
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W = np.zeros(dim, dtype=np.float32)
        self.b = np.float32(0.0)
        self.lr, self.l2 = lr, l2
        self.mV = np.zeros_like(self.V)
        self.vV = np.zeros_like(self.V)
        self.mW = np.zeros_like(self.W)
        self.vW = np.zeros_like(self.W)
        self.t = 0

    def logits(self, X):
        E = self.V[X]                                   # (B, F, k)
        S = E.sum(1)                                    # (B, k)
        inter = 0.5 * ((S ** 2).sum(1) - (E ** 2).sum((1, 2)))
        return self.b + self.W[X].sum(1) + inter, E, S

    def step(self, X, y):
        B = len(y)
        z, E, S = self.logits(X)
        g = ((sigmoid(z) - y) / B).astype(np.float32)    # (B,)
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
        loss = -np.mean(y * np.log(sigmoid(z) + 1e-9) + (1 - y) * np.log(1 - sigmoid(z) + 1e-9))
        return float(loss)

    def predict(self, X, bs=200_000):
        if len(X) == 0:
            return np.empty(0, dtype=np.float32)
        return np.concatenate([self.logits(X[i:i + bs])[0] for i in range(0, len(X), bs)])

def load_data(data_dir):
    print(f"Loading data from {data_dir} ...")
    t0 = time.time()
    
    # 1. Load video author mapping
    vid2author = {}
    with open(os.path.join(data_dir, 'video_features_basic_pure.csv')) as fh:
        for r in csv.DictReader(fh):
            vid2author[r['video_id']] = r['author_id']
            
    # 2. Load user demographic features
    u_ext = {}
    with open(os.path.join(data_dir, 'user_features_pure.csv')) as fh:
        for r in csv.DictReader(fh):
            u_ext[r['user_id']] = [r[k] for k in USER_FE]
            
    # 3. Load interaction logs
    rows = []
    log_files = [
        'log_standard_4_08_to_4_21_pure.csv',
        'log_public_4_22_to_4_28_pure.csv'
    ]
    for f in log_files:
        f_path = os.path.join(data_dir, f)
        if not os.path.exists(f_path):
            raise FileNotFoundError(f"Required log file not found: {f_path}")
        with open(f_path) as fh:
            for r in csv.DictReader(fh):
                uid = r['user_id']
                vid = r['video_id']
                author = vid2author.get(vid, 'UNK')
                tab = r['tab']
                dur = float(r['duration_ms'])
                label = 1 if r[LABEL] != '0' else 0
                date = int(r['date'])
                user_feats = u_ext.get(uid, ['UNK'] * len(USER_FE))
                rows.append((date, uid, vid, author, tab, dur, label, *user_feats))

    splits = {}
    for name, (lo, hi) in SPLITS.items():
        splits[name] = [x for x in rows if lo <= x[0] <= hi]
        
    print(f"Loaded splits: { {k: len(v) for k, v in splits.items()} } in {time.time() - t0:.2f}s")
    return splits

def encode_features(splits):
    print("Encoding features across 10 fields...")
    t0 = time.time()
    tr = splits['train']
    # Calculate duration bucket edges on train split only
    edges = np.quantile(np.asarray([x[5] for x in tr]), np.linspace(0, 1, 11)[1:-1])

    def raw_features(x):
        # x is (date, uid, vid, author, tab, dur, label, user_active_degree, follow, fans, friend, reg_days)
        dur_bucket = str(int(np.searchsorted(edges, x[5])))
        return [
            x[1],                # user_id
            x[2],                # video_id
            x[3],                # author_id
            x[4],                # tab
            dur_bucket,          # dur_bucket
            x[7],                # user_active_degree
            x[8],                # follow_user_num_range
            x[9],                # fans_user_num_range
            x[10],               # friend_user_num_range
            x[11],               # register_days_range
        ]

    vocabs = [dict() for _ in FIELDS]
    for x in tr:
        feats = raw_features(x)
        for i, v in enumerate(feats):
            if v not in vocabs[i]:
                vocabs[i][v] = len(vocabs[i])

    unk = [len(v) for v in vocabs]
    field_dims = [len(v) + 1 for v in vocabs]
    offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int32)
    total_dim = int(sum(field_dims))

    enc = {}
    for name, rws in splits.items():
        X = np.empty((len(rws), len(FIELDS)), dtype=np.int32)
        y = np.empty(len(rws), dtype=np.float32)
        users = []
        for n, x in enumerate(rws):
            feats = raw_features(x)
            for i, v in enumerate(feats):
                X[n, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            y[n] = x[6]
            users.append(x[1])
        enc[name] = (X, y, users)

    print(f"Feature encoding complete. Total dimension: {total_dim} across {len(FIELDS)} fields in {time.time() - t0:.2f}s")
    for i, f_name in enumerate(FIELDS):
        print(f"  Field {i:2d} ({f_name:22s}): {field_dims[i]} distinct IDs (including UNK)")
    return enc, total_dim

def default_json(obj):
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)

def run_experiment(k=64, lr=0.001, l2=1e-5, epochs=25, bs=8192, patience=4, seed=0):
    data_dir = os.path.join(PROJECT_ROOT, 'competition_data', 'data')
    splits = load_data(data_dir)
    enc, dim = encode_features(splits)

    Xtr, ytr, _ = enc['train']
    Xva, yva, uva = enc['valid']

    print(f"\nInitializing FM model (dim={dim}, k={k}, lr={lr}, l2={l2}, seed={seed})...")
    m = FM(dim, k=k, lr=lr, l2=l2, seed=seed)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_va = None
    best_epoch = 0
    bad_epochs = 0
    best_state = None

    history = []
    print("\nStarting FM training...")
    start_time = time.time()
    for ep in range(1, epochs + 1):
        ep_t0 = time.time()
        idx = rng.permutation(len(ytr))
        losses = []
        for i in range(0, len(idx), bs):
            b_idx = idx[i:i + bs]
            losses.append(m.step(Xtr[b_idx], ytr[b_idx]))

        mean_loss = float(np.mean(losses))
        va_preds = m.predict(Xva)
        va = evaluate(uva, yva, va_preds)
        ep_dur = time.time() - ep_t0

        log_entry = {
            'epoch': ep,
            'train_loss': mean_loss,
            'valid_gauc': float(va['GAUC']),
            'valid_ndcg5': float(va['nDCG@5']),
            'valid_primary': float(va['primary']),
            'epoch_time_sec': ep_dur
        }
        history.append(log_entry)

        print(f"Epoch {ep:2d}/{epochs:2d} | Train Loss: {mean_loss:.4f} | "
              f"Valid GAUC: {va['GAUC']:.4f} | nDCG@5: {va['nDCG@5']:.4f} | "
              f"Primary: {va['primary']:.4f} | Time: {ep_dur:.2f}s")

        if va['primary'] > best_primary + 1e-5:
            best_primary = va['primary']
            best_va = {k_: float(v_) if isinstance(v_, (int, float, np.floating, np.integer)) else v_ for k_, v_ in va.items()}
            best_epoch = ep
            bad_epochs = 0
            best_state = (m.V.copy(), m.W.copy(), np.float32(m.b))
        else:
            bad_epochs += 1
            if bad_epochs >= patience:
                print(f"Early stopping triggered at epoch {ep} (best epoch: {best_epoch})")
                break

    total_time = time.time() - start_time
    print(f"\nTraining completed in {total_time:.2f}s.")
    print(f"Best Validation Epoch: {best_epoch}")
    print(f"Best Validation GAUC:    {best_va['GAUC']:.4f}")
    print(f"Best Validation nDCG@5:  {best_va['nDCG@5']:.4f}")
    print(f"Best Validation Primary: {best_va['primary']:.4f}")

    results = {
        'variant': 'v3',
        'hypothesis': 'High Capacity with Strong Regularization (k=64, L2=1e-5)',
        'fields': FIELDS,
        'hyperparameters': {
            'k': k,
            'lr': lr,
            'l2': l2,
            'max_epochs': epochs,
            'batch_size': bs,
            'patience': patience,
            'seed': seed
        },
        'best_epoch': best_epoch,
        'best_metrics': best_va,
        'history': history,
        'total_elapsed_time_sec': total_time
    }

    out_file = os.path.join(os.path.dirname(__file__), 'results.json')
    with open(out_file, 'w') as fh:
        json.dump(results, fh, indent=2, default=default_json)
    print(f"Saved results to {out_file}")

    return results

if __name__ == '__main__':
    run_experiment()
