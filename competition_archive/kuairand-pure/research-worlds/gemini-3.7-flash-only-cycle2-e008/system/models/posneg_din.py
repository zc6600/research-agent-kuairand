"""Dual-Polarity Deep Negative Feedback Network (PosNeg-DIN) for KuaiRand."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from system.models.din import TargetAttention


class PosNegDINModel(nn.Module):
    """PosNeg-DIN: Models both positive engagement affinity and negative skip/bounce avoidance."""
    def __init__(self, field_dims, vid_field_idx, auth_field_idx=None, tag_field_idx=None,
                 embed_dim=16, mlp_hidden_dims=[256, 128, 64], dropout_rate=0.1):
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

        # Separate attention units for positive, negative, and general sequences
        self.pos_attention = TargetAttention(embed_dim)
        self.neg_attention = TargetAttention(embed_dim)
        self.all_attention = TargetAttention(embed_dim)

        # Polarity projection: takes [pos, neg, all, pos - neg, pos * neg] -> 3 * embed_dim
        self.polarity_proj = nn.Sequential(
            nn.Linear(5 * embed_dim, 3 * embed_dim),
            nn.LayerNorm(3 * embed_dim),
            nn.SiLU()
        )

        # Deep MLP: input is num_fields * embed_dim + 3 * embed_dim
        input_dim = self.num_fields * embed_dim + 3 * embed_dim
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

        cand_vid_emb = emb[:, self.vid_field_idx, :]

        if seqs is not None and seqs.dim() == 3:
            # 0: all vid
            s_all = seqs[:, 0, :] + self.vid_offset
            l_all = seq_lens[:, 0] if seq_lens is not None else None
            u_all = self.all_attention(cand_vid_emb, self.embedding(s_all), l_all)

            # 3: engaged vid (positive)
            s_pos = seqs[:, 3, :] + self.vid_offset
            l_pos = seq_lens[:, 3] if seq_lens is not None else None
            u_pos = self.pos_attention(cand_vid_emb, self.embedding(s_pos), l_pos)

            # 5: skipped vid (negative)
            s_neg = seqs[:, 5, :] + self.vid_offset
            l_neg = seq_lens[:, 5] if seq_lens is not None else None
            u_neg = self.neg_attention(cand_vid_emb, self.embedding(s_neg), l_neg)

            # Combine polarity signals
            polarity_raw = torch.cat([
                u_pos,
                u_neg,
                u_all,
                u_pos - u_neg,
                u_pos * u_neg
            ], dim=-1)
            u_polarity = self.polarity_proj(polarity_raw)
        else:
            u_polarity = torch.zeros(emb.size(0), 3 * self.embed_dim, device=emb.device)

        # FM 2nd-order interaction over tabular fields
        sum_v = emb.sum(dim=1)
        sum_v_sq = (emb ** 2).sum(dim=1)
        fm_out = 0.5 * (sum_v ** 2 - sum_v_sq).sum(dim=-1)

        # Deep input
        deep_in = torch.cat([emb.view(emb.size(0), -1), u_polarity], dim=-1)
        deep_out = self.mlp(deep_in).squeeze(-1)

        logits = linear + fm_out + deep_out
        return logits
