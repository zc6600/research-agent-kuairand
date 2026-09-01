"""KuaiRand-Pure feature engineering and data preprocessing.

Extracts categorical fields, numerical features, leak-free target statistics
(computed strictly on training data), and user historical sequences.
"""

from __future__ import annotations

import csv
import math
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

LABEL = 'long_view'
SPLITS = {
    'train': (20220408, 20220421),
    'valid': (20220422, 20220428),
}

# Categorical field specifications
USER_CAT_FIELDS = [
    'user_id', 'user_active_degree', 'is_live_streamer', 'is_video_author',
    'follow_user_num_range', 'fans_user_num_range', 'friend_user_num_range',
    'register_days_range', 'onehot_feat0', 'onehot_feat1', 'onehot_feat2',
    'onehot_feat3', 'onehot_feat4', 'onehot_feat5', 'onehot_feat6',
    'onehot_feat7', 'onehot_feat8', 'onehot_feat9', 'onehot_feat10',
    'onehot_feat11', 'onehot_feat12', 'onehot_feat13', 'onehot_feat14',
    'onehot_feat15', 'onehot_feat16', 'onehot_feat17'
]

VIDEO_CAT_FIELDS = [
    'video_id', 'author_id', 'video_type', 'upload_type',
    'music_id', 'music_type', 'tag_primary'
]

CONTEXT_CAT_FIELDS = [
    'tab', 'hour', 'day_of_week', 'dur_bucket'
]

ALL_CAT_FIELDS = USER_CAT_FIELDS + VIDEO_CAT_FIELDS + CONTEXT_CAT_FIELDS


