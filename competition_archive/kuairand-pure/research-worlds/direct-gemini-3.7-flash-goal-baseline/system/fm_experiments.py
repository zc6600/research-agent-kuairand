"""Systematic field ablation and optimization for FM."""

from __future__ import annotations

import csv
import math
import os
import time
from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

import numpy as np
from starter_kit.evaluate import evaluate
import starter_kit.baseline as B

LABEL = 'long_view'
SPLITS = {'train': (20220408, 20220421), 'valid': (20220422, 20220428)}


def load_raw_data(data_dir: str = "competition_data/data"):
    # Load video metadata
    vid2meta = {}
    v_path = os.path.join(data_dir, 'video_features_basic_pure.csv')
    with open(v_path) as fh:
        for r in csv.DictReader(fh):
            tag_str = r.get('tag', '')
            primary_tag = tag_str.split(',')[0] if tag_str else '0'
            vid2meta[r['video_id']] = {
                'author_id': r.get('author_id', 'UNK'),
                'video_type': r.get('video_type', 'UNK'),
                'upload_type': r.get('upload_type', 'UNK'),
                'tag': primary_tag,
            }

    # Load logs
    rows = []
    for f in ('log_standard_4_08_to_4_21_pure.csv', 'log_public_4_22_to_4_28_pure.csv'):
        path = os.path.join(data_dir, f)
        if not os.path.exists(path):
            path = os.path.join(data_dir, 'log_standard_4_22_to_5_08_pure.csv')
        with open(path) as fh:
            for r in csv.DictReader(fh):
                vid = r['video_id']
                meta = vid2meta.get(vid, {})
                d_int = int(r['date'])
                dur = float(r['duration_ms']) if r.get('duration_ms') else 1.0
                hour = str(int(r['hourmin']) // 100) if r.get('hourmin') else '0'
                dow = str((d_int % 100) % 7)
                rows.append({
                    'date': d_int,
                    'user_id': r['user_id'],
                    'video_id': vid,
                    'author_id': meta.get('author_id', 'UNK'),
                    'tag': meta.get('tag', '0'),
                    'tab': r.get('tab', '0'),
                    'video_type': meta.get('video_type', 'UNK'),
                    'upload_type': meta.get('upload_type', 'UNK'),
                    'hour': hour,
                    'dow': dow,
                    'duration_ms': dur,
                    'label': 1 if r.get(LABEL, '0') != '0' else 0,
                    'is_click': 1 if r.get('is_click', '0') != '0' else 0,
                    'is_like': 1 if r.get('is_like', '0') != '0' else 0,
                })

    splits = {}
    for name, (lo, hi) in SPLITS.items():
        splits[name] = [x for x in rows if lo <= x['date'] <= hi]
    return splits


def build_fm_dataset(splits: Dict[str, List[Dict[str, Any]]], field_names: List[str]):
    tr = splits['train']
    dur_edges = np.quantile([x['duration_ms'] for x in tr], np.linspace(0, 1, 11)[1:-1])

    def get_fields(x):
        res = []
        for f in field_names:
            if f == 'dur_bucket':
                res.append(str(int(np.searchsorted(dur_edges, x['duration_ms']))))
            else:
                res.append(str(x.get(f, 'UNK')))
        return res

    n_fields = len(field_names)
    vocabs = [dict() for _ in range(n_fields)]
    for x in tr:
        for i, v in enumerate(get_fields(x)):
            if v not in vocabs[i]:
                vocabs[i][v] = len(vocabs[i])

    unk = [len(v) for v in vocabs]
    field_dims = [len(v) + 1 for v in vocabs]
    offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int32)

    enc = {}
    for name, rws in splits.items():
        X = np.empty((len(rws), n_fields), dtype=np.int32)
        y = np.empty(len(rws), dtype=np.float32)
        users = []
        for j, x in enumerate(rws):
            for i, v in enumerate(get_fields(x)):
                X[j, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            y[j] = x['label']
            users.append(x['user_id'])
        enc[name] = (X, y, users)

    return enc, int(sum(field_dims))


def evaluate_fm(splits, field_names, k=16, lr=0.001, epochs=30, seeds=(0, 1, 2)):
    enc, dim = build_fm_dataset(splits, field_names)
    Xtr, ytr, _ = enc['train']
    Xva, yva, uva = enc['valid']

    seed_metrics = []
    for seed in seeds:
        m = B.FM(dim, k=k, lr=lr, seed=seed)
        rng = np.random.default_rng(seed)
        best = -1.0
        best_state = None
        bad = 0
        bs = 8192
        for ep in range(1, epochs + 1):
            idx = rng.permutation(len(ytr))
            for i in range(0, len(idx), bs):
                m.step(Xtr[idx[i:i + bs]], ytr[idx[i:i + bs]])
            va = evaluate(uva, yva, m.predict(Xva))
            if va['primary'] > best + 1e-5:
                best = va['primary']
                bad = 0
                best_state = (m.V.copy(), m.W.copy(), np.float32(m.b))
            else:
                bad += 1
                if bad >= 4:
                    break
        m.V, m.W, m.b = best_state
        final_va = evaluate(uva, yva, m.predict(Xva))
        seed_metrics.append(final_va)

    mean_gauc = float(np.mean([s['GAUC'] for s in seed_metrics]))
    mean_ndcg = float(np.mean([s['nDCG@5'] for s in seed_metrics]))
    mean_prim = float(np.mean([s['primary'] for s in seed_metrics]))
    std_prim = float(np.std([s['primary'] for s in seed_metrics]))
    return {
        'fields': field_names,
        'GAUC': mean_gauc,
        'nDCG@5': mean_ndcg,
        'primary': mean_prim,
        'std_primary': std_prim,
        'seeds': [s['primary'] for s in seed_metrics]
    }


if __name__ == '__main__':
    splits = load_raw_data()
    print(f"Loaded splits: {len(splits['train'])} train, {len(splits['valid'])} valid")

    field_configs = [
        ("Baseline (5 fields)", ['user_id', 'video_id', 'author_id', 'tab', 'dur_bucket']),
        ("+ Tag (6 fields)", ['user_id', 'video_id', 'author_id', 'tag', 'tab', 'dur_bucket']),
        ("+ Tag + Hour (7 fields)", ['user_id', 'video_id', 'author_id', 'tag', 'tab', 'hour', 'dur_bucket']),
        ("+ Tag + Hour + DOW (8 fields)", ['user_id', 'video_id', 'author_id', 'tag', 'tab', 'hour', 'dow', 'dur_bucket']),
        ("+ Tag + VideoType + UploadType (8 fields)", ['user_id', 'video_id', 'author_id', 'tag', 'tab', 'video_type', 'upload_type', 'dur_bucket']),
    ]

    for name, f_list in field_configs:
        t0 = time.time()
        res = evaluate_fm(splits, f_list, seeds=(0,))
        print(f"{name:35s} | GAUC {res['GAUC']:.4f} | nDCG@5 {res['nDCG@5']:.4f} | primary {res['primary']:.4f} | {time.time()-t0:.1f}s")
