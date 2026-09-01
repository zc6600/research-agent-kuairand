"""DCN-v2: Practical Deep & Cross Network for Web-Scale Recommendation."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class CrossNetworkV2(nn.Module):
    """Vector-based Cross Network v2: x_{l+1} = x_0 * (W_l x_l + b_l) + x_l."""
    def __init__(self, input_dim, num_layers=3):
        super().__init__()
        self.num_layers = num_layers
        self.weights = nn.ParameterList([
            nn.Parameter(torch.empty(input_dim, input_dim)) for _ in range(num_layers)
        ])
        self.biases = nn.ParameterList([
            nn.Parameter(torch.empty(input_dim)) for _ in range(num_layers)
        ])
        for w, b in zip(self.weights, self.biases):
            nn.init.xavier_uniform_(w)
            nn.init.zeros_(b)

    def forward(self, x0):
        xl = x0
        for w, b in zip(self.weights, self.biases):
            # xl: (B, D)
            # W xl + b: (B, D)
            mapped = F.linear(xl, w, b)
            xl = x0 * mapped + xl
        return xl


class DCNv2(nn.Module):
    """DCN-v2 with parallel Cross Network and Deep MLP."""
    def __init__(self, field_dims, embed_dim=32, num_cross_layers=3,
                 mlp_hidden_dims=[256, 128, 64], dropout_rate=0.1):
        super().__init__()
        self.field_dims = field_dims
        self.embed_dim = embed_dim
        self.num_fields = len(field_dims)
        self.total_dim = int(sum(field_dims))

        offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int64)
        self.register_buffer('offsets', torch.from_numpy(offsets).unsqueeze(0))

        # Linear part
        self.linear_emb = nn.Embedding(self.total_dim, 1)
        nn.init.zeros_(self.linear_emb.weight)
        self.bias = nn.Parameter(torch.zeros(1))

        # Field Embeddings
        self.embedding = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.01)

        input_dim = self.num_fields * embed_dim

        # Cross Net
        self.cross_net = CrossNetworkV2(input_dim, num_layers=num_cross_layers)

        # Deep MLP
        mlp_layers = []
        in_d = input_dim
        for h_dim in mlp_hidden_dims:
            mlp_layers.append(nn.Linear(in_d, h_dim))
            mlp_layers.append(nn.LayerNorm(h_dim))
            mlp_layers.append(nn.SiLU())
            if dropout_rate > 0:
                mlp_layers.append(nn.Dropout(dropout_rate))
            in_d = h_dim
        self.mlp = nn.Sequential(*mlp_layers)

        # Combination layer
        self.final_linear = nn.Linear(input_dim + mlp_hidden_dims[-1], 1)

    def forward(self, x):
        x_off = x + self.offsets
        linear = self.linear_emb(x_off).sum(dim=1).squeeze(-1) + self.bias

        emb = self.embedding(x_off)  # (B, num_fields, embed_dim)
        x0 = emb.view(emb.size(0), -1)  # (B, input_dim)

        cross_out = self.cross_net(x0)
        mlp_out = self.mlp(x0)

        comb = torch.cat([cross_out, mlp_out], dim=-1)
        logits = linear + self.final_linear(comb).squeeze(-1)
        return logits
