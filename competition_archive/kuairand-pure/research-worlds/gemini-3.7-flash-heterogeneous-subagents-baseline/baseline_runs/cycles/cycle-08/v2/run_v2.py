"""Round 08 - Variant v2: Dynamic User Cumulative Interaction Activity Bins (11 Fields in DCN-FM)

Candidate Architecture:
11 Fields:
1.  user_id
2.  video_id
3.  author_id
4.  tab
5.  dur_bucket (20 uniform bins in log(1 + duration_ms) space fitted on train split)
6.  user_cum_count_bin (20 quantile bins of cumulative previous user interactions up to each row, fitted on train split)
7.  user_active_degree
8.  follow_user_num_range
9.  fans_user_num_range
10. friend_user_num_range
11. register_days_range

Model: Explicit Cross Layer + Factorization Machine (DCN-FM)
Cross layer formulation: x_1 = x_0 * (x_0 @ W_c + b_c) + x_0, where x_0 = E_concat in R^(11 * 16) = R^176
Logits: z = b + linear(X) + FM_interaction(E) + x_1 @ w_p
Hyperparameters: k=16, lr=0.001, l2=1e-6, batch_size=8192, max_epochs=20, patience=4, seed=0
Data: KuaiRand-Pure standard train (4/08-4/21) + public valid (4/22-4/28)
"""

import csv
import os
import sys
import time
import json
from collections import defaultdict
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
    'user_cum_count_bin',
    'user_active_degree',
    'follow_user_num_range',
    'fans_user_num_range',
    'friend_user_num_range',
    'register_days_range'
]

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

class DCN_FM:
    def __init__(self, dim, num_fields=11, k=16, lr=0.001, l2=1e-6, seed=0):
        rng = np.random.default_rng(seed)
        self.dim = dim
        self.num_fields = num_fields
        self.k = k
        self.D = num_fields * k  # 11 * 16 = 176
        self.lr = lr
        self.l2 = l2

        # Model Parameters
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W = np.zeros(dim, dtype=np.float32)
        self.b = np.float32(0.0)
        
        # DCN Cross Layer Parameters
        self.W_c = rng.normal(0, 0.01, (self.D, self.D)).astype(np.float32)
        self.b_c = np.zeros(self.D, dtype=np.float32)
        self.w_p = rng.normal(0, 0.01, self.D).astype(np.float32)

        # Adam Moments
        self.mV = np.zeros_like(self.V)
        self.vV = np.zeros_like(self.V)
        self.mW = np.zeros_like(self.W)
        self.vW = np.zeros_like(self.W)
        self.mW_c = np.zeros_like(self.W_c)
        self.vW_c = np.zeros_like(self.W_c)
        self.mb_c = np.zeros_like(self.b_c)
        self.vb_c = np.zeros_like(self.b_c)
        self.mw_p = np.zeros_like(self.w_p)
        self.vw_p = np.zeros_like(self.w_p)
        self.t = 0

    def logits(self, X):
        B = len(X)
        E = self.V[X]                                        # (B, F, k)
        S = E.sum(1)                                         # (B, k)
        inter_fm = 0.5 * ((S ** 2).sum(1) - (E ** 2).sum((1, 2))) # (B,)
        lin = self.W[X].sum(1)                               # (B,)

        x0 = E.reshape(B, self.D)                            # (B, D)
        u = x0 @ self.W_c + self.b_c                         # (B, D)
        x1 = x0 * u + x0                                     # (B, D)
        z_cross = x1 @ self.w_p                              # (B,)

        z = self.b + lin + inter_fm + z_cross
        return z, E, S, x0, u, x1

    def step(self, X, y):
        B = len(y)
        z, E, S, x0, u, x1 = self.logits(X)
        p = sigmoid(z)
        g = ((p - y) / B).astype(np.float32)                 # (B,)

        # Compute Gradients
        # 1. Bias
        gb = np.float32(g.sum())

        # 2. Linear weights
        gW = np.zeros_like(self.W)
        np.add.at(gW, X, g[:, None])
        gW += self.l2 * self.W

        # 3. Cross layer output projection w_p
        gw_p = (x1.T @ g).astype(np.float32) + self.l2 * self.w_p

        # 4. Cross layer intermediate backprop
        gx1 = g[:, None] * self.w_p                          # (B, D)
        gu = gx1 * x0                                        # (B, D)
        gb_c = gu.sum(0).astype(np.float32) + self.l2 * self.b_c
        gW_c = (x0.T @ gu).astype(np.float32) + self.l2 * self.W_c

        # 5. Backprop into x0 (concatenated embeddings)
        gx0 = gx1 * (u + 1.0) + gu @ self.W_c.T              # (B, D)
        gE_cross = gx0.reshape(B, self.num_fields, self.k)   # (B, F, k)

        # 6. FM 2nd-order interaction gradient
        gE_fm = g[:, None, None] * (S[:, None, :] - E)       # (B, F, k)

        # 7. Total embedding gradient
        gE = (gE_fm + gE_cross).astype(np.float32)
        gV = np.zeros_like(self.V)
        np.add.at(gV, X, gE)
        gV += self.l2 * self.V

        # Adam updates
        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        
        params_grads_moments = [
            (self.V, gV, self.mV, self.vV),
            (self.W, gW, self.mW, self.vW),
            (self.W_c, gW_c, self.mW_c, self.vW_c),
            (self.b_c, gb_c, self.mb_c, self.vb_c),
            (self.w_p, gw_p, self.mw_p, self.vw_p)
        ]

        for P, G, M, Vv in params_grads_moments:
            M *= b1
            M += (1 - b1) * G
            Vv *= b2
            Vv += (1 - b2) * (G * G)
            P -= self.lr * (M / (1 - b1 ** self.t)) / (np.sqrt(Vv / (1 - b2 ** self.t)) + eps)

        self.b -= self.lr * gb

        loss = -np.mean(y * np.log(p + 1e-9) + (1 - y) * np.log(1 - p + 1e-9))
        return float(loss)

    def predict(self, X, bs=100_000):
        if len(X) == 0:
            return np.empty(0, dtype=np.float32)
        preds = []
        for i in range(0, len(X), bs):
            z_batch, _, _, _, _, _ = self.logits(X[i:i + bs])
            preds.append(z_batch)
        return np.concatenate(preds)

