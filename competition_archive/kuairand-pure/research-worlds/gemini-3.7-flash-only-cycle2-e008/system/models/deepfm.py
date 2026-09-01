"""DeepFM: A Factorization-Machine based Neural Network for CTR/Ranking Prediction."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class DeepFM(nn.Module):
    """DeepFM architecture combining wide linear part, FM 2nd-order interaction, and deep MLP."""
    def __init__(self, field_dims, embed_dim=32, mlp_hidden_dims=[256, 128, 64],
                 dropout_rate=0.1, use_layer_norm=True):
        super().__init__()
        self.field_dims = field_dims
        self.embed_dim = embed_dim
        self.num_fields = len(field_dims)
        self.total_dim = int(sum(field_dims))

        offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int64)
        self.register_buffer('offsets', torch.from_numpy(offsets).unsqueeze(0))

        # 1st-order linear
        self.linear_emb = nn.Embedding(self.total_dim, 1)
        nn.init.zeros_(self.linear_emb.weight)
        self.bias = nn.Parameter(torch.zeros(1))

        # Shared Embedding for FM and Deep
        self.latent_emb = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.latent_emb.weight, mean=0.0, std=0.01)

        # Deep MLP
        input_dim = self.num_fields * embed_dim
        mlp_layers = []
        in_d = input_dim
        for h_dim in mlp_hidden_dims:
            mlp_layers.append(nn.Linear(in_d, h_dim))
            if use_layer_norm:
                mlp_layers.append(nn.LayerNorm(h_dim))
            mlp_layers.append(nn.SiLU())
            if dropout_rate > 0:
                mlp_layers.append(nn.Dropout(dropout_rate))
            in_d = h_dim
        mlp_layers.append(nn.Linear(in_d, 1))
        self.mlp = nn.Sequential(*mlp_layers)

    def forward(self, x):
        """
        x: (Batch, num_fields)
        returns: (Batch,) logits
        """
        x_off = x + self.offsets  # (B, num_fields)

        # 1st-order linear
        linear = self.linear_emb(x_off).sum(dim=1).squeeze(-1) + self.bias

        # 2nd-order FM interaction
        v = self.latent_emb(x_off)  # (B, num_fields, embed_dim)
        sum_v = v.sum(dim=1)
        sum_v_sq = (v ** 2).sum(dim=1)
        fm_out = 0.5 * (sum_v ** 2 - sum_v_sq).sum(dim=-1)

        # Deep part
        deep_in = v.view(v.size(0), -1)  # (B, num_fields * embed_dim)
        deep_out = self.mlp(deep_in).squeeze(-1)

        logits = linear + fm_out + deep_out
        return logits
