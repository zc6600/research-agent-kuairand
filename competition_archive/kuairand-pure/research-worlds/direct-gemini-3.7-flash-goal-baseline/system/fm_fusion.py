"""FM with Fine-grained Regularization, Target Statistics Fusion, and Multi-Seed Ensembling."""

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


def load_dataset_with_stats(data_dir: str = "competition_data/data"):
    # 1. Video metadata
    vid2meta = {}
    v_path = os.path.join(data_dir, 'video_features_basic_pure.csv')
    with open(v_path) as fh:
        for r in csv.DictReader(fh):
            tag_str = r.get('tag', '')
            primary_tag = tag_str.split(',')[0] if tag_str else '0'
            vid2meta[r['video_id']] = {
                'author_id': r.get('author_id', 'UNK'),
                'tag': primary_tag,
            }

    # 2. Logs
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
                play = float(r['play_time_ms']) if r.get('play_time_ms') else 0.0
                hour = str(int(r['hourmin']) // 100) if r.get('hourmin') else '0'
                dow = str((d_int % 100) % 7)
                rows.append({
                    'date': d_int,
                    'user_id': r['user_id'],
                    'video_id': vid,
                    'author_id': meta.get('author_id', 'UNK'),
                    'tag': meta.get('tag', '0'),
                    'tab': r.get('tab', '0'),
                    'hour': hour,
                    'dow': dow,
                    'duration_ms': dur,
                    'play_time_ms': play,
                    'play_ratio': min(5.0, play / max(1.0, dur)),
                    'label': 1 if r.get(LABEL, '0') != '0' else 0,
                    'is_click': 1 if r.get('is_click', '0') != '0' else 0,
                    'is_like': 1 if r.get('is_like', '0') != '0' else 0,
                })

    train_rows = [x for x in rows if SPLITS['train'][0] <= x['date'] <= SPLITS['train'][1]]
    valid_rows = [x for x in rows if SPLITS['valid'][0] <= x['date'] <= SPLITS['valid'][1]]

    # 3. Compute leak-free priors on train
    n_tr = len(train_rows)
    g_lv = sum(x['label'] for x in train_rows) / n_tr
    g_clk = sum(x['is_click'] for x in train_rows) / n_tr
    g_pr = sum(x['play_ratio'] for x in train_rows) / n_tr

    item_cnt = Counter(); item_lv = Counter(); item_clk = Counter(); item_pr = defaultdict(float)
    author_cnt = Counter(); author_lv = Counter(); author_clk = Counter()
    user_tag_cnt = Counter(); user_tag_lv = Counter()
    user_author_cnt = Counter(); user_author_lv = Counter()

    for r in train_rows:
        vid, aid, tag, uid = r['video_id'], r['author_id'], r['tag'], r['user_id']
        lv, clk, pr = r['label'], r['is_click'], r['play_ratio']
        
        item_cnt[vid] += 1; item_lv[vid] += lv; item_clk[vid] += clk; item_pr[vid] += pr
        author_cnt[aid] += 1; author_lv[aid] += lv; author_clk[aid] += clk
        user_tag_cnt[(uid, tag)] += 1; user_tag_lv[(uid, tag)] += lv
        user_author_cnt[(uid, aid)] += 1; user_author_lv[(uid, aid)] += lv

    # Helper to compute target scores
    def get_stats(r):
        vid, aid, tag, uid = r['video_id'], r['author_id'], r['tag'], r['user_id']
        i_n = item_cnt[vid]
        i_lv_r = (item_lv[vid] + 20.0 * g_lv) / (i_n + 20.0)
        i_clk_r = (item_clk[vid] + 20.0 * g_clk) / (i_n + 20.0)
        i_pr_m = (item_pr[vid] + 20.0 * g_pr) / (i_n + 20.0)

        a_n = author_cnt[aid]
        a_lv_r = (author_lv[aid] + 30.0 * g_lv) / (a_n + 30.0)
        
        ut_n = user_tag_cnt[(uid, tag)]
        ut_r = (user_tag_lv[(uid, tag)] + 5.0 * g_lv) / (ut_n + 5.0) if ut_n > 0 else g_lv
        
        ua_n = user_author_cnt[(uid, aid)]
        ua_r = (user_author_lv[(uid, aid)] + 3.0 * i_lv_r) / (ua_n + 3.0) if ua_n > 0 else i_lv_r

        return np.array([i_lv_r, i_clk_r, i_pr_m, a_lv_r, ut_r, ua_r], dtype=np.float32)

    # 4. Build categorical matrix
    fields = ['user_id', 'video_id', 'author_id', 'tag', 'tab', 'hour', 'dow', 'dur_bucket']
    dur_edges = np.quantile([x['duration_ms'] for x in train_rows], np.linspace(0, 1, 11)[1:-1])

    def get_cats(x):
        return [
            x['user_id'], x['video_id'], x['author_id'], x['tag'], x['tab'],
            x['hour'], x['dow'], str(int(np.searchsorted(dur_edges, x['duration_ms'])))
        ]

    n_f = len(fields)
    vocabs = [dict() for _ in range(n_f)]
    for x in train_rows:
        for i, v in enumerate(get_cats(x)):
            if v not in vocabs[i]:
                vocabs[i][v] = len(vocabs[i])

    unk = [len(v) for v in vocabs]
    field_dims = [len(v) + 1 for v in vocabs]
    offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int32)

    def encode_split(rws):
        X = np.empty((len(rws), n_f), dtype=np.int32)
        S = np.empty((len(rws), 6), dtype=np.float32)
        y = np.empty(len(rws), dtype=np.float32)
        u = []
        for j, x in enumerate(rws):
            for i, v in enumerate(get_cats(x)):
                X[j, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            S[j] = get_stats(x)
            y[j] = x['label']
            u.append(x['user_id'])
        return X, S, y, u

    Xtr, Str, ytr, utr = encode_split(train_rows)
    Xva, Sva, yva, uva = encode_split(valid_rows)

    return (Xtr, Str, ytr, utr), (Xva, Sva, yva, uva), int(sum(field_dims))


def train_single_fm(Xtr, ytr, Xva, yva, uva, dim, k=16, lr=0.001, l2=1e-5, bs=8192, max_epochs=35, patience=4, seed=0):
    m = B.FM(dim, k=k, lr=lr, l2=l2, seed=seed)
    rng = np.random.default_rng(seed)
    best = -1.0
    best_state = None
    bad = 0
    for ep in range(1, max_epochs + 1):
        idx = rng.permutation(len(ytr))
        for i in range(0, len(idx), bs):
            m.step(Xtr[idx[i:i + bs]], ytr[idx[i:i + bs]])
        preds = m.predict(Xva)
        va = evaluate(uva, yva, preds)
        if va['primary'] > best + 1e-5:
            best = va['primary']
            bad = 0
            best_state = (m.V.copy(), m.W.copy(), np.float32(m.b))
        else:
            bad += 1
            if bad >= patience:
                break
    m.V, m.W, m.b = best_state
    return m


def run_experiment_suite():
    t0 = time.time()
    (Xtr, Str, ytr, utr), (Xva, Sva, yva, uva), dim = load_dataset_with_stats()
    print(f"Data loaded in {time.time()-t0:.1f}s. Dim: {dim}")

    # 1. Fine-grained L2 search
    print("\n--- 1. Fine-grained L2 Search (Seed 0) ---")
    l2_candidates = [3e-6, 6e-6, 1e-5, 1.5e-5, 2e-5, 3e-5]
    best_l2 = 1e-5
    best_prim = -1.0
    for l2 in l2_candidates:
        m = train_single_fm(Xtr, ytr, Xva, yva, uva, dim, k=16, lr=0.001, l2=l2, seed=0)
        res = evaluate(uva, yva, m.predict(Xva))
        print(f"L2={l2:.1e} | GAUC {res['GAUC']:.4f} | nDCG@5 {res['nDCG@5']:.4f} | primary {res['primary']:.4f}")
        if res['primary'] > best_prim:
            best_prim = res['primary']
            best_l2 = l2

    print(f"\nBest L2: {best_l2:.1e} with primary {best_prim:.4f}")

    # 2. Target Statistics Fusion
    print("\n--- 2. Target Statistics & Affinity Fusion ---")
    m_opt = train_single_fm(Xtr, ytr, Xva, yva, uva, dim, k=16, lr=0.001, l2=best_l2, seed=0)
    fm_raw_preds = m_opt.predict(Xva)
    
    # Sva columns: [0: item_lv_r, 1: item_clk_r, 2: item_pr_m, 3: author_lv_r, 4: user_tag_r, 5: user_author_r]
    # Test linear logit fusion weights
    def logit(p):
        p_c = np.clip(p, 1e-5, 1 - 1e-5)
        return np.log(p_c / (1 - p_c))

    stat_logits = logit(Sva[:, 0])  # item long view logit
    stat_clk_logits = logit(Sva[:, 1])
    stat_ut_logits = logit(Sva[:, 4])
    stat_ua_logits = logit(Sva[:, 5])

    fusion_weights = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5]
    for w in fusion_weights:
        fused = fm_raw_preds + w * stat_logits
        res = evaluate(uva, yva, fused)
        print(f"Fusion weight {w:4.2f} on item LV | GAUC {res['GAUC']:.4f} | nDCG@5 {res['nDCG@5']:.4f} | primary {res['primary']:.4f}")

    # Multi-statistic blend
    for w_i in [0.05, 0.1]:
        for w_ut in [0.02, 0.05]:
            for w_ua in [0.02, 0.05]:
                fused = fm_raw_preds + w_i * stat_logits + w_ut * stat_ut_logits + w_ua * stat_ua_logits
                res = evaluate(uva, yva, fused)
                print(f"Blend w_i={w_i}, w_ut={w_ut}, w_ua={w_ua} | GAUC {res['GAUC']:.4f} | nDCG@5 {res['nDCG@5']:.4f} | primary {res['primary']:.4f}")

    # 3. Multi-Seed Ensemble (5 seeds)
    print("\n--- 3. Multi-Seed Ensemble (5 seeds) ---")
    seeds = [0, 1, 2, 3, 4]
    all_preds = []
    for s in seeds:
        m = train_single_fm(Xtr, ytr, Xva, yva, uva, dim, k=16, lr=0.001, l2=best_l2, seed=s)
        p = m.predict(Xva)
        res = evaluate(uva, yva, p)
        print(f"Seed {s} standalone: GAUC {res['GAUC']:.4f} | nDCG@5 {res['nDCG@5']:.4f} | primary {res['primary']:.4f}")
        all_preds.append(p)

    ens_preds = np.mean(all_preds, axis=0)
    ens_res = evaluate(uva, yva, ens_preds)
    print(f"\n>>> 5-Seed Ensemble FM: GAUC {ens_res['GAUC']:.4f} | nDCG@5 {ens_res['nDCG@5']:.4f} | primary {ens_res['primary']:.4f}")

    # 4. Multi-Seed Ensemble + Target Statistics Fusion
    print("\n--- 4. Multi-Seed Ensemble + Fusion ---")
    for w in [0.05, 0.1, 0.15]:
        fused_ens = ens_preds + w * stat_logits + 0.03 * stat_ut_logits + 0.03 * stat_ua_logits
        res = evaluate(uva, yva, fused_ens)
        print(f"Ensemble + Fusion (w={w:4.2f}) | GAUC {res['GAUC']:.4f} | nDCG@5 {res['nDCG@5']:.4f} | primary {res['primary']:.4f}")


if __name__ == '__main__':
    run_experiment_suite()
