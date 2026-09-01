"""Compute personalized user affinity features and measure predictive power."""

from __future__ import annotations

import csv
import math
import os
import time
from collections import Counter, defaultdict
import numpy as np

from starter_kit.evaluate import evaluate


def run_affinity_analysis():
    data_dir = "competition_data/data"

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

    # 2. Train logs
    train_rows = []
    with open(os.path.join(data_dir, 'log_standard_4_08_to_4_21_pure.csv')) as fh:
        for r in csv.DictReader(fh):
            train_rows.append(r)

    valid_rows = []
    with open(os.path.join(data_dir, 'log_public_4_22_to_4_28_pure.csv')) as fh:
        for r in csv.DictReader(fh):
            valid_rows.append(r)

    print(f"Loaded {len(train_rows)} train rows, {len(valid_rows)} valid rows.")

    # 3. Build user historical affinity profiles
    user_author_cnt = Counter()
    user_author_lv = Counter()
    user_author_clk = Counter()

    user_tag_cnt = Counter()
    user_tag_lv = Counter()

    user_tab_cnt = Counter()
    user_tab_lv = Counter()

    user_pos_durs = defaultdict(list)
    item_lv_cnt = Counter()
    item_imp_cnt = Counter()

    for r in train_rows:
        uid = r['user_id']
        vid = r['video_id']
        meta = vid2meta.get(vid, {})
        aid = meta.get('author_id', 'UNK')
        tag = meta.get('tag', '0')
        tab = r.get('tab', '0')
        lv = 1 if r.get('long_view', '0') != '0' else 0
        clk = 1 if r.get('is_click', '0') != '0' else 0
        dur = float(r.get('duration_ms', 1.0) or 1.0)

        item_imp_cnt[vid] += 1
        item_lv_cnt[vid] += lv

        user_author_cnt[(uid, aid)] += 1
        user_author_lv[(uid, aid)] += lv
        user_author_clk[(uid, aid)] += clk

        user_tag_cnt[(uid, tag)] += 1
        user_tag_lv[(uid, tag)] += lv

        user_tab_cnt[(uid, tab)] += 1
        user_tab_lv[(uid, tab)] += lv

        if lv == 1:
            user_pos_durs[uid].append(dur)

    g_lv = sum(item_lv_cnt.values()) / len(train_rows)
    print(f"Global LV rate: {g_lv:.4f}")

    # Check match statistics on validation set
    valid_author_matches = 0
    valid_tag_matches = 0
    for r in valid_rows:
        uid = r['user_id']
        vid = r['video_id']
        meta = vid2meta.get(vid, {})
        aid = meta.get('author_id', 'UNK')
        tag = meta.get('tag', '0')

        if (uid, aid) in user_author_cnt:
            valid_author_matches += 1
        if (uid, tag) in user_tag_cnt:
            valid_tag_matches += 1

    print(f"Validation interactions where user watched author before: {valid_author_matches}/{len(valid_rows)} ({valid_author_matches/len(valid_rows)*100:.2f}%)")
    print(f"Validation interactions where user watched tag before: {valid_tag_matches}/{len(valid_rows)} ({valid_tag_matches/len(valid_rows)*100:.2f}%)")


if __name__ == '__main__':
    run_affinity_analysis()
