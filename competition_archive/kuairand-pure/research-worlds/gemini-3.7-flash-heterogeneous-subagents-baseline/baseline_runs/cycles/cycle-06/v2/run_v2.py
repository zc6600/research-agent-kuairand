"""Round 06 - Variant v2: Multi-Task Joint Optimization with Like Auxiliary (L = L_long_view + 0.3 * L_like)
Shared 10-field embedding layer + explicit cross layer with dedicated task heads.

10 Fields:
- user_id
- video_id
- author_id
- tab
- dur_bucket (20 uniform bins in log(1 + duration_ms) space fitted on train split)
- user_active_degree
- follow_user_num_range
- fans_user_num_range
- friend_user_num_range
- register_days_range

Model: Explicit Cross Layer + Factorization Machine (DCN-FM) with Multi-Task Heads
Shared Representations:
- Embeddings: V in R^{dim x k}, k=16, D=160
- Cross layer: W_c in R^{D x D}, b_c in R^D, x_1 = x_0 * (x_0 @ W_c + b_c) + x_0
- FM 2nd-order interaction: inter_fm = 0.5 * ((sum E)^2 - sum(E^2))

Dedicated Task Heads:
- Task 1 (long_view): W_long in R^{dim}, b_long in R, w_p_long in R^D
  z_long = b_long + W_long[X].sum() + inter_fm + x_1 @ w_p_long
- Task 2 (is_like): W_like in R^{dim}, b_like in R, w_p_like in R^D
  z_like = b_like + W_like[X].sum() + inter_fm + x_1 @ w_p_like

Objective:
L = L_{long_view} + 0.3 * L_{like}

Hyperparameters: k=16, lr=0.001, l2=1e-6, batch_size=8192, max_epochs=20, patience=4, seed=0
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

class MultiTask_DCN_FM:
    def __init__(self, dim, num_fields=10, k=16, alpha=0.3, lr=0.001, l2=1e-6, seed=0):
        rng = np.random.default_rng(seed)
        self.dim = dim
        self.num_fields = num_fields
        self.k = k
        self.D = num_fields * k  # 160
        self.alpha = float(alpha)
        self.lr = lr
        self.l2 = l2

        # Shared Model Parameters
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W_c = rng.normal(0, 0.01, (self.D, self.D)).astype(np.float32)
        self.b_c = np.zeros(self.D, dtype=np.float32)

        # Dedicated Head 1: long_view (Primary)
        self.W_long = np.zeros(dim, dtype=np.float32)
        self.b_long = np.float32(0.0)
        self.w_p_long = rng.normal(0, 0.01, self.D).astype(np.float32)

        # Dedicated Head 2: is_like (Auxiliary)
        self.W_like = np.zeros(dim, dtype=np.float32)
        self.b_like = np.float32(0.0)
        self.w_p_like = rng.normal(0, 0.01, self.D).astype(np.float32)

        # Adam Moments
        self.mV = np.zeros_like(self.V)
        self.vV = np.zeros_like(self.V)
        self.mW_c = np.zeros_like(self.W_c)
        self.vW_c = np.zeros_like(self.W_c)
        self.mb_c = np.zeros_like(self.b_c)
        self.vb_c = np.zeros_like(self.b_c)

        self.mW_long = np.zeros_like(self.W_long)
        self.vW_long = np.zeros_like(self.W_long)
        self.mw_p_long = np.zeros_like(self.w_p_long)
        self.vw_p_long = np.zeros_like(self.w_p_long)

        self.mW_like = np.zeros_like(self.W_like)
        self.vW_like = np.zeros_like(self.W_like)
        self.mw_p_like = np.zeros_like(self.w_p_like)
        self.vw_p_like = np.zeros_like(self.w_p_like)

        self.t = 0

    def logits(self, X):
        B = len(X)
        E = self.V[X]                                              # (B, F, k)
        S = E.sum(1)                                               # (B, k)
        inter_fm = 0.5 * ((S ** 2).sum(1) - (E ** 2).sum((1, 2))) # (B,)
        lin_long = self.W_long[X].sum(1)                           # (B,)
        lin_like = self.W_like[X].sum(1)                           # (B,)

        x0 = E.reshape(B, self.D)                                  # (B, D)
        u = x0 @ self.W_c + self.b_c                               # (B, D)
        x1 = x0 * u + x0                                           # (B, D)

        z_cross_long = x1 @ self.w_p_long                          # (B,)
        z_cross_like = x1 @ self.w_p_like                          # (B,)

        z_long = self.b_long + lin_long + inter_fm + z_cross_long
        z_like = self.b_like + lin_like + inter_fm + z_cross_like
        return z_long, z_like, E, S, x0, u, x1

    def step(self, X, y_long, y_like):
        B = len(y_long)
        z_long, z_like, E, S, x0, u, x1 = self.logits(X)
        p_long = sigmoid(z_long)
        p_like = sigmoid(z_like)

        # Loss derivatives w.r.t logits
        g_long = ((p_long - y_long) / B).astype(np.float32)                 # (B,)
        g_like = (self.alpha * (p_like - y_like) / B).astype(np.float32)     # (B,)

        # Compute Head 1 (long_view) Gradients
        gb_long = np.float32(g_long.sum())
        gW_long = np.zeros_like(self.W_long)
        np.add.at(gW_long, X, g_long[:, None])
        gW_long += self.l2 * self.W_long
        gw_p_long = (x1.T @ g_long).astype(np.float32) + self.l2 * self.w_p_long

        # Compute Head 2 (is_like) Gradients
        gb_like = np.float32(g_like.sum())
        gW_like = np.zeros_like(self.W_like)
        np.add.at(gW_like, X, g_like[:, None])
        gW_like += self.l2 * self.W_like
        gw_p_like = (x1.T @ g_like).astype(np.float32) + self.l2 * self.w_p_like

        # Combined Shared Cross Layer Intermediate Backprop
        gx1 = g_long[:, None] * self.w_p_long + g_like[:, None] * self.w_p_like  # (B, D)
        gu = gx1 * x0                                                             # (B, D)
        gb_c = gu.sum(0).astype(np.float32) + self.l2 * self.b_c
        gW_c = (x0.T @ gu).astype(np.float32) + self.l2 * self.W_c

        # Backprop into x0 (concatenated embeddings)
        gx0 = gx1 * (u + 1.0) + gu @ self.W_c.T                                   # (B, D)
        gE_cross = gx0.reshape(B, self.num_fields, self.k)                        # (B, F, k)

        # Shared FM 2nd-order interaction gradient
        g_fm_scalar = g_long + g_like                                             # (B,)
        gE_fm = g_fm_scalar[:, None, None] * (S[:, None, :] - E)                 # (B, F, k)

        # Total Shared Embedding Gradient
        gE = (gE_fm + gE_cross).astype(np.float32)
        gV = np.zeros_like(self.V)
        np.add.at(gV, X, gE)
        gV += self.l2 * self.V

        # Adam updates
        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        
        params_grads_moments = [
            (self.V, gV, self.mV, self.vV),
            (self.W_long, gW_long, self.mW_long, self.vW_long),
            (self.W_like, gW_like, self.mW_like, self.vW_like),
            (self.W_c, gW_c, self.mW_c, self.vW_c),
            (self.b_c, gb_c, self.mb_c, self.vb_c),
            (self.w_p_long, gw_p_long, self.mw_p_long, self.vw_p_long),
            (self.w_p_like, gw_p_like, self.mw_p_like, self.vw_p_like)
        ]

        for P, G, M, Vv in params_grads_moments:
            M *= b1
            M += (1 - b1) * G
            Vv *= b2
            Vv += (1 - b2) * (G * G)
            P -= self.lr * (M / (1 - b1 ** self.t)) / (np.sqrt(Vv / (1 - b2 ** self.t)) + eps)

        self.b_long -= self.lr * gb_long
        self.b_like -= self.lr * gb_like

        loss_long = -np.mean(y_long * np.log(p_long + 1e-9) + (1 - y_long) * np.log(1 - p_long + 1e-9))
        loss_like = -np.mean(y_like * np.log(p_like + 1e-9) + (1 - y_like) * np.log(1 - p_like + 1e-9))
        total_loss = loss_long + self.alpha * loss_like
        return float(total_loss), float(loss_long), float(loss_like)

    def predict(self, X, bs=100_000):
        if len(X) == 0:
            return np.empty(0, dtype=np.float32)
        preds = []
        for i in range(0, len(X), bs):
            z_long, _, _, _, _, _, _ = self.logits(X[i:i + bs])
            preds.append(z_long)
        return np.concatenate(preds)

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
                label_long = 1.0 if r['long_view'] != '0' else 0.0
                label_like = 1.0 if r.get('is_like', '0') != '0' else 0.0
                date = int(r['date'])
                user_feats = u_ext.get(uid, ['UNK'] * len(USER_FE))
                rows.append((date, uid, vid, author, tab, dur, label_long, label_like, *user_feats))

    splits = {}
    for name, (lo, hi) in SPLITS.items():
        splits[name] = [x for x in rows if lo <= x[0] <= hi]
        
    print(f"Loaded splits: { {k: len(v) for k, v in splits.items()} } in {time.time() - t0:.2f}s")
    return splits

def encode_features(splits):
    print("Encoding features across 10 fields with 20 Logarithmic Duration Bins...")
    t0 = time.time()
    tr = splits['train']
    
    # Calculate log-transformed duration bin edges on train split only
    train_log_durs = np.log1p(np.asarray([x[5] for x in tr], dtype=np.float64))
    min_log = float(np.min(train_log_durs))
    max_log = float(np.max(train_log_durs))
    print(f"Train log(1 + duration_ms) range: [{min_log:.4f}, {max_log:.4f}]")
    
    # 20 uniform bins require 19 internal bin cutoffs
    edges = np.linspace(min_log, max_log, 21)[1:-1]
    print(f"Created {len(edges)} internal cutoffs for 20 log duration bins:")
    print("  Cutoffs:", np.round(edges, 4).tolist())

    def raw_features(x):
        # x is (date, uid, vid, author, tab, dur, label_long, label_like, user_active_degree, follow, fans, friend, reg_days)
        log_d = np.log1p(float(x[5]))
        dur_bucket = str(int(np.searchsorted(edges, log_d)))
        return [
            x[1],                # user_id
            x[2],                # video_id
            x[3],                # author_id
            x[4],                # tab
            dur_bucket,          # dur_bucket
            x[8],                # user_active_degree
            x[9],                # follow_user_num_range
            x[10],               # fans_user_num_range
            x[11],               # friend_user_num_range
            x[12],               # register_days_range
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
        y_long = np.empty(len(rws), dtype=np.float32)
        y_like = np.empty(len(rws), dtype=np.float32)
        users = []
        for n, x in enumerate(rws):
            feats = raw_features(x)
            for i, v in enumerate(feats):
                X[n, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            y_long[n] = x[6]
            y_like[n] = x[7]
            users.append(x[1])
        enc[name] = (X, y_long, y_like, users)

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

def run_experiment(k=16, alpha=0.3, lr=0.001, l2=1e-6, epochs=20, bs=8192, patience=4, seed=0):
    data_dir = os.path.join(PROJECT_ROOT, 'competition_data', 'data')
    splits = load_data(data_dir)
    enc, dim = encode_features(splits)

    Xtr, ytr_long, ytr_like, _ = enc['train']
    Xva, yva_long, yva_like, uva = enc['valid']

    print(f"\nInitializing Multi-Task DCN_FM model (dim={dim}, fields={len(FIELDS)}, k={k}, D={len(FIELDS)*k}, alpha={alpha}, lr={lr}, l2={l2}, seed={seed})...")
    m = MultiTask_DCN_FM(dim, num_fields=len(FIELDS), k=k, alpha=alpha, lr=lr, l2=l2, seed=seed)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_va = None
    best_epoch = 0
    bad_epochs = 0

    history = []
    print("\nStarting Multi-Task DCN_FM training with Like Auxiliary (alpha=0.3)...")
    start_time = time.time()
    for ep in range(1, epochs + 1):
        ep_t0 = time.time()
        idx = rng.permutation(len(ytr_long))
        losses = []
        losses_long = []
        losses_like = []
        for i in range(0, len(idx), bs):
            b_idx = idx[i:i + bs]
            tot_l, l_long, l_like = m.step(Xtr[b_idx], ytr_long[b_idx], ytr_like[b_idx])
            losses.append(tot_l)
            losses_long.append(l_long)
            losses_like.append(l_like)

        mean_loss = float(np.mean(losses))
        mean_long = float(np.mean(losses_long))
        mean_like = float(np.mean(losses_like))

        va_preds = m.predict(Xva)
        va = evaluate(uva, yva_long, va_preds)
        ep_dur = time.time() - ep_t0

        log_entry = {
            'epoch': ep,
            'total_train_loss': mean_loss,
            'long_view_loss': mean_long,
            'like_loss': mean_like,
            'valid_gauc': float(va['GAUC']),
            'valid_ndcg5': float(va['nDCG@5']),
            'valid_primary': float(va['primary']),
            'epoch_time_sec': ep_dur
        }
        history.append(log_entry)

        print(f"Epoch {ep:2d}/{epochs:2d} | Train Tot: {mean_loss:.4f} (Long: {mean_long:.4f}, Like: {mean_like:.4f}) | "
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
        'hypothesis': 'Multi-Task Joint Optimization with Like Auxiliary (L = L_long_view + 0.3 * L_like)',
        'fields': FIELDS,
        'hyperparameters': {
            'k': k,
            'alpha_like': alpha,
            'lr': lr,
            'l2': l2,
            'max_epochs': epochs,
            'batch_size': bs,
            'patience': patience,
            'seed': seed,
            'num_log_bins': 20
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
