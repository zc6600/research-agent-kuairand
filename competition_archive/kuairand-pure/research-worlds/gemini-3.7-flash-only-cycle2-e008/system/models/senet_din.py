"""Squeeze-and-Excitation Network (SENet-DIN / FiBiNET) with Dynamic Field Recalibration."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from system.models.din import TargetAttention


class SENetLayer(nn.Module):
    """Squeeze-and-Excitation field recalibration module for tabular embeddings."""
    def __init__(self, num_fields, reduction_ratio=4):
        super().__init__()
        self.num_fields = num_fields
        reduced_dim = max(1, num_fields // reduction_ratio)
        self.excitation = nn.Sequential(
            nn.Linear(num_fields, reduced_dim),
            nn.SiLU(),
            nn.Linear(reduced_dim, num_fields),
            nn.Sigmoid()
        )

    def forward(self, emb):
        """
        emb: (B, num_fields, embed_dim)
        returns: (B, num_fields, embed_dim) recalibrated embeddings
        """
        # Squeeze: average pooling across embedding dimension
        z = emb.mean(dim=-1)  # (B, num_fields)
        # Excitation: field importance weights
        a = self.excitation(z).unsqueeze(-1)  # (B, num_fields, 1)
        # Recalibrate
        emb_recalibrated = emb * a
        return emb_recalibrated


class SENetDINModel(nn.Module):
    """SENet-DIN: Combines dynamic field-importance recalibration with sequential Target Attention."""
    def __init__(self, field_dims, vid_field_idx, auth_field_idx=None, tag_field_idx=None,
                 facets=['vid'], embed_dim=16, reduction_ratio=4,
                 mlp_hidden_dims=[256, 128, 64], dropout_rate=0.1):
        super().__init__()
        self.field_dims = field_dims
        self.vid_field_idx = vid_field_idx
        self.auth_field_idx = auth_field_idx
        self.tag_field_idx = tag_field_idx
        self.facets = facets
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

        # SENet Recalibration module
        self.senet = SENetLayer(num_fields=self.num_fields, reduction_ratio=reduction_ratio)

        # Target Attention
        self.attention = TargetAttention(embed_dim)

        # Deep MLP: input is (num_fields * 2 + 1) * embed_dim (original + recalibrated + seq_int)
        input_dim = (self.num_fields * 2 + 1) * embed_dim
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

        # Squeeze-and-Excitation Recalibration
        emb_senet = self.senet(emb)  # (B, num_fields, embed_dim)

        cand_vid_emb = emb[:, self.vid_field_idx, :]

        if seqs is not None:
            is_3d = (seqs.dim() == 3)
            s_vid = (seqs[:, 0, :] if is_3d else seqs) + self.vid_offset
            l_vid = (seq_lens[:, 0] if (is_3d and seq_lens is not None) else seq_lens)
            s_emb = self.embedding(s_vid)
            u_int = self.attention(cand_vid_emb, s_emb, l_vid)
        else:
            u_int = torch.zeros_like(cand_vid_emb)

        # Dual FM 2nd-order interactions (original + recalibrated)
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
            u_int
        ], dim=-1)
        deep_out = self.mlp(deep_in).squeeze(-1)

        logits = linear + 0.5 * (fm_orig + fm_senet) + deep_out
        return logits
