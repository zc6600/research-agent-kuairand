"""Fast vectorized data loading, feature preprocessing, and sequence construction for KuaiRand-Pure.

Features supported:
- 'base5': user_id, video_id, author_id, tab, dur_bucket (Starter kit baseline)
- 'cwm13': 13 fields from CWM
- 'extended': 29 rich categorical fields (user demographics, video content, time/context)
- User historical interaction sequence builder with 7 facets:
  0: all video_id
  1: all author_id
  2: all tag_first
  3: engaged video_id (is_click == 1 or long_view == 1)
  4: engaged author_id (is_click == 1 or long_view == 1)
  5: negative / skipped video_id (play_time_ms < 3000 and is_click == 0 and long_view == 0)
  6: time_delta bucket (elapsed seconds between history interaction and candidate item)
- Multi-task targets: long_view, is_click, is_like, is_profile_enter, is_comment
- Inverse Propensity Score (IPS) weights derived from random exposure log
"""
import os
import time
import bisect
import collections
import numpy as np
import polars as pl
import torch
from torch.utils.data import Dataset, DataLoader

BASE_FIELDS = ['user_id', 'video_id', 'author_id', 'tab', 'dur_bucket']

CWM_FIELDS = [
    'user_id', 'video_id', 'author_id', 'tab', 'dur_bucket',
    'music_id', 'video_type', 'upload_type',
    'follow_user_num_range', 'register_days_range', 'fans_user_num_range',
    'friend_user_num_range', 'user_active_degree'
]

EXT_FIELDS = [
    # User side
    'user_id', 'user_active_degree', 'follow_user_num_range', 'fans_user_num_range',
    'friend_user_num_range', 'register_days_range', 'is_live_streamer', 'is_video_author',
    'onehot_feat0', 'onehot_feat1', 'onehot_feat2', 'onehot_feat5', 'onehot_feat6',
    'onehot_feat7', 'onehot_feat8', 'onehot_feat9', 'onehot_feat10', 'onehot_feat11',
    # Video side
    'video_id', 'author_id', 'video_type', 'upload_type', 'music_id', 'music_type', 'tag_first', 'dur_bucket',
    # Context / Time
    'tab', 'hour_bucket', 'day_of_week'
]

# 14 discrete interval boundary edges in seconds (yields 15 non-zero buckets: 1..15; 0 reserved for padding)
TIME_EDGES = [
    10.0, 30.0, 60.0, 180.0, 600.0, 1800.0, 3600.0,
    10800.0, 21600.0, 43200.0, 86400.0, 172800.0, 345600.0, 604800.0
]


def bucket_time_delta_sec(dt_sec):
    """Maps time delta in seconds to bucket 1..15."""
    return bisect.bisect_right(TIME_EDGES, max(0.0, dt_sec)) + 1


