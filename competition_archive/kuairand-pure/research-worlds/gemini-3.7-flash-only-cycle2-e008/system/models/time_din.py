"""Time-Aware Deep Interest Network (Time-DIN) with Recency Interval Embeddings."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from system.models.din import TargetAttention


class TimeDINModel(nn.Module):
    """Time-Aware Deep Interest Network attending over temporal recency and semantic similarity."""
    def __init__(self, field_dims, vid_field_idx, auth_field_idx=None, tag_field_idx=None,
                 embed_dim=16, num_time_buckets=16, mlp_hidden_dims=[256, 128, 64], dropout_rate=0.1):
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

        # Time Interval Bucket Embedding: 16 buckets (0=pad, 1..15=intervals)
        self.time_emb = nn.Embedding(num_time_buckets, embed_dim, padding_idx=0)
        nn.init.normal_(self.time_emb.weight, mean=0.0, std=0.01)

        # Target Attention units
        self.time_attention = TargetAttention(embed_dim)
        self.eng_attention = TargetAttention(embed_dim)

        # Deep MLP: input is (num_fields + 2) * embed_dim (time_vid_interest + eng_vid_interest)
        input_dim = (self.num_fields + 2) * embed_dim
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
        """
        x: (B, num_fields)
        seqs: (B, NUM_FACETS, S)
        seq_lens: (B, NUM_FACETS)
        """
        x_off = x + self.offsets
        linear = self.linear_emb(x_off).sum(dim=1).squeeze(-1) + self.bias
        emb = self.embedding(x_off)  # (B, num_fields, embed_dim)

        cand_vid_emb = emb[:, self.vid_field_idx, :]

        if seqs is not None:
            is_3d = (seqs.dim() == 3)
            # Facet 0: all video sequence
            s_vid = (seqs[:, 0, :] if is_3d else seqs) + self.vid_offset
            l_vid = (seq_lens[:, 0] if (is_3d and seq_lens is not None) else seq_lens)
            s_vid_emb = self.embedding(s_vid)  # (B, S, D)

            # Facet 6: time_delta buckets
            if is_3d and seqs.size(1) > 6:
                s_time = seqs[:, 6, :]  # (B, S)
                t_emb = self.time_emb(s_time)  # (B, S, D)
                s_time_vid_emb = s_vid_emb + t_emb
            else:
                s_time_vid_emb = s_vid_emb

            u_time_int = self.time_attention(cand_vid_emb, s_time_vid_emb, l_vid)

            # Facet 3: engaged video sequence
            if is_3d and seqs.size(1) > 3:
                s_eng = seqs[:, 3, :] + self.vid_offset
                l_eng = seq_lens[:, 3] if seq_lens is not None else None
                s_eng_emb = self.embedding(s_eng)
                u_eng_int = self.eng_attention(cand_vid_emb, s_eng_emb, l_eng)
            else:
                u_eng_int = torch.zeros_like(cand_vid_emb)
        else:
            u_time_int = torch.zeros_like(cand_vid_emb)
            u_eng_int = torch.zeros_like(cand_vid_emb)

        # FM 2nd-order interaction over tabular fields
        sum_v = emb.sum(dim=1)
        sum_v_sq = (emb ** 2).sum(dim=1)
        fm_out = 0.5 * (sum_v ** 2 - sum_v_sq).sum(dim=-1)

        # Deep input
        deep_in = torch.cat([emb.view(emb.size(0), -1), u_time_int, u_eng_int], dim=-1)
        deep_out = self.mlp(deep_in).squeeze(-1)

        logits = linear + fm_out + deep_out
        return logits
