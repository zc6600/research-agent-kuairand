"""Round 03 - Variant v2: Wide & Deep Architecture (Linear + 2-layer MLP [128, 64] with Dropout 0.1)
Fields (10 total):
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

Model Architecture:
- Wide component: Linear feature weights + global bias
- Deep component: 10 fields * 16 embedding dim = 160 dim concatenated embedding
  MLP: Linear(160, 128) -> ReLU -> Dropout(0.1) -> Linear(128, 64) -> ReLU -> Dropout(0.1) -> Linear(64, 1)
- Total Logit: z = z_wide + z_deep

Hyperparameters:
- Embedding dim: k=16
- Learning Rate: 0.001 (Adam)
- Batch Size: 8192
- Max Epochs: 20
- Early Stopping Patience: 4
- Seed: 0
Data: KuaiRand-Pure standard train (2022-04-08 to 2022-04-21) + public valid (2022-04-22 to 2022-04-28)
"""

import csv
import os
import sys
import time
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

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

def set_seed(seed=0):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

class WideAndDeep(nn.Module):
    def __init__(self, num_features, num_fields=10, embed_dim=16, hidden_dims=(128, 64), dropout_rate=0.1):
        super().__init__()
        self.num_features = num_features
        self.num_fields = num_fields
        self.embed_dim = embed_dim
        
        # Wide component: linear embedding (num_features x 1) + global bias
        self.wide_embed = nn.Embedding(num_features, 1)
        self.bias = nn.Parameter(torch.zeros(1))
        nn.init.zeros_(self.wide_embed.weight)
        
        # Deep component: dense embeddings (num_features x embed_dim)
        self.deep_embed = nn.Embedding(num_features, embed_dim)
        nn.init.normal_(self.deep_embed.weight, mean=0.0, std=0.01)
        
        # Deep component: MLP
        input_dim = num_fields * embed_dim  # 10 * 16 = 160
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dims[1], 1)
        )
        
        # Initialize MLP layers
        for m in self.mlp.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x):
        # x: (B, num_fields) long tensor
        # Wide part
        wide_out = self.wide_embed(x).sum(dim=1) + self.bias  # (B, 1)
        
        # Deep part
        deep_in = self.deep_embed(x).view(x.size(0), -1)      # (B, num_fields * embed_dim)
        deep_out = self.mlp(deep_in)                          # (B, 1)
        
        logits = (wide_out + deep_out).squeeze(1)             # (B,)
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

def run_experiment(k=16, hidden_dims=(128, 64), dropout_rate=0.1, lr=0.001, epochs=20, bs=8192, patience=4, seed=0):
    set_seed(seed)
    device = torch.device('cpu')  # CPU is optimal and avoids MPS synchronization overhead
    print(f"Using compute device: {device}")

    data_dir = os.path.join(PROJECT_ROOT, 'competition_data', 'data')
    splits = load_data(data_dir)
    enc, dim = encode_features(splits)

    Xtr, ytr, _ = enc['train']
    Xva, yva, uva = enc['valid']

    print(f"\nInitializing Wide & Deep model (dim={dim}, k={k}, hidden_dims={hidden_dims}, dropout={dropout_rate}, lr={lr}, seed={seed})...")
    model = WideAndDeep(num_features=dim, num_fields=len(FIELDS), embed_dim=k, hidden_dims=hidden_dims, dropout_rate=dropout_rate).to(device)
    
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Model total trainable parameters: {total_params:,}")

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train_dataset = TensorDataset(torch.from_numpy(Xtr), torch.from_numpy(ytr))
    train_loader = DataLoader(train_dataset, batch_size=bs, shuffle=True, pin_memory=False)

    best_primary = -1.0
    best_va = None
    best_epoch = 0
    bad_epochs = 0
    best_state_dict = None

    history = []
    print("\nStarting Wide & Deep training...")
    start_time = time.time()

    for ep in range(1, epochs + 1):
        ep_t0 = time.time()
        model.train()
        losses = []

        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        mean_loss = float(np.mean(losses))

        # Validation evaluation
        model.eval()
        with torch.no_grad():
            va_x = torch.from_numpy(Xva).to(device)
            # Evaluate in chunks to be memory safe
            va_preds_list = []
            eval_bs = 200_000
            for i in range(0, len(va_x), eval_bs):
                chunk_x = va_x[i:i + eval_bs]
                chunk_logits = model(chunk_x)
                va_preds_list.append(chunk_logits.cpu().numpy())
            va_preds = np.concatenate(va_preds_list)

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
            best_state_dict = {k_: v_.clone() for k_, v_ in model.state_dict().items()}
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
        'hypothesis': 'Wide & Deep Architecture (Linear + 2-layer MLP [128, 64] with Dropout 0.1) on 10 Fields',
        'fields': FIELDS,
        'hyperparameters': {
            'embed_dim': k,
            'hidden_dims': list(hidden_dims),
            'dropout_rate': dropout_rate,
            'lr': lr,
            'max_epochs': epochs,
            'batch_size': bs,
            'patience': patience,
            'seed': seed,
            'total_trainable_params': total_params
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