def load_data_and_compute_cum_counts(data_dir):
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
    raw_records = []
    log_files = [
        ('train', 'log_standard_4_08_to_4_21_pure.csv'),
        ('valid', 'log_public_4_22_to_4_28_pure.csv')
    ]
    
    for split_tag, f in log_files:
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
                time_ms = int(r['time_ms'])
                user_feats = u_ext.get(uid, ['UNK'] * len(USER_FE))
                
                raw_records.append({
                    'orig_idx': len(raw_records),
                    'split_tag': split_tag,
                    'date': date,
                    'time_ms': time_ms,
                    'user_id': uid,
                    'video_id': vid,
                    'author_id': author,
                    'tab': tab,
                    'duration_ms': dur,
                    'label': label,
                    'user_feats': user_feats
                })

    print(f"Loaded {len(raw_records)} raw interaction rows in {time.time() - t0:.2f}s")
    
    # 4. Chronological sort across full dataset to compute exact dynamic user cumulative interaction counts
    t_sort = time.time()
    raw_records_sorted = sorted(raw_records, key=lambda x: (x['time_ms'], x['orig_idx']))
    
    user_counts = defaultdict(int)
    for r in raw_records_sorted:
        r['user_cum_count'] = user_counts[r['user_id']]
        user_counts[r['user_id']] += 1
        
    print(f"Computed dynamic user cumulative interaction counts across {len(user_counts)} unique users in {time.time() - t_sort:.2f}s")
    
    # Group into splits preserving original chronological partition
    splits = {'train': [], 'valid': []}
    for r in raw_records:
        date = r['date']
        uid = r['user_id']
        vid = r['video_id']
        author = r['author_id']
        tab = r['tab']
        dur = r['duration_ms']
        cum_cnt = r['user_cum_count']
        label = r['label']
        user_feats = r['user_feats']
        
        row_tuple = (date, uid, vid, author, tab, dur, cum_cnt, label, *user_feats)
        
        if SPLITS['train'][0] <= date <= SPLITS['train'][1]:
            splits['train'].append(row_tuple)
        elif SPLITS['valid'][0] <= date <= SPLITS['valid'][1]:
            splits['valid'].append(row_tuple)
            
    print(f"Partitioned splits: { {k: len(v) for k, v in splits.items()} }")
    return splits

