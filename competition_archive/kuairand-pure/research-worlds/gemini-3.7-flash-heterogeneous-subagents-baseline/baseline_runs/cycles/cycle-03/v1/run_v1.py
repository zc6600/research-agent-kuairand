"""Round 03 - Variant v1: DeepFM Architecture (FM + 2-layer MLP [64, 32] with ReLU)
Fields (10 fields, k=16):
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

Model: DeepFM (Shared Embedding k=16, Linear + FM 2nd-order + MLP [160 -> 64 -> 32 -> 1])
Hyperparameters: k=16, lr=0.001, batch_size=8192, max_epochs=20, patience=4, weight_decay=1e-6
Data: KuaiRand-Pure standard train + public valid
"""

import csv
import os
import sys
import time
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

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

def set_seed(seed=42):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

class DeepFM(nn.Module):
    def __init__(self, num_features, num_fields=10, k=16, mlp_dims=(64, 32)):
        super().__init__()
        self.num_features = num_features
        self.num_fields = num_fields
        self.k = k

        # 1st-order linear embeddings + global bias
        self.W = nn.Embedding(num_features, 1)
        nn.init.zeros_(self.W.weight)
        self.b = nn.Parameter(torch.zeros(1))

        # 2nd-order & Deep shared feature embeddings
        self.V = nn.Embedding(num_features, k)
        nn.init.normal_(self.V.weight, std=0.01)

        # Deep Component (MLP)
        layers = []
        in_dim = num_fields * k
        for h_dim in mlp_dims:
            linear = nn.Linear(in_dim, h_dim)
            nn.init.xavier_uniform_(linear.weight)
            nn.init.zeros_(linear.bias)
            layers.append(linear)
            layers.append(nn.ReLU())
            in_dim = h_dim
        
        out_linear = nn.Linear(in_dim, 1)
        nn.init.xavier_uniform_(out_linear.weight)
        nn.init.zeros_(out_linear.bias)
        layers.append(out_linear)

        self.mlp = nn.Sequential(*layers)

    def forward(self, x):
        # x: (B, num_fields) of integer IDs
        B = x.shape[0]

        # 1. Linear component
        linear_part = self.W(x).sum(dim=1).squeeze(-1) + self.b  # (B,)

        # 2. FM 2nd-order interaction component
        E = self.V(x)  # (B, F, k)
        sum_E = E.sum(dim=1)  # (B, k)
        sum_sq = (sum_E ** 2).sum(dim=1)  # (B,)
        sq_sum = (E ** 2).sum(dim=(1, 2))  # (B,)
        fm_inter = 0.5 * (sum_sq - sq_sum)  # (B,)

        # 3. Deep MLP component
        E_flat = E.reshape(B, -1)  # (B, F * k)
        mlp_part = self.mlp(E_flat).squeeze(-1)  # (B,)

        # Total logits
        logits = linear_part + fm_inter + mlp_part
        return logits

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
        X = np.empty((len(rws), len(FIELDS)), dtype=np.int64)
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

def run_experiment(k=16, lr=0.001, mlp_dims=(64, 32), epochs=20, bs=8192, patience=4, weight_decay=1e-6, seed=42):
    set_seed(seed)
    data_dir = os.path.join(PROJECT_ROOT, 'competition_data', 'data')
    splits = load_data(data_dir)
    enc, dim = encode_features(splits)

    Xtr, ytr, _ = enc['train']
    Xva, yva, uva = enc['valid']

    print(f"\nInitializing DeepFM model (dim={dim}, k={k}, mlp_dims={mlp_dims}, lr={lr}, weight_decay={weight_decay}, seed={seed})...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    model = DeepFM(num_features=dim, num_fields=len(FIELDS), k=k, mlp_dims=mlp_dims).to(device)
    
    # Calculate parameter count
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total model parameters: {total_params:,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.BCEWithLogitsLoss()

    # Create PyTorch datasets
    train_dataset = TensorDataset(torch.from_numpy(Xtr), torch.from_numpy(ytr))
    train_loader = DataLoader(train_dataset, batch_size=bs, shuffle=True, drop_last=False)

    Xva_t = torch.from_numpy(Xva).to(device)

    best_primary = -1.0
    best_va = None
    best_epoch = 0
    bad_epochs = 0

    history = []
    print("\nStarting DeepFM training...")
    start_time = time.time()

    for ep in range(1, epochs + 1):
        ep_t0 = time.time()
        model.train()
        losses = []

        for b_X, b_y in train_loader:
            b_X, b_y = b_X.to(device), b_y.to(device)
            optimizer.zero_grad()
            logits = model(b_X)
            loss = criterion(logits, b_y)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        mean_loss = float(np.mean(losses))

        # Validation evaluation
        model.eval()
        with torch.no_grad():
            # Batch inference to avoid OOM
            preds_list = []
            eval_bs = 65536
            for i in range(0, len(Xva_t), eval_bs):
                batch_preds = model(Xva_t[i:i + eval_bs])
                preds_list.append(batch_preds.cpu().numpy())
            va_preds = np.concatenate(preds_list)

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
        'variant': 'v1',
        'hypothesis': 'DeepFM Architecture (FM + 2-layer MLP [64, 32] with ReLU)',
        'architecture': {
            'model_type': 'DeepFM',
            'num_fields': len(FIELDS),
            'embedding_dim': k,
            'mlp_layers': [len(FIELDS) * k, *mlp_dims, 1],
            'total_parameters': total_params
        },
        'fields': FIELDS,
        'hyperparameters': {
            'k': k,
            'lr': lr,
            'mlp_dims': list(mlp_dims),
            'weight_decay': weight_decay,
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

    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'results.json'))
    with open(out_file, 'w') as fh:
        json.dump(results, fh, indent=2, default=default_json)
        fh.flush()
        os.fsync(fh.fileno())
    print(f"Saved results to {out_file}")

    return results

if __name__ == '__main__':
    run_experiment()