class KuaiRandData:
    """Preprocesses and caches all tables and engineered features."""

    def __init__(self, data_dir: str | Path):
        self.data_dir = str(data_dir)
        self.user_features: Dict[str, Dict[str, str]] = {}
        self.video_features: Dict[str, Dict[str, Any]] = {}
        self.train_logs: List[Dict[str, Any]] = []
        self.valid_logs: List[Dict[str, Any]] = []
        
        # Statistics strictly from train
        self.item_stats: Dict[str, Dict[str, float]] = {}
        self.author_stats: Dict[str, Dict[str, float]] = {}
        self.user_stats: Dict[str, Dict[str, float]] = {}
        self.user_author_history: Dict[Tuple[str, str], int] = Counter()
        self.user_tag_history: Dict[Tuple[str, str], List[int]] = defaultdict(list)
        self.user_tab_history: Dict[Tuple[str, str], List[int]] = defaultdict(list)
        
        # Vocabularies
        self.vocabs: Dict[str, Dict[str, int]] = {}
        self.field_dims: List[int] = []
        self.dur_edges: np.ndarray = np.array([])
        
        self._load_metadata()
        self._load_logs()
        self._compute_train_statistics()
        self._build_vocabs()

    def _load_metadata(self):
        # User features
        u_path = os.path.join(self.data_dir, 'user_features_pure.csv')
        if os.path.exists(u_path):
            with open(u_path) as f:
                for r in csv.DictReader(f):
                    self.user_features[r['user_id']] = r

        # Video features
        v_path = os.path.join(self.data_dir, 'video_features_basic_pure.csv')
        if os.path.exists(v_path):
            with open(v_path) as f:
                for r in csv.DictReader(f):
                    tag_str = r.get('tag', '')
                    primary_tag = tag_str.split(',')[0] if tag_str else '0'
                    width = float(r.get('server_width', 0) or 0)
                    height = float(r.get('server_height', 0) or 0)
                    aspect = height / width if width > 0 else 1.0
                    self.video_features[r['video_id']] = {
                        'author_id': r.get('author_id', 'UNK'),
                        'video_type': r.get('video_type', 'UNK'),
                        'upload_type': r.get('upload_type', 'UNK'),
                        'music_id': r.get('music_id', 'UNK'),
                        'music_type': r.get('music_type', 'UNK'),
                        'tag_primary': primary_tag,
                        'tag_all': [t for t in tag_str.split(',') if t] if tag_str else ['0'],
                        'aspect_ratio': aspect,
                    }

    def _load_logs(self):
        train_file = os.path.join(self.data_dir, 'log_standard_4_08_to_4_21_pure.csv')
        with open(train_file) as f:
            for r in csv.DictReader(f):
                self.train_logs.append(self._parse_row(r))

        valid_file = os.path.join(self.data_dir, 'log_public_4_22_to_4_28_pure.csv')
        if not os.path.exists(valid_file):
            valid_file = os.path.join(self.data_dir, 'log_standard_4_22_to_5_08_pure.csv')
        with open(valid_file) as f:
            for r in csv.DictReader(f):
                date = int(r['date'])
                if SPLITS['valid'][0] <= date <= SPLITS['valid'][1]:
                    self.valid_logs.append(self._parse_row(r))

    def _parse_row(self, r: Dict[str, str]) -> Dict[str, Any]:
        dur = float(r['duration_ms']) if r.get('duration_ms') else 1.0
        play = float(r['play_time_ms']) if r.get('play_time_ms') else 0.0
        hour = str(int(r['hourmin']) // 100) if r.get('hourmin') else '0'
        d_int = int(r['date'])
        dow = str((d_int % 100) % 7)
        
        return {
            'date': d_int,
            'user_id': r['user_id'],
            'video_id': r['video_id'],
            'tab': r.get('tab', '0'),
            'hour': hour,
            'day_of_week': dow,
            'duration_ms': dur,
            'play_time_ms': play,
            'play_ratio': min(5.0, play / max(1.0, dur)),
            'long_view': 1 if r.get('long_view', '0') != '0' else 0,
            'is_click': 1 if r.get('is_click', '0') != '0' else 0,
            'is_like': 1 if r.get('is_like', '0') != '0' else 0,
            'is_comment': 1 if r.get('is_comment', '0') != '0' else 0,
            'is_forward': 1 if r.get('is_forward', '0') != '0' else 0,
            'is_follow': 1 if r.get('is_follow', '0') != '0' else 0,
        }

    def _compute_train_statistics(self):
        """Compute Bayesian smoothed statistics strictly on training data."""
        item_lv = Counter(); item_imp = Counter()
        item_clk = Counter(); item_like = Counter()
        item_play = defaultdict(float)
        
        author_lv = Counter(); author_imp = Counter(); author_clk = Counter()
        user_lv = Counter(); user_imp = Counter(); user_clk = Counter()
        user_play = defaultdict(float)

        for r in self.train_logs:
            vid = r['video_id']
            uid = r['user_id']
            vf = self.video_features.get(vid, {})
            aid = vf.get('author_id', 'UNK')
            tag = vf.get('tag_primary', '0')
            tab = r['tab']
            
            lv = r['long_view']
            clk = r['is_click']
            like = r['is_like']
            pr = r['play_ratio']
            
            item_imp[vid] += 1; item_lv[vid] += lv; item_clk[vid] += clk; item_like[vid] += like
            item_play[vid] += pr
            
            author_imp[aid] += 1; author_lv[aid] += lv; author_clk[aid] += clk
            user_imp[uid] += 1; user_lv[uid] += lv; user_clk[uid] += clk
            user_play[uid] += pr
            
            self.user_author_history[(uid, aid)] += 1
            self.user_tag_history[(uid, tag)].append(lv)
            self.user_tab_history[(uid, tab)].append(lv)

        n_train = max(1, len(self.train_logs))
        self.global_lv_mean = sum(item_lv.values()) / n_train
        self.global_clk_mean = sum(item_clk.values()) / n_train
        self.global_like_mean = sum(item_like.values()) / n_train
        self.global_play_mean = sum(item_play.values()) / n_train

        prior_item = 20.0
        for vid, imp in item_imp.items():
            self.item_stats[vid] = {
                'imp_log': math.log1p(imp),
                'lv_rate': (item_lv[vid] + prior_item * self.global_lv_mean) / (imp + prior_item),
                'clk_rate': (item_clk[vid] + prior_item * self.global_clk_mean) / (imp + prior_item),
                'like_rate': (item_like[vid] + prior_item * self.global_like_mean) / (imp + prior_item),
                'play_mean': (item_play[vid] + prior_item * self.global_play_mean) / (imp + prior_item),
            }

        prior_author = 30.0
        for aid, imp in author_imp.items():
            self.author_stats[aid] = {
                'imp_log': math.log1p(imp),
                'lv_rate': (author_lv[aid] + prior_author * self.global_lv_mean) / (imp + prior_author),
                'clk_rate': (author_clk[aid] + prior_author * self.global_clk_mean) / (imp + prior_author),
            }

        prior_user = 10.0
        for uid, imp in user_imp.items():
            self.user_stats[uid] = {
                'imp_log': math.log1p(imp),
                'lv_rate': (user_lv[uid] + prior_user * self.global_lv_mean) / (imp + prior_user),
                'clk_rate': (user_clk[uid] + prior_user * self.global_clk_mean) / (imp + prior_user),
                'play_mean': (user_play[uid] + prior_user * self.global_play_mean) / (imp + prior_user),
            }

    def _build_vocabs(self):
        train_durs = [r['duration_ms'] for r in self.train_logs]
        self.dur_edges = np.quantile(np.asarray(train_durs), np.linspace(0, 1, 21)[1:-1])

        self.vocabs = {f: {} for f in ALL_CAT_FIELDS}
        
        for r in self.train_logs:
            raw_vals = self._extract_raw_cat(r)
            for f, val in raw_vals.items():
                if val not in self.vocabs[f]:
                    self.vocabs[f][val] = len(self.vocabs[f])

        self.field_dims = [len(self.vocabs[f]) + 1 for f in ALL_CAT_FIELDS]  # +1 for UNK
        self.offsets = np.cumsum([0] + self.field_dims[:-1]).astype(np.int64)

    def _extract_raw_cat(self, r: Dict[str, Any]) -> Dict[str, str]:
        uid = r['user_id']
        vid = r['video_id']
        uf = self.user_features.get(uid, {})
        vf = self.video_features.get(vid, {})
        dur_bucket = str(int(np.searchsorted(self.dur_edges, r['duration_ms'])))
        
        res = {
            'user_id': uid,
            'video_id': vid,
            'author_id': vf.get('author_id', 'UNK'),
            'video_type': vf.get('video_type', 'UNK'),
            'upload_type': vf.get('upload_type', 'UNK'),
            'music_id': vf.get('music_id', 'UNK'),
            'music_type': vf.get('music_type', 'UNK'),
            'tag_primary': vf.get('tag_primary', '0'),
            'tab': r['tab'],
            'hour': r['hour'],
            'day_of_week': r['day_of_week'],
            'dur_bucket': dur_bucket,
        }
        for uf_name in USER_CAT_FIELDS:
            if uf_name not in res:
                res[uf_name] = str(uf.get(uf_name, 'UNK'))
        return res

    def extract_features(self, logs: List[Dict[str, Any]]) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[str], Dict[str, torch.Tensor]]:
        """Extract categorical tensor, continuous tensor, label tensor, user list, auxiliary labels."""
        N = len(logs)
        F_cat = len(ALL_CAT_FIELDS)
        F_num = 14  # continuous feature dimension
        
        X_cat = np.empty((N, F_cat), dtype=np.int64)
        X_num = np.empty((N, F_num), dtype=np.float32)
        y = np.empty(N, dtype=np.float32)
        aux_click = np.empty(N, dtype=np.float32)
        aux_play = np.empty(N, dtype=np.float32)
        users = []

        for i, r in enumerate(logs):
            uid = r['user_id']
            vid = r['video_id']
            vf = self.video_features.get(vid, {})
            aid = vf.get('author_id', 'UNK')
            tag = vf.get('tag_primary', '0')
            tab = r['tab']
            
            raw_cats = self._extract_raw_cat(r)
            for j, f in enumerate(ALL_CAT_FIELDS):
                val = raw_cats[f]
                idx = self.vocabs[f].get(val, len(self.vocabs[f]))  # UNK is at end
                X_cat[i, j] = idx + self.offsets[j]
            
            # Continuous & statistical features
            istat = self.item_stats.get(vid, {})
            astat = self.author_stats.get(aid, {})
            ustat = self.user_stats.get(uid, {})
            
            i_imp = istat.get('imp_log', 0.0)
            i_lv = istat.get('lv_rate', self.global_lv_mean)
            i_clk = istat.get('clk_rate', self.global_clk_mean)
            i_like = istat.get('like_rate', self.global_like_mean)
            i_play = istat.get('play_mean', self.global_play_mean)
            
            a_imp = astat.get('imp_log', 0.0)
            a_lv = astat.get('lv_rate', self.global_lv_mean)
            a_clk = astat.get('clk_rate', self.global_clk_mean)
            
            u_imp = ustat.get('imp_log', 0.0)
            u_lv = ustat.get('lv_rate', self.global_lv_mean)
            u_clk = ustat.get('clk_rate', self.global_clk_mean)
            
            u_a_cnt = math.log1p(self.user_author_history.get((uid, aid), 0))
            u_tag_lvs = self.user_tag_history.get((uid, tag), [])
            u_tag_rate = (sum(u_tag_lvs) + 5.0 * self.global_lv_mean) / (len(u_tag_lvs) + 5.0) if u_tag_lvs else self.global_lv_mean
            
            u_tab_lvs = self.user_tab_history.get((uid, tab), [])
            u_tab_rate = (sum(u_tab_lvs) + 5.0 * self.global_lv_mean) / (len(u_tab_lvs) + 5.0) if u_tab_lvs else self.global_lv_mean
            
            X_num[i] = [
                i_imp, i_lv, i_clk, i_like, i_play,
                a_imp, a_lv, a_clk,
                u_imp, u_lv, u_clk,
                u_a_cnt, u_tag_rate, u_tab_rate
            ]
            
            y[i] = r['long_view']
            aux_click[i] = r['is_click']
            aux_play[i] = r['play_ratio']
            users.append(uid)

        aux = {
            'click': torch.from_numpy(aux_click),
            'play_ratio': torch.from_numpy(aux_play)
        }
        return (
            torch.from_numpy(X_cat),
            torch.from_numpy(X_num),
            torch.from_numpy(y),
            users,
            aux
        )
