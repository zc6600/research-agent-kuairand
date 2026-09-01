"""Neural ranking architectures for KuaiRand-Pure.

Includes:
1. PyTorchFM: Fast, vectorized Factorization Machine.
2. DeepFM: Wide + FM 2nd-order + Deep MLP with LayerNorm/GELU/Dropout.
3. DCNv2: Deep & Cross Network v2 (Explicit Cross Network + Deep MLP).
4. MultiTaskDeepFM: Shared backbone with multi-task heads (long_view, click, play_ratio).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class FMInteraction(nn.Module):
    """Vectorized 2nd-order FM interaction layer."""

    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        # embeddings shape: (batch_size, num_fields, embed_dim)
        sum_emb = torch.sum(embeddings, dim=1)  # (B, D)
        sum_sq = torch.sum(embeddings ** 2, dim=1)  # (B, D)
        sq_sum = sum_emb ** 2  # (B, D)
        output = 0.5 * torch.sum(sq_sum - sum_sq, dim=1, keepdim=True)  # (B, 1)
        return output


class CrossNetworkV2(nn.Module):
    """DCN-v2 Explicit Cross Network."""

    def __init__(self, in_features: int, num_layers: int = 3, low_rank: int = 32):
        super().__init__()
        self.num_layers = num_layers
        self.U = nn.ParameterList([
            nn.Parameter(torch.randn(in_features, low_rank) / math.sqrt(in_features))
            for _ in range(num_layers)
        ])
        self.V = nn.ParameterList([
            nn.Parameter(torch.randn(low_rank, in_features) / math.sqrt(low_rank))
            for _ in range(num_layers)
        ])
        self.bias = nn.ParameterList([
            nn.Parameter(torch.zeros(in_features))
            for _ in range(num_layers)
        ])

    def forward(self, x0: torch.Tensor) -> torch.Tensor:
        # x0: (B, in_features)
        xl = x0
        for u, v, b in zip(self.U, self.V, self.bias):
            # low rank projection: x0 * (U (V xl)) + b + xl
            proj = torch.matmul(xl, v.t())  # (B, low_rank)
            proj = torch.matmul(proj, u.t())  # (B, in_features)
            xl = x0 * (proj + b) + xl
        return xl


class DeepFM(nn.Module):
    """DeepFM architecture with dense feature integration."""

    def __init__(
        self,
        total_vocab_size: int,
        num_cat_fields: int,
        num_dense_features: int = 14,
        embed_dim: int = 16,
        mlp_hidden_dims: Tuple[int, ...] = (256, 128, 64),
        dropout: float = 0.1,
        use_layernorm: bool = True,
    ):
        super().__init__()
        self.num_cat_fields = num_cat_fields
        self.num_dense_features = num_dense_features
        self.embed_dim = embed_dim

        # 1st-order linear embeddings for categorical fields
        self.linear_cat = nn.Embedding(total_vocab_size, 1)
        nn.init.zeros_(self.linear_cat.weight)
        
        # 1st-order linear weights for dense features
        self.linear_dense = nn.Linear(num_dense_features, 1, bias=False)
        nn.init.zeros_(self.linear_dense.weight)
        
        self.bias = nn.Parameter(torch.zeros(1))

        # 2nd-order embeddings for categorical fields
        self.embedding = nn.Embedding(total_vocab_size, embed_dim)
        nn.init.normal_(self.embedding.weight, std=0.01)

        # Projection for dense features into embedding space
        self.dense_proj = nn.Sequential(
            nn.Linear(num_dense_features, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU()
        )

        self.fm_interaction = FMInteraction()

        # Deep MLP
        total_in_dim = (num_cat_fields + 1) * embed_dim
        layers = []
        in_dim = total_in_dim
        for hidden_dim in mlp_hidden_dims:
            layers.append(nn.Linear(in_dim, hidden_dim))
            if use_layernorm:
                layers.append(nn.LayerNorm(hidden_dim))
            layers.append(nn.GELU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            in_dim = hidden_dim
        layers.append(nn.Linear(in_dim, 1))
        self.mlp = nn.Sequential(*layers)

    def forward(self, x_cat: torch.Tensor, x_num: torch.Tensor) -> torch.Tensor:
        # Linear part
        lin_cat = self.linear_cat(x_cat).sum(dim=1)  # (B, 1)
        lin_num = self.linear_dense(x_num)  # (B, 1)
        linear_out = self.bias + lin_cat + lin_num

        # FM part
        cat_emb = self.embedding(x_cat)  # (B, F_cat, D)
        num_emb = self.dense_proj(x_num).unsqueeze(1)  # (B, 1, D)
        all_emb = torch.cat([cat_emb, num_emb], dim=1)  # (B, F_cat + 1, D)
        fm_out = self.fm_interaction(all_emb)  # (B, 1)

        # MLP part
        flat_emb = all_emb.view(all_emb.size(0), -1)  # (B, (F_cat+1)*D)
        mlp_out = self.mlp(flat_emb)  # (B, 1)

        logits = linear_out + fm_out + mlp_out
        return logits.squeeze(-1)


class MultiTaskDeepFM(nn.Module):
    """Multi-task DeepFM predicting long_view, click, and play_ratio."""

    def __init__(
        self,
        total_vocab_size: int,
        num_cat_fields: int,
        num_dense_features: int = 14,
        embed_dim: int = 16,
        mlp_hidden_dims: Tuple[int, ...] = (256, 128),
        tower_hidden_dims: Tuple[int, ...] = (64, 32),
        dropout: float = 0.1,
    ):
        super().__init__()
        self.num_cat_fields = num_cat_fields
        self.embed_dim = embed_dim

        # Linear weights
        self.linear_cat = nn.Embedding(total_vocab_size, 1)
        self.linear_dense = nn.Linear(num_dense_features, 1, bias=False)
        self.bias = nn.Parameter(torch.zeros(1))

        # Embeddings
        self.embedding = nn.Embedding(total_vocab_size, embed_dim)
        nn.init.normal_(self.embedding.weight, std=0.01)

        self.dense_proj = nn.Sequential(
            nn.Linear(num_dense_features, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU()
        )

        self.fm_interaction = FMInteraction()

        # Shared representation backbone
        total_in_dim = (num_cat_fields + 1) * embed_dim
        layers = []
        in_dim = total_in_dim
        for hidden_dim in mlp_hidden_dims:
            layers.append(nn.Linear(in_dim, hidden_dim))
            layers.append(nn.LayerNorm(hidden_dim))
            layers.append(nn.GELU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            in_dim = hidden_dim
        self.shared_backbone = nn.Sequential(*layers)

        # Task 1: Long view tower (target)
        self.tower_long_view = nn.Sequential(
            nn.Linear(in_dim, tower_hidden_dims[0]),
            nn.LayerNorm(tower_hidden_dims[0]),
            nn.GELU(),
            nn.Linear(tower_hidden_dims[0], 1)
        )

        # Task 2: Click tower (auxiliary classification)
        self.tower_click = nn.Sequential(
            nn.Linear(in_dim, tower_hidden_dims[0]),
            nn.LayerNorm(tower_hidden_dims[0]),
            nn.GELU(),
            nn.Linear(tower_hidden_dims[0], 1)
        )

        # Task 3: Play ratio tower (auxiliary regression)
        self.tower_play = nn.Sequential(
            nn.Linear(in_dim, tower_hidden_dims[0]),
            nn.LayerNorm(tower_hidden_dims[0]),
            nn.GELU(),
            nn.Linear(tower_hidden_dims[0], 1)
        )

    def forward(self, x_cat: torch.Tensor, x_num: torch.Tensor) -> Dict[str, torch.Tensor]:
        # Linear & FM
        lin_cat = self.linear_cat(x_cat).sum(dim=1)
        lin_num = self.linear_dense(x_num)
        linear_out = self.bias + lin_cat + lin_num

        cat_emb = self.embedding(x_cat)
        num_emb = self.dense_proj(x_num).unsqueeze(1)
        all_emb = torch.cat([cat_emb, num_emb], dim=1)
        fm_out = self.fm_interaction(all_emb)

        # Shared features
        flat_emb = all_emb.view(all_emb.size(0), -1)
        shared_feat = self.shared_backbone(flat_emb)

        lv_logits = linear_out + fm_out + self.tower_long_view(shared_feat)
        click_logits = self.tower_click(shared_feat)
        play_preds = self.tower_play(shared_feat)

        return {
            'long_view': lv_logits.squeeze(-1),
            'click': click_logits.squeeze(-1),
            'play_ratio': play_preds.squeeze(-1)
        }


class DCNv2DeepFM(nn.Module):
    """Hybrid DCN-v2 + DeepFM architecture."""

    def __init__(
        self,
        total_vocab_size: int,
        num_cat_fields: int,
        num_dense_features: int = 14,
        embed_dim: int = 20,
        cross_layers: int = 3,
        mlp_hidden_dims: Tuple[int, ...] = (256, 128, 64),
        dropout: float = 0.1,
    ):
        super().__init__()
        self.num_cat_fields = num_cat_fields
        self.embed_dim = embed_dim

        self.linear_cat = nn.Embedding(total_vocab_size, 1)
        self.linear_dense = nn.Linear(num_dense_features, 1, bias=False)
        self.bias = nn.Parameter(torch.zeros(1))

        self.embedding = nn.Embedding(total_vocab_size, embed_dim)
        nn.init.normal_(self.embedding.weight, std=0.01)

        self.dense_proj = nn.Sequential(
            nn.Linear(num_dense_features, embed_dim),
            nn.LayerNorm(embed_dim),
            nn.GELU()
        )

        self.fm_interaction = FMInteraction()

        total_in_dim = (num_cat_fields + 1) * embed_dim
        self.cross_net = CrossNetworkV2(total_in_dim, num_layers=cross_layers, low_rank=32)

        layers = []
        in_dim = total_in_dim
        for hidden_dim in mlp_hidden_dims:
            layers.append(nn.Linear(in_dim, hidden_dim))
            layers.append(nn.LayerNorm(hidden_dim))
            layers.append(nn.GELU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            in_dim = hidden_dim
        self.mlp = nn.Sequential(*layers)

        self.out_proj = nn.Linear(total_in_dim + in_dim, 1)

    def forward(self, x_cat: torch.Tensor, x_num: torch.Tensor) -> torch.Tensor:
        lin_cat = self.linear_cat(x_cat).sum(dim=1)
        lin_num = self.linear_dense(x_num)
        linear_out = self.bias + lin_cat + lin_num

        cat_emb = self.embedding(x_cat)
        num_emb = self.dense_proj(x_num).unsqueeze(1)
        all_emb = torch.cat([cat_emb, num_emb], dim=1)
        fm_out = self.fm_interaction(all_emb)

        flat_emb = all_emb.view(all_emb.size(0), -1)
        cross_out = self.cross_net(flat_emb)
        mlp_out = self.mlp(flat_emb)

        combined = torch.cat([cross_out, mlp_out], dim=1)
        deep_out = self.out_proj(combined)

        logits = linear_out + fm_out + deep_out
        return logits.squeeze(-1)
