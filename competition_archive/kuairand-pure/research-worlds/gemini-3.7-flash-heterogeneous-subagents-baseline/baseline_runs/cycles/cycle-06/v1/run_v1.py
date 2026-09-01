"""Round 06 - Variant v1: Multi-Task Joint Optimization with Click Auxiliary (L = L_long_view + 0.3 * L_click)
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

Model: Multi-Task Explicit Cross Layer + Factorization Machine (MT-DCN-FM)
Shared parameters:
- Embedding table V in R^(dim x k) (k=16)
- Explicit Cross Layer W_c in R^(160 x 160), b_c in R^160
Dedicated task output heads for Task 1 (long_view) and Task 2 (is_click):
- Head 1 (long_view): W_1 in R^dim, b_1 in R, w_p1 in R^160
- Head 2 (is_click):  W_2 in R^dim, b_2 in R, w_p2 in R^160

Loss: L_total = L_long_view + 0.3 * L_click
Hyperparameters: k=16, lr=0.001, l2=1e-6, batch_size=8192, max_epochs=20, patience=4, seed=0, click_weight=0.3
Evaluation: Strictly on long_view on log_public_4_22_to_4_28_pure.csv using starter_kit/evaluate.py
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

LABEL_MAIN = 'long_view'
LABEL_AUX = 'is_click'
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
    def __init__(self, dim, num_fields=10, k=16, lr=0.001, l2=1e-6, click_weight=0.3, seed=0):
        rng = np.random.default_rng(seed)
        self.dim = dim
        self.num_fields = num_fields
        self.k = k
        self.D = num_fields * k  # 160
        self.lr = lr
        self.l2 = l2
        self.click_weight = np.float32(click_weight)

        # 1. Shared Representation Parameters
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W_c = rng.normal(0, 0.01, (self.D, self.D)).astype(np.float32)
        self.b_c = np.zeros(self.D, dtype=np.float32)

        # 2. Task 1 (long_view) Output Head Parameters
        self.W1 = np.zeros(dim, dtype=np.float32)
        self.b1 = np.float32(0.0)
        self.w_p1 = rng.normal(0, 0.01, self.D).astype(np.float32)

        # 3. Task 2 (is_click) Output Head Parameters
        self.W2 = np.zeros(dim, dtype=np.float32)
        self.b2 = np.float32(0.0)
        self.w_p2 = rng.normal(0, 0.01, self.D).astype(np.float32)

        # Adam Optimizer Moments
        self.mV = np.zeros_like(self.V)
        self.vV = np.zeros_like(self.V)
        self.mW_c = np.zeros_like(self.W_c)
        self.vW_c = np.zeros_like(self.W_c)
        self.mb_c = np.zeros_like(self.b_c)
        self.vb_c = np.zeros_like(self.b_c)

        self.mW1 = np.zeros_like(self.W1)
        self.vW1 = np.zeros_like(self.W1)
        self.mw_p1 = np.zeros_like(self.w_p1)
        self.vw_p1 = np.zeros_like(self.w_p1)

        self.mW2 = np.zeros_like(self.W2)
        self.vW2 = np.zeros_like(self.W2)
        self.mw_p2 = np.zeros_like(self.w_p2)
        self.vw_p2 = np.zeros_like(self.w_p2)

        self.t = 0

    def logits(self, X):
        B = len(X)
        # Shared Embedding & FM Interaction
        E = self.V[X]                                        # (B, F, k)
        S = E.sum(1)                                         # (B, k)
        inter_fm = 0.5 * ((S ** 2).sum(1) - (E ** 2).sum((1, 2))) # (B,)

        # Shared Explicit Cross Layer
        x0 = E.reshape(B, self.D)                            # (B, D)
        u = x0 @ self.W_c + self.b_c                         # (B, D)
        x1 = x0 * u + x0                                     # (B, D)

        # Task 1 (long_view) Logits
        lin1 = self.W1[X].sum(1)                             # (B,)
        z1 = self.b1 + lin1 + inter_fm + x1 @ self.w_p1      # (B,)

        # Task 2 (is_click) Logits
        lin2 = self.W2[X].sum(1)                             # (B,)
        z2 = self.b2 + lin2 + inter_fm + x1 @ self.w_p2      # (B,)

        return z1, z2, E, S, x0, u, x1

    def step(self, X, y1, y2):
        B = len(y1)
        z1, z2, E, S, x0, u, x1 = self.logits(X)
        p1 = sigmoid(z1)
        p2 = sigmoid(z2)

        # Output Gradients
        g1 = ((p1 - y1) / B).astype(np.float32)
        g2 = (self.click_weight * (p2 - y2) / B).astype(np.float32)

        # 1. Gradients for Task 1 Head (long_view)
        gb1 = np.float32(g1.sum())
        gW1 = np.zeros_like(self.W1)
        np.add.at(gW1, X, g1[:, None])
        gW1 += self.l2 * self.W1
        gw_p1 = (x1.T @ g1).astype(np.float32) + self.l2 * self.w_p1

        # 2. Gradients for Task 2 Head (is_click)
        gb2 = np.float32(g2.sum())
        gW2 = np.zeros_like(self.W2)
        np.add.at(gW2, X, g2[:, None])
        gW2 += self.l2 * self.W2
        gw_p2 = (x1.T @ g2).astype(np.float32) + self.l2 * self.w_p2

        # 3. Backpropagation into Cross Layer
        gx1 = g1[:, None] * self.w_p1 + g2[:, None] * self.w_p2  # (B, D)
        gu = gx1 * x0                                            # (B, D)
        gb_c = gu.sum(0).astype(np.float32) + self.l2 * self.b_c
        gW_c = (x0.T @ gu).astype(np.float32) + self.l2 * self.W_c

        # 4. Backpropagation into x0 (concatenated embeddings)
        gx0 = gx1 * (u + 1.0) + gu @ self.W_c.T                  # (B, D)
        gE_cross = gx0.reshape(B, self.num_fields, self.k)       # (B, F, k)

        # 5. FM 2nd-order interaction gradient (shared across tasks)
        g_fm = g1 + g2
        gE_fm = g_fm[:, None, None] * (S[:, None, :] - E)        # (B, F, k)

        # 6. Total Shared Embedding gradient
        gE = (gE_fm + gE_cross).astype(np.float32)
        gV = np.zeros_like(self.V)
        np.add.at(gV, X, gE)
        gV += self.l2 * self.V

        # 7. Adam parameter updates
        self.t += 1
        b1_opt, b2_opt, eps = 0.9, 0.999, 1e-8

        params_grads_moments = [
            (self.V, gV, self.mV, self.vV),
            (self.W_c, gW_c, self.mW_c, self.vW_c),
            (self.b_c, gb_c, self.mb_c, self.vb_c),
            (self.W1, gW1, self.mW1, self.vW1),
            (self.w_p1, gw_p1, self.mw_p1, self.vw_p1),
            (self.W2, gW2, self.mW2, self.vW2),
            (self.w_p2, gw_p2, self.mw_p2, self.vw_p2),
        ]

        for P, G, M, Vv in params_grads_moments:
            M *= b1_opt
            M += (1 - b1_opt) * G
            Vv *= b2_opt
            Vv += (1 - b2_opt) * (G * G)
            P -= self.lr * (M / (1 - b1_opt ** self.t)) / (np.sqrt(Vv / (1 - b2_opt ** self.t)) + eps)

        self.b1 -= self.lr * gb1
        self.b2 -= self.lr * gb2

        loss1 = -np.mean(y1 * np.log(p1 + 1e-9) + (1 - y1) * np.log(1 - p1 + 1e-9))
        loss2 = -np.mean(y2 * np.log(p2 + 1e-9) + (1 - y2) * np.log(1 - p2 + 1e-9))
        total_loss = float(loss1 + float(self.click_weight) * loss2)
        return total_loss, float(loss1), float(loss2)

    def predict_main(self, X, bs=100_000):
        """Evaluate main task (long_view) logits for validation ranking."""
        if len(X) == 0:
            return np.empty(0, dtype=np.float32)
        preds = []
        for i in range(0, len(X), bs):
            z1, _, _, _, _, _, _ = self.logits(X[i:i + bs])
            preds.append(z1)
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
                label_lv = 1 if r[LABEL_MAIN] != '0' else 0
                label_click = 1 if r[LABEL_AUX] != '0' else 0
                date = int(r['date'])
                user_feats = u_ext.get(uid, ['UNK'] * len(USER_FE))
                rows.append((date, uid, vid, author, tab, dur, label_lv, label_click, *user_feats))

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

    # 20 uniform bins require 19 internal cutoffs
    edges = np.linspace(min_log, max_log, 21)[1:-1]
    print(f"Created {len(edges)} internal cutoffs for 20 log duration bins:")
    print("  Cutoffs:", np.round(edges, 4).tolist())

    def raw_features(x):
        # x is (date, uid, vid, author, tab, dur, label_lv, label_click, user_active_degree, follow, fans, friend, reg_days)
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
        y_lv = np.empty(len(rws), dtype=np.float32)
        y_clk = np.empty(len(rws), dtype=np.float32)
        users = []
        for n, x in enumerate(rws):
            feats = raw_features(x)
            for i, v in enumerate(feats):
                X[n, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            y_lv[n] = x[6]
            y_clk[n] = x[7]
            users.append(x[1])
        enc[name] = {
            'X': X,
            'y_lv': y_lv,
            'y_clk': y_clk,
            'users': users
        }

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

def run_experiment(k=16, lr=0.001, l2=1e-6, click_weight=0.3, epochs=20, bs=8192, patience=4, seed=0):
    data_dir = os.path.join(PROJECT_ROOT, 'competition_data', 'data')
    splits = load_data(data_dir)
    enc, dim = encode_features(splits)

    Xtr = enc['train']['X']
    ytr_lv = enc['train']['y_lv']
    ytr_clk = enc['train']['y_clk']

    Xva = enc['valid']['X']
    yva_lv = enc['valid']['y_lv']
    uva = enc['valid']['users']

    print(f"\nInitializing MultiTask_DCN_FM model (dim={dim}, fields={len(FIELDS)}, k={k}, D={len(FIELDS)*k}, lr={lr}, l2={l2}, click_weight={click_weight}, seed={seed})...")
    m = MultiTask_DCN_FM(dim, num_fields=len(FIELDS), k=k, lr=lr, l2=l2, click_weight=click_weight, seed=seed)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_va = None
    best_epoch = 0
    bad_epochs = 0

    history = []
    print(f"\nStarting Multi-Task Joint Optimization (L = L_long_view + {click_weight} * L_click)...")
    start_time = time.time()
    for ep in range(1, epochs + 1):
        ep_t0 = time.time()
        idx = rng.permutation(len(ytr_lv))
        losses = []
        losses1 = []
        losses2 = []
        for i in range(0, len(idx), bs):
            b_idx = idx[i:i + bs]
            tot_l, l1, l2_val = m.step(Xtr[b_idx], ytr_lv[b_idx], ytr_clk[b_idx])
            losses.append(tot_l)
            losses1.append(l1)
            losses2.append(l2_val)

        mean_loss = float(np.mean(losses))
        mean_l1 = float(np.mean(losses1))
        mean_l2 = float(np.mean(losses2))

        va_preds = m.predict_main(Xva)
        va = evaluate(uva, yva_lv, va_preds)
        ep_dur = time.time() - ep_t0

        log_entry = {
            'epoch': ep,
            'train_loss_total': mean_loss,
            'train_loss_long_view': mean_l1,
            'train_loss_click': mean_l2,
            'valid_gauc': float(va['GAUC']),
            'valid_ndcg5': float(va['nDCG@5']),
            'valid_primary': float(va['primary']),
            'epoch_time_sec': ep_dur
        }
        history.append(log_entry)

        print(f"Epoch {ep:2d}/{epochs:2d} | Train L_tot: {mean_loss:.4f} (L_lv: {mean_l1:.4f}, L_clk: {mean_l2:.4f}) | "
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
        'variant': 'v1',
        'hypothesis': 'Multi-Task Joint Optimization with Click Auxiliary (L = L_long_view + 0.3 * L_click)',
        'fields': FIELDS,
        'hyperparameters': {
            'k': k,
            'lr': lr,
            'l2': l2,
            'click_weight': click_weight,
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