def encode_features(splits):
    print("Encoding features across 11 fields with 20 Log-Duration Bins and 20 User Cumulative Interaction Bins...")
    t0 = time.time()
    tr = splits['train']
    
    # Calculate log-transformed duration bin edges on train split only
    # Transform duration using log(1 + duration_ms) and create 20 uniform bins across the range observed on the training partition.
    train_log_durs = np.log1p(np.asarray([x[5] for x in tr], dtype=np.float64))
    min_log = float(np.min(train_log_durs))
    max_log = float(np.max(train_log_durs))
    dur_edges = np.linspace(min_log, max_log, 21)[1:-1]
    print(f"Train log(1 + duration_ms) range: [{min_log:.4f}, {max_log:.4f}] with {len(dur_edges)} cutoffs")
    print("  Log Duration Cutoffs:", np.round(dur_edges, 4).tolist())

    # Calculate 20 quantile bin edges for cumulative user interaction counts fitted on train split
    train_cum_counts = np.asarray([x[6] for x in tr], dtype=np.float64)
    min_cum = float(np.min(train_cum_counts))
    max_cum = float(np.max(train_cum_counts))
    mean_cum = float(np.mean(train_cum_counts))
    cum_edges = np.percentile(train_cum_counts, np.linspace(0, 100, 21)[1:-1])
    print(f"Train cumulative user interaction count stats: min={min_cum:.0f}, max={max_cum:.0f}, mean={mean_cum:.2f}")
    print(f"Created {len(cum_edges)} quantile cutoffs for 20 user activity bins:")
    print("  User Cumulative Count Cutoffs:", np.round(cum_edges, 2).tolist())

    def raw_features(x):
        # x is (date, uid, vid, author, tab, dur, cum_cnt, label, user_active_degree, follow, fans, friend, reg_days)
        log_d = np.log1p(float(x[5]))
        dur_bucket = str(int(np.searchsorted(dur_edges, log_d)))
        
        cum_c = float(x[6])
        cum_bucket = str(int(np.searchsorted(cum_edges, cum_c)))
        
        return [
            x[1],                # 0. user_id
            x[2],                # 1. video_id
            x[3],                # 2. author_id
            x[4],                # 3. tab
            dur_bucket,          # 4. dur_bucket (20 log bins)
            cum_bucket,          # 5. user_cum_count_bin (20 quantile bins)
            x[8],                # 6. user_active_degree
            x[9],                # 7. follow_user_num_range
            x[10],               # 8. fans_user_num_range
            x[11],               # 9. friend_user_num_range
            x[12],               # 10. register_days_range
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
            y[n] = x[7]
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

def run_experiment(k=16, lr=0.001, l2=1e-6, epochs=20, bs=8192, patience=4, seed=0):
    data_dir = os.path.join(PROJECT_ROOT, 'competition_data', 'data')
    splits = load_data_and_compute_cum_counts(data_dir)
    enc, dim = encode_features(splits)

    Xtr, ytr, _ = enc['train']
    Xva, yva, uva = enc['valid']

    num_fields = len(FIELDS)
    D = num_fields * k  # 11 * 16 = 176
    print(f"\nInitializing DCN_FM model (dim={dim}, fields={num_fields}, k={k}, D={D}, lr={lr}, l2={l2}, seed={seed})...")
    m = DCN_FM(dim, num_fields=num_fields, k=k, lr=lr, l2=l2, seed=seed)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_va = None
    best_epoch = 0
    bad_epochs = 0

    history = []
    print(f"\nStarting DCN_FM training across {num_fields} fields (D={D})...")
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
        'variant': 'v2',
        'hypothesis': 'Dynamic User Cumulative Interaction Activity Bins (11 fields in Log-Duration DCN-FM, D=176)',
        'fields': FIELDS,
        'hyperparameters': {
            'num_fields': num_fields,
            'k': k,
            'D': D,
            'lr': lr,
            'l2': l2,
            'max_epochs': epochs,
            'batch_size': bs,
            'patience': patience,
            'seed': seed,
            'num_log_dur_bins': 20,
            'num_cum_count_bins': 20
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
