"""High-signal feature engineering and model experiments for KuaiRand-Pure."""

from __future__ import annotations

import csv
import math
import os
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from starter_kit.evaluate import evaluate


class HighSignalFeatures:
    """Builds clean, high-signal, leak-free features for KuaiRand-Pure."""

    def __init__(self, data_dir: str = "competition_data/data"):
        self.data_dir = data_dir
        self.load_data()
        self.compute_train_priors()

    def load_data(self):
        # 1. Video features
        self.vid2meta = {}
        v_path = os.path.join(self.data_dir, 'video_features_basic_pure.csv')
        if os.path.exists(v_path):
            with open(v_path) as f:
                for r in csv.DictReader(f):
                    tag_str = r.get('tag', '')
                    primary_tag = tag_str.split(',')[0] if tag_str else '0'
                    self.vid2meta[r['video_id']] = {
                        'author_id': r.get('author_id', 'UNK'),
                        'video_type': r.get('video_type', 'UNK'),
                        'upload_type': r.get('upload_type', 'UNK'),
                        'tag': primary_tag,
                    }

        # 2. Logs
        self.train_rows = []
        with open(os.path.join(self.data_dir, 'log_standard_4_08_to_4_21_pure.csv')) as f:
            for r in csv.DictReader(f):
                self.train_rows.append(self._parse_row(r))

        valid_file = os.path.join(self.data_dir, 'log_public_4_22_to_4_28_pure.csv')
        if not os.path.exists(valid_file):
            valid_file = os.path.join(self.data_dir, 'log_standard_4_22_to_5_08_pure.csv')
        self.valid_rows = []
        with open(valid_file) as f:
            for r in csv.DictReader(f):
                date = int(r['date'])
                if 20220422 <= date <= 20220428:
                    self.valid_rows.append(self._parse_row(r))

    def _parse_row(self, r: Dict[str, str]) -> Dict[str, Any]:
        vid = r['video_id']
        meta = self.vid2meta.get(vid, {})
        dur = float(r['duration_ms']) if r.get('duration_ms') else 1.0
        play = float(r['play_time_ms']) if r.get('play_time_ms') else 0.0
        return {
            'date': int(r['date']),
            'user_id': r['user_id'],
            'video_id': vid,
            'author_id': meta.get('author_id', 'UNK'),
            'tag': meta.get('tag', '0'),
            'tab': r.get('tab', '0'),
            'duration_ms': dur,
            'play_time_ms': play,
            'play_ratio': min(5.0, play / max(1.0, dur)),
            'long_view': 1 if r.get('long_view', '0') != '0' else 0,
            'is_click': 1 if r.get('is_click', '0') != '0' else 0,
            'is_like': 1 if r.get('is_like', '0') != '0' else 0,
        }

    def compute_train_priors(self):
        # Global stats
        n_tr = len(self.train_rows)
        tr_lvs = [r['long_view'] for r in self.train_rows]
        tr_clks = [r['is_click'] for r in self.train_rows]
        tr_likes = [r['is_like'] for r in self.train_rows]
        tr_prs = [r['play_ratio'] for r in self.train_rows]
        
        self.g_lv = sum(tr_lvs) / n_tr
        self.g_clk = sum(tr_clks) / n_tr
        self.g_like = sum(tr_likes) / n_tr
        self.g_pr = sum(tr_prs) / n_tr

        # Item stats
        self.item_cnt = Counter()
        self.item_lv = Counter()
        self.item_clk = Counter()
        self.item_like = Counter()
        self.item_pr = defaultdict(float)

        # Author stats
        self.author_cnt = Counter()
        self.author_lv = Counter()
        self.author_clk = Counter()

        # User stats & affinities
        self.user_cnt = Counter()
        self.user_lv = Counter()
        self.user_clk = Counter()
        self.user_dur = defaultdict(float)

        self.user_author_cnt = Counter()
        self.user_author_lv = Counter()
        self.user_tag_cnt = Counter()
        self.user_tag_lv = Counter()
        self.user_tab_cnt = Counter()
        self.user_tab_lv = Counter()

        for r in self.train_rows:
            uid = r['user_id']
            vid = r['video_id']
            aid = r['author_id']
            tag = r['tag']
            tab = r['tab']
            lv = r['long_view']
            clk = r['is_click']
            like = r['is_like']
            pr = r['play_ratio']
            dur = r['duration_ms']

            self.item_cnt[vid] += 1
            self.item_lv[vid] += lv
            self.item_clk[vid] += clk
            self.item_like[vid] += like
            self.item_pr[vid] += pr

            self.author_cnt[aid] += 1
            self.author_lv[aid] += lv
            self.author_clk[aid] += clk

            self.user_cnt[uid] += 1
            self.user_lv[uid] += lv
            self.user_clk[uid] += clk
            self.user_dur[uid] += dur

            self.user_author_cnt[(uid, aid)] += 1
            self.user_author_lv[(uid, aid)] += lv
            self.user_tag_cnt[(uid, tag)] += 1
            self.user_tag_lv[(uid, tag)] += lv
            self.user_tab_cnt[(uid, tab)] += 1
            self.user_tab_lv[(uid, tab)] += lv

        # Quantile edges for video duration
        durs = [r['duration_ms'] for r in self.train_rows]
        self.dur_edges = np.quantile(np.asarray(durs), np.linspace(0, 1, 11)[1:-1])

    def get_feature_vector(self, r: Dict[str, Any]) -> Tuple[List[str], List[float]]:
        uid = r['user_id']
        vid = r['video_id']
        aid = r['author_id']
        tag = r['tag']
        tab = r['tab']
        dur = r['duration_ms']
        dur_b = str(int(np.searchsorted(self.dur_edges, dur)))

        # Categorical fields (6 high-signal fields)
        cats = [uid, vid, aid, tag, tab, dur_b]

        # Continuous target statistics (smooth Bayesian estimates)
        p_item = 20.0
        i_n = self.item_cnt[vid]
        i_lv_rate = (self.item_lv[vid] + p_item * self.g_lv) / (i_n + p_item)
        i_clk_rate = (self.item_clk[vid] + p_item * self.g_clk) / (i_n + p_item)
        i_like_rate = (self.item_like[vid] + p_item * self.g_like) / (i_n + p_item)
        i_pr_mean = (self.item_pr[vid] + p_item * self.g_pr) / (i_n + p_item)
        i_log_cnt = math.log1p(i_n)

        p_author = 30.0
        a_n = self.author_cnt[aid]
        a_lv_rate = (self.author_lv[aid] + p_author * self.g_lv) / (a_n + p_author)
        a_clk_rate = (self.author_clk[aid] + p_author * self.g_clk) / (a_n + p_author)
        a_log_cnt = math.log1p(a_n)

        # Personalized user affinity
        ua_n = self.user_author_cnt[(uid, aid)]
        ua_lv = self.user_author_lv[(uid, aid)]
        ua_rate = (ua_lv + 3.0 * i_lv_rate) / (ua_n + 3.0) if ua_n > 0 else i_lv_rate
        ua_watched = 1.0 if ua_n > 0 else 0.0

        utag_n = self.user_tag_cnt[(uid, tag)]
        utag_lv = self.user_tag_lv[(uid, tag)]
        utag_rate = (utag_lv + 5.0 * self.g_lv) / (utag_n + 5.0) if utag_n > 0 else self.g_lv

        utab_n = self.user_tab_cnt[(uid, tab)]
        utab_lv = self.user_tab_lv[(uid, tab)]
        utab_rate = (utab_lv + 5.0 * self.g_lv) / (utab_n + 5.0) if utab_n > 0 else self.g_lv

        # Duration match with user typical watch duration
        u_n = self.user_cnt[uid]
        u_avg_dur = self.user_dur[uid] / u_n if u_n > 0 else dur
        dur_ratio = dur / max(100.0, u_avg_dur)
        log_dur_ratio = math.log(max(0.01, min(100.0, dur_ratio)))

        nums = [
            i_log_cnt, i_lv_rate, i_clk_rate, i_like_rate, i_pr_mean,
            a_log_cnt, a_lv_rate, a_clk_rate,
            ua_watched, ua_rate, utag_rate, utab_rate, log_dur_ratio
        ]
        return cats, nums
