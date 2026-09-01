"""Unified Tri-Paradigm Ranker: Recency Interval Embeddings + Dual-Polarity Feedback + SENet Recalibration."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from system.models.din import TargetAttention
from system.models.senet_din import SENetLayer


class UnifiedTriRanker(nn.Module):
    """Unified Ranker combining Time-Aware Attention, Pos/Neg Polarity, and SENet dynamic field recalibration."""
    def __init__(self, field_dims, vid_field_idx, auth_field_idx=None, tag_field_idx=None,
                 embed_dim=16, num_time_buckets=16, reduction_ratio=4,
                 mlp_hidden_dims=[256, 128, 64], dropout_rate=0.1):
        super().__init__()
        self.field_dims = field_dims
        self.vid_field_idx = vid_field_idx
        self.auth_field_idx = auth_field_idx
        self.tag_field_idx = tag_field_idx
        self.embed_dim = embed_dim
        self.num_fields = len(field_dims)
        self.total_dim = int(sum(field_dims))

        offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int64)
        self.register_buffer('offsets', torch.from_numpy(offsets).unsqueeze(0))
        self.vid_offset = offsets[vid_field_idx]

        # Linear component
        self.linear_emb = nn.Embedding(self.total_dim, 1)
        nn.init.zeros_(self.linear_emb.weight)
        self.bias = nn.Parameter(torch.zeros(1))

        # Shared Embeddings
        self.embedding = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.01)

        # Time Interval Embedding
        self.time_emb = nn.Embedding(num_time_buckets, embed_dim, padding_idx=0)
        nn.init.normal_(self.time_emb.weight, mean=0.0, std=0.01)

        # SENet field recalibration
        self.senet = SENetLayer(num_fields=self.num_fields, reduction_ratio=reduction_ratio)

        # Attention units
        self.time_vid_attention = TargetAttention(embed_dim)
        self.pos_attention = TargetAttention(embed_dim)
        self.neg_attention = TargetAttention(embed_dim)

        # Polarity projection: [pos, neg, time_vid, pos - neg, pos * neg] -> 3 * embed_dim
        self.polarity_proj = nn.Sequential(
            nn.Linear(5 * embed_dim, 3 * embed_dim),
            nn.LayerNorm(3 * embed_dim),
            nn.SiLU()
        )

        # Deep MLP: input is (num_fields * 2 + 3) * embed_dim
        input_dim = (self.num_fields * 2 + 3) * embed_dim
        mlp_layers = []
        in_d = input_dim
        for h_dim in mlp_hidden_dims:
            mlp_layers.append(nn.Linear(in_d, h_dim))
            mlp_layers.append(nn.LayerNorm(h_dim))
            mlp_layers.append(nn.SiLU())
            if dropout_rate > 0:
                mlp_layers.append(nn.Dropout(dropout_rate))
            in_d = h_dim
        mlp_layers.append(nn.Linear(in_d, 1))
        self.mlp = nn.Sequential(*mlp_layers)

    def forward(self, x, seqs=None, seq_lens=None):
        x_off = x + self.offsets
        linear = self.linear_emb(x_off).sum(dim=1).squeeze(-1) + self.bias
        emb = self.embedding(x_off)  # (B, num_fields, embed_dim)

        # SENet Recalibration
        emb_senet = self.senet(emb)

        cand_vid_emb = emb[:, self.vid_field_idx, :]

        if seqs is not None and seqs.dim() == 3:
            # 0: all vid + 6: time_delta
            s_vid = seqs[:, 0, :] + self.vid_offset
            l_vid = seq_lens[:, 0] if seq_lens is not None else None
            s_vid_emb = self.embedding(s_vid)
            if seqs.size(1) > 6:
                s_time = seqs[:, 6, :]
                s_time_vid_emb = s_vid_emb + self.time_emb(s_time)
            else:
                s_time_vid_emb = s_vid_emb
            u_time_vid = self.time_vid_attention(cand_vid_emb, s_time_vid_emb, l_vid)

            # 3: engaged vid (positive)
            s_pos = seqs[:, 3, :] + self.vid_offset
            l_pos = seq_lens[:, 3] if seq_lens is not None else None
            u_pos = self.pos_attention(cand_vid_emb, self.embedding(s_pos), l_pos)

            # 5: skipped vid (negative)
            s_neg = seqs[:, 5, :] + self.vid_offset
            l_neg = seq_lens[:, 5] if seq_lens is not None else None
            u_neg = self.neg_attention(cand_vid_emb, self.embedding(s_neg), l_neg)

            # Polarity representation
            polarity_raw = torch.cat([
                u_pos,
                u_neg,
                u_time_vid,
                u_pos - u_neg,
                u_pos * u_neg
            ], dim=-1)
            u_polarity = self.polarity_proj(polarity_raw)
        else:
            u_polarity = torch.zeros(emb.size(0), 3 * self.embed_dim, device=emb.device)

        # Dual FM interactions
        sum_v1 = emb.sum(dim=1)
        sum_v1_sq = (emb ** 2).sum(dim=1)
        fm_orig = 0.5 * (sum_v1 ** 2 - sum_v1_sq).sum(dim=-1)

        sum_v2 = emb_senet.sum(dim=1)
        sum_v2_sq = (emb_senet ** 2).sum(dim=1)
        fm_senet = 0.5 * (sum_v2 ** 2 - sum_v2_sq).sum(dim=-1)

        # Deep input
        deep_in = torch.cat([
            emb.view(emb.size(0), -1),
            emb_senet.view(emb_senet.size(0), -1),
            u_polarity
        ], dim=-1)
        deep_out = self.mlp(deep_in).squeeze(-1)

        logits = linear + 0.5 * (fm_orig + fm_senet) + deep_out
        return logits
