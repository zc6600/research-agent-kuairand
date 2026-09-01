"""Factorization Machine (FM) in PyTorch and pure NumPy."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class TorchFM(nn.Module):
    """PyTorch Factorization Machine model with 1st-order linear + 2nd-order interactions."""
    def __init__(self, field_dims, embed_dim=16, l2_reg=1e-6):
        super().__init__()
        self.field_dims = field_dims
        self.embed_dim = embed_dim
        self.num_fields = len(field_dims)
        self.total_dim = int(sum(field_dims))
        
        # Offsets for fast single embedding table lookup
        offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int64)
        self.register_buffer('offsets', torch.from_numpy(offsets).unsqueeze(0))

        # 1st-order linear weights + bias
        self.linear_emb = nn.Embedding(self.total_dim, 1)
        nn.init.zeros_(self.linear_emb.weight)
        self.bias = nn.Parameter(torch.zeros(1))

        # 2nd-order latent factors
        self.latent_emb = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.latent_emb.weight, mean=0.0, std=0.01)

    def forward(self, x):
        """
        x: (Batch, num_fields) int tensor of field indices within each field
        returns: (Batch,) logits
        """
        x_off = x + self.offsets  # (B, num_fields)

        # 1st-order linear
        linear = self.linear_emb(x_off).sum(dim=1).squeeze(-1) + self.bias  # (B,)

        # 2nd-order FM interaction
        v = self.latent_emb(x_off)  # (B, num_fields, embed_dim)
        sum_v = v.sum(dim=1)        # (B, embed_dim)
        sum_v_sq = (v ** 2).sum(dim=1)  # (B, embed_dim)
        fm_interaction = 0.5 * (sum_v ** 2 - sum_v_sq).sum(dim=-1)  # (B,)

        logits = linear + fm_interaction
        return logits
