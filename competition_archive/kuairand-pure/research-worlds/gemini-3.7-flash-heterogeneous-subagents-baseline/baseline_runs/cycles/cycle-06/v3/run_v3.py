"""Round 06 - Variant v3: Tri-Task Joint Model (L = L_long_view + 0.2 * L_click + 0.2 * L_like)
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

Architecture:
- Shared 10-field embedding layer V (dim x k, k=16, D=160)
- Shared DCN explicit cross layer (W_c in R^{160x160}, b_c in R^{160})
- Shared FM 2nd-order interaction
- 3 dedicated task output heads (long_view, is_click, is_like):
  * Linear weights W_t in R^{dim}
  * Scalar bias b_t in R
  * Cross-layer projection w_p_t in R^{160}

Loss:
L_total = L_long_view + 0.2 * L_click + 0.2 * L_like

Hyperparameters:
k=16, lr=0.001, l2=1e-6, batch_size=8192, max_epochs=20, patience=4, seed=0
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

PRIMARY_LABEL = 'long_view'
AUX_LABELS = ['is_click', 'is_like']
ALL_TASKS = ['long_view', 'is_click', 'is_like']
TASK_WEIGHTS = {
    'long_view': 1.0,
    'is_click': 0.2,
    'is_like': 0.2
}

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

class TriTaskDCNFM:
    def __init__(self, dim, num_fields=10, k=16, lr=0.001, l2=1e-6, seed=0, task_weights=None):
        rng = np.random.default_rng(seed)
        self.dim = dim
        self.num_fields = num_fields
        self.k = k
        self.D = num_fields * k  # 160
        self.lr = lr
        self.l2 = l2
        self.tasks = ALL_TASKS
        self.task_weights = task_weights if task_weights is not None else TASK_WEIGHTS

        # Shared Backbone Parameters
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W_c = rng.normal(0, 0.01, (self.D, self.D)).astype(np.float32)
        self.b_c = np.zeros(self.D, dtype=np.float32)

        # Task-Specific Heads (long_view, is_click, is_like)
        self.W = {t: np.zeros(dim, dtype=np.float32) for t in self.tasks}
        self.b = {t: np.float32(0.0) for t in self.tasks}
        self.w_p = {t: rng.normal(0, 0.01, self.D).astype(np.float32) for t in self.tasks}

        # Adam Moments for Shared Parameters
        self.mV = np.zeros_like(self.V)
        self.vV = np.zeros_like(self.V)
        self.mW_c = np.zeros_like(self.W_c)
        self.vW_c = np.zeros_like(self.W_c)
        self.mb_c = np.zeros_like(self.b_c)
        self.vb_c = np.zeros_like(self.b_c)

        # Adam Moments for Task Heads
        self.mW = {t: np.zeros_like(self.W[t]) for t in self.tasks}
        self.vW = {t: np.zeros_like(self.W[t]) for t in self.tasks}
        self.mw_p = {t: np.zeros_like(self.w_p[t]) for t in self.tasks}
        self.vw_p = {t: np.zeros_like(self.w_p[t]) for t in self.tasks}

        self.t = 0

    def forward_shared(self, X):
        B = len(X)
        E = self.V[X]                                        # (B, F, k)
        S = E.sum(1)                                         # (B, k)
        inter_fm = 0.5 * ((S ** 2).sum(1) - (E ** 2).sum((1, 2))) # (B,)

        x0 = E.reshape(B, self.D)                            # (B, D)
        u = x0 @ self.W_c + self.b_c                         # (B, D)
        x1 = x0 * u + x0                                     # (B, D)
        return E, S, x0, u, x1, inter_fm

    def logits(self, X, task='long_view'):
        E, S, x0, u, x1, inter_fm = self.forward_shared(X)
        lin = self.W[task][X].sum(1)                         # (B,)
        z_cross = x1 @ self.w_p[task]                        # (B,)
        z = self.b[task] + lin + inter_fm + z_cross
        return z

    def step(self, X, Y_dict):
        """
        X: (B, num_fields)
        Y_dict: dict of task -> (B,) float32 labels
        """
        B = len(X)
        E, S, x0, u, x1, inter_fm = self.forward_shared(X)

        # Compute task predictions and weighted error signals
        p_dict = {}
        g_dict = {}
        task_losses = {}

        gx1_total = np.zeros_like(x1)  # (B, D)
        g_fm_total = np.zeros(B, dtype=np.float32)  # (B,)

        gW_dict = {}
        gw_p_dict = {}
        gb_dict = {}

        for t in self.tasks:
            lin_t = self.W[t][X].sum(1)
            z_cross_t = x1 @ self.w_p[t]
            z_t = self.b[t] + lin_t + inter_fm + z_cross_t
            p_t = sigmoid(z_t)
            p_dict[t] = p_t

            y_t = Y_dict[t]
            alpha_t = self.task_weights[t]
            # Gradient of alpha_t * L_t w.r.t z_t
            g_t = (alpha_t * (p_t - y_t) / B).astype(np.float32)
            g_dict[t] = g_t

            # Task loss
            loss_t = -np.mean(y_t * np.log(p_t + 1e-9) + (1.0 - y_t) * np.log(1.0 - p_t + 1e-9))
            task_losses[t] = float(loss_t)

            # Head gradients
            gb_dict[t] = np.float32(g_t.sum())

            gW_t = np.zeros_like(self.W[t])
            np.add.at(gW_t, X, g_t[:, None])
            gW_t += self.l2 * self.W[t]
            gW_dict[t] = gW_t

            gw_p_t = (x1.T @ g_t).astype(np.float32) + self.l2 * self.w_p[t]
            gw_p_dict[t] = gw_p_t

            # Accumulate gradient into shared representations
            gx1_total += g_t[:, None] * self.w_p[t]
            g_fm_total += g_t

        # Backprop through shared cross layer
        gu = gx1_total * x0                                  # (B, D)
        gb_c = gu.sum(0).astype(np.float32) + self.l2 * self.b_c
        gW_c = (x0.T @ gu).astype(np.float32) + self.l2 * self.W_c

        gx0 = gx1_total * (u + 1.0) + gu @ self.W_c.T        # (B, D)
        gE_cross = gx0.reshape(B, self.num_fields, self.k)   # (B, F, k)

        # FM interaction gradient
        gE_fm = g_fm_total[:, None, None] * (S[:, None, :] - E) # (B, F, k)

        # Total embedding gradient
        gE = (gE_fm + gE_cross).astype(np.float32)
        gV = np.zeros_like(self.V)
        np.add.at(gV, X, gE)
        gV += self.l2 * self.V

        # Adam optimization updates
        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8

        # Update shared parameters
        shared_params = [
            (self.V, gV, self.mV, self.vV),
            (self.W_c, gW_c, self.mW_c, self.vW_c),
            (self.b_c, gb_c, self.mb_c, self.vb_c)
        ]
        for P, G, M, Vv in shared_params:
            M *= b1
            M += (1 - b1) * G
            Vv *= b2
            Vv += (1 - b2) * (G * G)
            P -= self.lr * (M / (1 - b1 ** self.t)) / (np.sqrt(Vv / (1 - b2 ** self.t)) + eps)

        # Update task head parameters
        for t in self.tasks:
            head_params = [
                (self.W[t], gW_dict[t], self.mW[t], self.vW[t]),
                (self.w_p[t], gw_p_dict[t], self.mw_p[t], self.vw_p[t])
            ]
            for P, G, M, Vv in head_params:
                M *= b1
                M += (1 - b1) * G
                Vv *= b2
                Vv += (1 - b2) * (G * G)
                P -= self.lr * (M / (1 - b1 ** self.t)) / (np.sqrt(Vv / (1 - b2 ** self.t)) + eps)

            self.b[t] -= self.lr * gb_dict[t]

        total_loss = (
            self.task_weights['long_view'] * task_losses['long_view'] +
            self.task_weights['is_click'] * task_losses['is_click'] +
            self.task_weights['is_like'] * task_losses['is_like']
        )

        return {
            'total_loss': float(total_loss),
            'long_view_loss': task_losses['long_view'],
            'click_loss': task_losses['is_click'],
            'like_loss': task_losses['is_like']
        }

    def predict(self, X, task='long_view', bs=100_000):
        if len(X) == 0:
            return np.empty(0, dtype=np.float32)
        preds = []
        for i in range(0, len(X), bs):
            z_batch = self.logits(X[i:i + bs], task=task)
            preds.append(z_batch)
        return np.concatenate(preds)


def load_data(data_dir):
    print(f"Loading data strictly from {data_dir} ...")
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
                lv_label = 1 if r[PRIMARY_LABEL] != '0' else 0
                click_label = 1 if r['is_click'] != '0' else 0
                like_label = 1 if r['is_like'] != '0' else 0
                date = int(r['date'])
                user_feats = u_ext.get(uid, ['UNK'] * len(USER_FE))
                rows.append((date, uid, vid, author, tab, dur, lv_label, click_label, like_label, *user_feats))

    splits = {}
    for name, (lo, hi) in SPLITS.items():
        splits[name] = [x for x in rows if lo <= x[0] <= hi]

    print(f"Loaded splits: { {k: len(v) for k, v in splits.items()} } in {time.time() - t0:.2f}s")
    return splits


def encode_features(splits):
    print("Encoding features across 10 fields with 20 Logarithmic Duration Bins...")
    t0 = time.time()
    tr = splits['train']

    # Duration log transformation fitted strictly on train split
    train_log_durs = np.log1p(np.asarray([x[5] for x in tr], dtype=np.float64))
    min_log = float(np.min(train_log_durs))
    max_log = float(np.max(train_log_durs))
    print(f"Train log(1 + duration_ms) range: [{min_log:.4f}, {max_log:.4f}]")

    edges = np.linspace(min_log, max_log, 21)[1:-1]
    print(f"Created {len(edges)} internal cutoffs for 20 log duration bins:")
    print("  Cutoffs:", np.round(edges, 4).tolist())

    def raw_features(x):
        # x is (date, uid, vid, author, tab, dur, lv_label, click_label, like_label, user_active_degree, follow, fans, friend, reg_days)
        log_d = np.log1p(float(x[5]))
        dur_bucket = str(int(np.searchsorted(edges, log_d)))
        return [
            x[1],                # user_id
            x[2],                # video_id
            x[3],                # author_id
            x[4],                # tab
            dur_bucket,          # dur_bucket
            x[9],                # user_active_degree
            x[10],               # follow_user_num_range
            x[11],               # fans_user_num_range
            x[12],               # friend_user_num_range
            x[13],               # register_days_range
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
        y_lv = np.empty(len(rws), dtype=np.float32)
        y_click = np.empty(len(rws), dtype=np.float32)
        y_like = np.empty(len(rws), dtype=np.float32)
        users = []
        for n, x in enumerate(rws):
            feats = raw_features(x)
            for i, v in enumerate(feats):
                X[n, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            y_lv[n] = x[6]
            y_click[n] = x[7]
            y_like[n] = x[8]
            users.append(x[1])
        enc[name] = (X, {'long_view': y_lv, 'is_click': y_click, 'is_like': y_like}, users)

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
    splits = load_data(data_dir)
    enc, dim = encode_features(splits)

    Xtr, Ytr, _ = enc['train']
    Xva, Yva, uva = enc['valid']

    print("\nTarget Label Statistics (Train Split):")
    for t in ALL_TASKS:
        pos_cnt = int(np.sum(Ytr[t]))
        rate = float(np.mean(Ytr[t]))
        print(f"  Task '{t:10s}': {pos_cnt:7d} positives ({rate * 100:.2f}%)")

    print("\nTarget Label Statistics (Validation Split):")
    for t in ALL_TASKS:
        pos_cnt = int(np.sum(Yva[t]))
        rate = float(np.mean(Yva[t]))
        print(f"  Task '{t:10s}': {pos_cnt:7d} positives ({rate * 100:.2f}%)")

    print(f"\nInitializing TriTaskDCNFM model (dim={dim}, fields={len(FIELDS)}, k={k}, D={len(FIELDS)*k}, lr={lr}, l2={l2}, seed={seed})...")
    print(f"Task loss weights: {TASK_WEIGHTS}")
    m = TriTaskDCNFM(dim, num_fields=len(FIELDS), k=k, lr=lr, l2=l2, seed=seed, task_weights=TASK_WEIGHTS)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_va = None
    best_epoch = 0
    bad_epochs = 0

    history = []
    print("\nStarting Tri-Task Joint DCN_FM training...")
    start_time = time.time()
    for ep in range(1, epochs + 1):
        ep_t0 = time.time()
        idx = rng.permutation(len(Xtr))
        batch_losses = []
        for i in range(0, len(idx), bs):
            b_idx = idx[i:i + bs]
            b_Y = {t: Ytr[t][b_idx] for t in ALL_TASKS}
            step_res = m.step(Xtr[b_idx], b_Y)
            batch_losses.append(step_res)

        mean_total_loss = float(np.mean([x['total_loss'] for x in batch_losses]))
        mean_lv_loss = float(np.mean([x['long_view_loss'] for x in batch_losses]))
        mean_click_loss = float(np.mean([x['click_loss'] for x in batch_losses]))
        mean_like_loss = float(np.mean([x['like_loss'] for x in batch_losses]))

        # Evaluate strictly on long_view on the public validation split
        va_preds = m.predict(Xva, task='long_view')
        va = evaluate(uva, Yva['long_view'], va_preds)
        ep_dur = time.time() - ep_t0

        log_entry = {
            'epoch': ep,
            'train_total_loss': mean_total_loss,
            'train_lv_loss': mean_lv_loss,
            'train_click_loss': mean_click_loss,
            'train_like_loss': mean_like_loss,
            'valid_gauc': float(va['GAUC']),
            'valid_ndcg5': float(va['nDCG@5']),
            'valid_primary': float(va['primary']),
            'epoch_time_sec': ep_dur
        }
        history.append(log_entry)

        print(f"Epoch {ep:2d}/{epochs:2d} | Loss: {mean_total_loss:.4f} (LV: {mean_lv_loss:.4f}, Click: {mean_click_loss:.4f}, Like: {mean_like_loss:.4f}) | "
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
        'variant': 'v3',
        'hypothesis': 'Tri-Task Joint Model (L = L_long_view + 0.2 * L_click + 0.2 * L_like)',
        'fields': FIELDS,
        'task_weights': TASK_WEIGHTS,
        'hyperparameters': {
            'k': k,
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