def load_and_preprocess(data_dir='competition_data/data', mode='extended', max_seq_len=20):
    """Loads raw data, processes all features with Polars vectorization, and returns encoded splits.

    Returns dict containing:
      - 'train': (X, y, user_ids, multi_y, user_seqs, seq_lens, ips_weights)
      - 'valid': (X, y, user_ids, multi_y, user_seqs, seq_lens, ips_weights)
      - 'field_dims': list of vocab sizes per field
      - 'feature_names': list of column names
      - 'num_fields': total number of sparse categorical fields
      - 'video_vocab_size': size of video_id vocab (for sequence embedding)
    """
    t0 = time.time()
    train_path = os.path.join(data_dir, 'log_standard_4_08_to_4_21_pure.csv')
    valid_path = os.path.join(data_dir, 'log_public_4_22_to_4_28_pure.csv')
    random_path = os.path.join(data_dir, 'log_random_4_22_to_4_28_pure.csv')
    user_path = os.path.join(data_dir, 'user_features_pure.csv')
    video_path = os.path.join(data_dir, 'video_features_basic_pure.csv')

    train_df = pl.read_csv(train_path)
    valid_df = pl.read_csv(valid_path)
    user_df = pl.read_csv(user_path)
    video_df = pl.read_csv(video_path)

    # 1. Compute duration quantiles from train
    dur_edges = np.quantile(train_df['duration_ms'].to_numpy(), np.linspace(0, 1, 11)[1:-1])

    def bucket_dur(dur_series):
        arr = dur_series.to_numpy()
        return np.searchsorted(dur_edges, arr).astype(np.int32)

    # 2. Clean video features
    video_clean = video_df.select([
        pl.col('video_id').cast(pl.Utf8),
        pl.col('author_id').fill_null('UNK_AUTH').cast(pl.Utf8),
        pl.col('video_type').fill_null('UNK_VT').cast(pl.Utf8),
        pl.col('upload_type').fill_null('UNK_UT').cast(pl.Utf8),
        pl.col('music_id').fill_null('UNK_MUS').cast(pl.Utf8),
        pl.col('music_type').fill_null('UNK_MT').cast(pl.Utf8),
        pl.col('tag').fill_null('UNK_TAG').str.split(',').list.get(0).alias('tag_first').cast(pl.Utf8),
    ])

    # 3. Clean user features
    user_cols = [
        'user_active_degree', 'follow_user_num_range', 'fans_user_num_range',
        'friend_user_num_range', 'register_days_range', 'is_live_streamer', 'is_video_author',
        'onehot_feat0', 'onehot_feat1', 'onehot_feat2', 'onehot_feat5', 'onehot_feat6',
        'onehot_feat7', 'onehot_feat8', 'onehot_feat9', 'onehot_feat10', 'onehot_feat11'
    ]
    user_select = [pl.col('user_id').cast(pl.Utf8)] + [
        pl.col(c).fill_null('UNK').cast(pl.Utf8) for c in user_cols
    ]
    user_clean = user_df.select(user_select)

    def process_logs(df):
        df_mod = df.with_columns([
            pl.col('user_id').cast(pl.Utf8),
            pl.col('video_id').cast(pl.Utf8),
            pl.col('tab').cast(pl.Utf8),
            (pl.col('hourmin') // 100).cast(pl.Utf8).alias('hour_bucket'),
            (pl.col('date') % 7).cast(pl.Utf8).alias('day_of_week'),
            pl.Series('dur_bucket', bucket_dur(df['duration_ms'])).cast(pl.Utf8),
        ])
        # Join
        joined = df_mod.join(video_clean, on='video_id', how='left')
        joined = joined.join(user_clean, on='user_id', how='left')
        return joined

    tr_joined = process_logs(train_df)
    va_joined = process_logs(valid_df)

    if mode == 'base5':
        feature_names = BASE_FIELDS
    elif mode == 'cwm13':
        feature_names = CWM_FIELDS
    elif mode == 'extended':
        feature_names = EXT_FIELDS
    else:
        raise ValueError(f"Unknown mode: {mode}")

    # Build vocabularies strictly on train
    vocabs = {}
    unk_ids = {}
    field_dims = []
    for col in feature_names:
        unique_vals = tr_joined[col].fill_null('UNK').unique().to_list()
        vdict = {val: idx for idx, val in enumerate(unique_vals)}
        vocabs[col] = vdict
        unk_ids[col] = len(vdict)
        field_dims.append(len(vdict) + 1)

    offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int32)

    def encode_split(joined_df):
        N = len(joined_df)
        X = np.empty((N, len(feature_names)), dtype=np.int32)
        for i, col in enumerate(feature_names):
            vals = joined_df[col].fill_null('UNK').to_list()
            vdict = vocabs[col]
            unk = unk_ids[col]
            X[:, i] = [vdict.get(v, unk) for v in vals]
        
        y = joined_df['long_view'].cast(pl.Float32).to_numpy()
        users = joined_df['user_id'].to_list()

        multi_y = np.column_stack([
            joined_df['long_view'].cast(pl.Float32).to_numpy(),
            joined_df['is_click'].cast(pl.Float32).to_numpy(),
            joined_df['is_like'].cast(pl.Float32).to_numpy(),
            joined_df['is_profile_enter'].cast(pl.Float32).to_numpy(),
            joined_df['is_comment'].cast(pl.Float32).to_numpy(),
        ])
        return X, y, users, multi_y

    X_tr, y_tr, u_tr, my_tr = encode_split(tr_joined)
    X_va, y_va, u_va, my_va = encode_split(va_joined)

    # Compute Inverse Propensity Scoring (IPS) weights from random exposure log
    if os.path.exists(random_path):
        rand_df = pl.read_csv(random_path)
        tr_vid_counts = train_df['video_id'].value_counts()
        ra_vid_counts = rand_df['video_id'].value_counts()
        prop_df = tr_vid_counts.join(ra_vid_counts, on='video_id', suffix='_rand', how='left').fill_null(0)
        v_ids = prop_df['video_id'].cast(pl.Utf8).to_list()
        c_tr = prop_df['count'].to_numpy().astype(float)
        c_ra = prop_df['count_rand'].to_numpy().astype(float)
        p_tr = c_tr / c_tr.sum()
        p_ra = (c_ra + 1.0) / (c_ra.sum() + len(c_ra))
        raw_ips = p_ra / np.maximum(p_tr, 1e-7)
        norm_ips = raw_ips / np.mean(raw_ips)
        clipped_ips = np.clip(norm_ips, 0.2, 5.0).astype(np.float32)
        ips_map = {vid: w for vid, w in zip(v_ids, clipped_ips)}

        tr_raw_vids = tr_joined['video_id'].to_list()
        va_raw_vids = va_joined['video_id'].to_list()
        ips_tr = np.array([ips_map.get(v, 1.0) for v in tr_raw_vids], dtype=np.float32)
        ips_va = np.array([ips_map.get(v, 1.0) for v in va_raw_vids], dtype=np.float32)
    else:
        ips_tr = np.ones(len(X_tr), dtype=np.float32)
        ips_va = np.ones(len(X_va), dtype=np.float32)

    # 4. Build sequential interaction history per user for sequential models
    # Multi-facet support:
    # 0: all video_id
    # 1: all author_id
    # 2: all tag_first
    # 3: engaged video_id (is_click == 1 or long_view == 1)
    # 4: engaged author_id (is_click == 1 or long_view == 1)
    # 5: negative / skipped video_id (play_time_ms < 3000 and is_click == 0 and long_view == 0)
    # 6: time_delta bucket (elapsed seconds between history interaction and candidate item)
    vid_col_idx = feature_names.index('video_id')
    auth_col_idx = feature_names.index('author_id') if 'author_id' in feature_names else None
    tag_col_idx = feature_names.index('tag_first') if 'tag_first' in feature_names else None

    NUM_FACETS = 7

    def build_user_sequences(joined_df, is_train=True):
        user_hist_vid = collections.defaultdict(list)
        user_hist_auth = collections.defaultdict(list)
        user_hist_tag = collections.defaultdict(list)
        user_hist_eng_vid = collections.defaultdict(list)
        user_hist_eng_auth = collections.defaultdict(list)
        user_hist_neg_vid = collections.defaultdict(list)
        user_hist_time_ms = collections.defaultdict(list)

        N = len(joined_df)
        seqs = np.zeros((N, NUM_FACETS, max_seq_len), dtype=np.int32)
        lengths = np.zeros((N, NUM_FACETS), dtype=np.int32)

        user_ids = joined_df['user_id'].to_list()
        vid_indices = X_tr[:, vid_col_idx] if is_train else X_va[:, vid_col_idx]
        auth_indices = X_tr[:, auth_col_idx] if (is_train and auth_col_idx is not None) else (X_va[:, auth_col_idx] if auth_col_idx is not None else None)
        tag_indices = X_tr[:, tag_col_idx] if (is_train and tag_col_idx is not None) else (X_va[:, tag_col_idx] if tag_col_idx is not None else None)

        is_click = joined_df['is_click'].to_numpy()
        long_view = joined_df['long_view'].to_numpy()
        play_time_ms = joined_df['play_time_ms'].to_numpy()
        time_ms = joined_df['time_ms'].to_numpy()

        is_eng = ((is_click == 1) | (long_view == 1))
        is_neg = ((play_time_ms < 3000) & (is_click == 0) & (long_view == 0))

        for i in range(N):
            u = user_ids[i]
            t_curr = time_ms[i]

            # Facet 0: All video_id & Facet 6: time_delta buckets
            h0 = user_hist_vid[u]
            l0 = len(h0)
            if l0 > 0:
                rec0 = h0[-max_seq_len:]
                seqs[i, 0, :len(rec0)] = rec0
                lengths[i, 0] = len(rec0)

                # Facet 6: time_delta
                ht0 = user_hist_time_ms[u][-max_seq_len:]
                dt_buckets = [bucket_time_delta_sec((t_curr - t_past) / 1000.0) for t_past in ht0]
                seqs[i, 6, :len(dt_buckets)] = dt_buckets
                lengths[i, 6] = len(dt_buckets)

            # Facet 1: All author_id
            if auth_indices is not None:
                h1 = user_hist_auth[u]
                l1 = len(h1)
                if l1 > 0:
                    rec1 = h1[-max_seq_len:]
                    seqs[i, 1, :len(rec1)] = rec1
                    lengths[i, 1] = len(rec1)

            # Facet 2: All tag_first
            if tag_indices is not None:
                h2 = user_hist_tag[u]
                l2 = len(h2)
                if l2 > 0:
                    rec2 = h2[-max_seq_len:]
                    seqs[i, 2, :len(rec2)] = rec2
                    lengths[i, 2] = len(rec2)

            # Facet 3: Engaged video_id
            h3 = user_hist_eng_vid[u]
            l3 = len(h3)
            if l3 > 0:
                rec3 = h3[-max_seq_len:]
                seqs[i, 3, :len(rec3)] = rec3
                lengths[i, 3] = len(rec3)

            # Facet 4: Engaged author_id
            if auth_indices is not None:
                h4 = user_hist_eng_auth[u]
                l4 = len(h4)
                if l4 > 0:
                    rec4 = h4[-max_seq_len:]
                    seqs[i, 4, :len(rec4)] = rec4
                    lengths[i, 4] = len(rec4)

            # Facet 5: Negative / skipped video_id
            h5 = user_hist_neg_vid[u]
            l5 = len(h5)
            if l5 > 0:
                rec5 = h5[-max_seq_len:]
                seqs[i, 5, :len(rec5)] = rec5
                lengths[i, 5] = len(rec5)

            # Update histories with current interaction
            user_hist_vid[u].append(vid_indices[i])
            user_hist_time_ms[u].append(t_curr)
            if auth_indices is not None:
                user_hist_auth[u].append(auth_indices[i])
            if tag_indices is not None:
                user_hist_tag[u].append(tag_indices[i])
            if is_eng[i]:
                user_hist_eng_vid[u].append(vid_indices[i])
                if auth_indices is not None:
                    user_hist_eng_auth[u].append(auth_indices[i])
            if is_neg[i]:
                user_hist_neg_vid[u].append(vid_indices[i])

        hist_state = {
            'vid': user_hist_vid,
            'time_ms': user_hist_time_ms,
            'auth': user_hist_auth,
            'tag': user_hist_tag,
            'eng_vid': user_hist_eng_vid,
            'eng_auth': user_hist_eng_auth,
            'neg_vid': user_hist_neg_vid,
        }
        return seqs, lengths, hist_state

    tr_seqs, tr_lens, user_hist_state = build_user_sequences(tr_joined, is_train=True)

    # For valid, user history carries over from the end of train
    def build_valid_sequences(va_df, hist_state):
        N = len(va_df)
        seqs = np.zeros((N, NUM_FACETS, max_seq_len), dtype=np.int32)
        lengths = np.zeros((N, NUM_FACETS), dtype=np.int32)

        user_ids = va_df['user_id'].to_list()
        vid_indices = X_va[:, vid_col_idx]
        auth_indices = X_va[:, auth_col_idx] if auth_col_idx is not None else None
        tag_indices = X_va[:, tag_col_idx] if tag_col_idx is not None else None

        is_click = va_df['is_click'].to_numpy()
        long_view = va_df['long_view'].to_numpy()
        play_time_ms = va_df['play_time_ms'].to_numpy()
        time_ms = va_df['time_ms'].to_numpy()

        is_eng = ((is_click == 1) | (long_view == 1))
        is_neg = ((play_time_ms < 3000) & (is_click == 0) & (long_view == 0))

        # Deep copy history lists for valid simulation
        hist_vid = {k: list(v) for k, v in hist_state['vid'].items()}
        hist_time = {k: list(v) for k, v in hist_state['time_ms'].items()}
        hist_auth = {k: list(v) for k, v in hist_state['auth'].items()}
        hist_tag = {k: list(v) for k, v in hist_state['tag'].items()}
        hist_eng_vid = {k: list(v) for k, v in hist_state['eng_vid'].items()}
        hist_eng_auth = {k: list(v) for k, v in hist_state['eng_auth'].items()}
        hist_neg_vid = {k: list(v) for k, v in hist_state['neg_vid'].items()}

        for i in range(N):
            u = user_ids[i]
            t_curr = time_ms[i]

            # Facet 0 & 6
            h0 = hist_vid.get(u, [])
            l0 = len(h0)
            if l0 > 0:
                rec0 = h0[-max_seq_len:]
                seqs[i, 0, :len(rec0)] = rec0
                lengths[i, 0] = len(rec0)

                ht0 = hist_time.get(u, [])[-max_seq_len:]
                dt_buckets = [bucket_time_delta_sec((t_curr - t_past) / 1000.0) for t_past in ht0]
                seqs[i, 6, :len(dt_buckets)] = dt_buckets
                lengths[i, 6] = len(dt_buckets)

            # Facet 1
            if auth_indices is not None:
                h1 = hist_auth.get(u, [])
                l1 = len(h1)
                if l1 > 0:
                    rec1 = h1[-max_seq_len:]
                    seqs[i, 1, :len(rec1)] = rec1
                    lengths[i, 1] = len(rec1)

            # Facet 2
            if tag_indices is not None:
                h2 = hist_tag.get(u, [])
                l2 = len(h2)
                if l2 > 0:
                    rec2 = h2[-max_seq_len:]
                    seqs[i, 2, :len(rec2)] = rec2
                    lengths[i, 2] = len(rec2)

            # Facet 3
            h3 = hist_eng_vid.get(u, [])
            l3 = len(h3)
            if l3 > 0:
                rec3 = h3[-max_seq_len:]
                seqs[i, 3, :len(rec3)] = rec3
                lengths[i, 3] = len(rec3)

            # Facet 4
            if auth_indices is not None:
                h4 = hist_eng_auth.get(u, [])
                l4 = len(h4)
                if l4 > 0:
                    rec4 = h4[-max_seq_len:]
                    seqs[i, 4, :len(rec4)] = rec4
                    lengths[i, 4] = len(rec4)

            # Facet 5
            h5 = hist_neg_vid.get(u, [])
            l5 = len(h5)
            if l5 > 0:
                rec5 = h5[-max_seq_len:]
                seqs[i, 5, :len(rec5)] = rec5
                lengths[i, 5] = len(rec5)

            # Update histories
            if u not in hist_vid:
                hist_vid[u] = []
                hist_time[u] = []
            hist_vid[u].append(vid_indices[i])
            hist_time[u].append(t_curr)

            if auth_indices is not None:
                if u not in hist_auth:
                    hist_auth[u] = []
                hist_auth[u].append(auth_indices[i])

            if tag_indices is not None:
                if u not in hist_tag:
                    hist_tag[u] = []
                hist_tag[u].append(tag_indices[i])

            if is_eng[i]:
                if u not in hist_eng_vid:
                    hist_eng_vid[u] = []
                hist_eng_vid[u].append(vid_indices[i])

                if auth_indices is not None:
                    if u not in hist_eng_auth:
                        hist_eng_auth[u] = []
                    hist_eng_auth[u].append(auth_indices[i])

            if is_neg[i]:
                if u not in hist_neg_vid:
                    hist_neg_vid[u] = []
                hist_neg_vid[u].append(vid_indices[i])

        return seqs, lengths

    va_seqs, va_lens = build_valid_sequences(va_joined, user_hist_state)

    total_time = time.time() - t0
    video_vocab_size = field_dims[vid_col_idx]

    return {
        'train': (X_tr, y_tr, u_tr, my_tr, tr_seqs, tr_lens, ips_tr),
        'valid': (X_va, y_va, u_va, my_va, va_seqs, va_lens, ips_va),
        'field_dims': field_dims,
        'offsets': offsets,
        'feature_names': feature_names,
        'num_fields': len(feature_names),
        'total_dim': int(sum(field_dims)),
        'video_vocab_size': video_vocab_size,
        'load_time': total_time
    }


class KuaiRandDataset(Dataset):
    """PyTorch Dataset supporting tabular features, multi-feedback targets, and interaction sequences."""
    def __init__(self, X, y, multi_y=None, seqs=None, seq_lens=None, ips=None):
        self.X = torch.from_numpy(np.ascontiguousarray(X).copy()).long()
        self.y = torch.from_numpy(np.ascontiguousarray(y).copy()).float()
        self.multi_y = torch.from_numpy(np.ascontiguousarray(multi_y).copy()).float() if multi_y is not None else None
        self.seqs = torch.from_numpy(np.ascontiguousarray(seqs).copy()).long() if seqs is not None else None
        self.seq_lens = torch.from_numpy(np.ascontiguousarray(seq_lens).copy()).long() if seq_lens is not None else None
        self.ips = torch.from_numpy(np.ascontiguousarray(ips).copy()).float() if ips is not None else None

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        item = {
            'X': self.X[idx],
            'y': self.y[idx]
        }
        if self.multi_y is not None:
            item['multi_y'] = self.multi_y[idx]
        if self.seqs is not None:
            item['seqs'] = self.seqs[idx]
            item['seq_lens'] = self.seq_lens[idx]
        if self.ips is not None:
            item['ips'] = self.ips[idx]
        return item
