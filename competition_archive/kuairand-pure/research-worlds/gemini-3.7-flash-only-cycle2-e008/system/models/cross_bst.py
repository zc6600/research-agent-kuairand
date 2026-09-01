"""Cross-BST: Hybrid DCN-v2 Explicit Multiplicative Crossing with Behavior Sequence Transformer."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from system.models.bst import BSTTransformerBlock
from system.models.cross_din import CrossNetwork
from system.models.din import TargetAttention


class CrossBSTModel(nn.Module):
    """Cross-BST: DCN-v2 explicit multiplicative crossings combined with Transformer-encoded sequence dynamics."""
    def __init__(self, field_dims, vid_field_idx, auth_field_idx=None, tag_field_idx=None,
                 facets=['vid'], embed_dim=16, max_seq_len=20, num_heads=2, ffn_dim=64,
                 num_transformer_layers=1, num_cross_layers=3, mlp_hidden_dims=[256, 128, 64],
                 dropout_rate=0.1):
        super().__init__()
        self.field_dims = field_dims
        self.vid_field_idx = vid_field_idx
        self.auth_field_idx = auth_field_idx
        self.tag_field_idx = tag_field_idx
        self.facets = facets
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len
        self.num_fields = len(field_dims)
        self.total_dim = int(sum(field_dims))

        offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int64)
        self.register_buffer('offsets', torch.from_numpy(offsets).unsqueeze(0))
        self.vid_offset = offsets[vid_field_idx]
        self.auth_offset = offsets[auth_field_idx] if auth_field_idx is not None else None
        self.tag_offset = offsets[tag_field_idx] if tag_field_idx is not None else None

        # Positional Embeddings
        self.pos_emb = nn.Parameter(torch.empty(max_seq_len, embed_dim))
        nn.init.normal_(self.pos_emb, mean=0.0, std=0.02)

        # Linear
        self.linear_emb = nn.Embedding(self.total_dim, 1)
        nn.init.zeros_(self.linear_emb.weight)
        self.bias = nn.Parameter(torch.zeros(1))

        # Shared Embeddings
        self.embedding = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.01)

        # Transformer blocks
        self.transformers = nn.ModuleDict()
        for f in self.facets:
            self.transformers[f] = nn.ModuleList([
                BSTTransformerBlock(embed_dim=embed_dim, num_heads=num_heads, ffn_dim=ffn_dim, dropout_rate=dropout_rate)
                for _ in range(num_transformer_layers)
            ])

        # Target Attention units
        self.attentions = nn.ModuleDict()
        for f in self.facets:
            self.attentions[f] = TargetAttention(embed_dim)

        input_dim = (self.num_fields + len(self.facets)) * embed_dim

        # Cross Network
        self.cross_net = CrossNetwork(input_dim, num_layers=num_cross_layers)
        self.cross_linear = nn.Linear(input_dim, 1)

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
        mlp_layers.append(nn.Linear(in_d, 1))
        self.mlp = nn.Sequential(*mlp_layers)

    def forward(self, x, seqs=None, seq_lens=None):
        x_off = x + self.offsets
        linear = self.linear_emb(x_off).sum(dim=1).squeeze(-1) + self.bias
        emb = self.embedding(x_off)  # (B, num_fields, embed_dim)

        cand_vid_emb = emb[:, self.vid_field_idx, :]
        cand_auth_emb = emb[:, self.auth_field_idx, :] if self.auth_field_idx is not None else None
        cand_tag_emb = emb[:, self.tag_field_idx, :] if self.tag_field_idx is not None else None

        interest_list = []
        if seqs is not None:
            is_3d = (seqs.dim() == 3)
            for f in self.facets:
                attn_unit = self.attentions[f]
                tf_blocks = self.transformers[f]
                if f == 'vid':
                    q = cand_vid_emb
                    s = (seqs[:, 0, :] if is_3d else seqs) + self.vid_offset
                    l = (seq_lens[:, 0] if (is_3d and seq_lens is not None) else seq_lens)
                elif f == 'auth':
                    q = cand_auth_emb if cand_auth_emb is not None else cand_vid_emb
                    s = (seqs[:, 1, :] if is_3d else seqs) + (self.auth_offset if self.auth_offset is not None else 0)
                    l = (seq_lens[:, 1] if (is_3d and seq_lens is not None) else seq_lens)
                elif f == 'tag':
                    q = cand_tag_emb if cand_tag_emb is not None else cand_vid_emb
                    s = (seqs[:, 2, :] if is_3d else seqs) + (self.tag_offset if self.tag_offset is not None else 0)
                    l = (seq_lens[:, 2] if (is_3d and seq_lens is not None) else seq_lens)
                elif f == 'eng_vid':
                    q = cand_vid_emb
                    s = (seqs[:, 3, :] if is_3d else seqs) + self.vid_offset
                    l = (seq_lens[:, 3] if (is_3d and seq_lens is not None) else seq_lens)
                elif f == 'eng_auth':
                    q = cand_auth_emb if cand_auth_emb is not None else cand_vid_emb
                    s = (seqs[:, 4, :] if is_3d else seqs) + (self.auth_offset if self.auth_offset is not None else 0)
                    l = (seq_lens[:, 4] if (is_3d and seq_lens is not None) else seq_lens)
                else:
                    raise ValueError(f"Unknown facet: {f}")

                s_emb = self.embedding(s)
                S = s_emb.size(1)
                s_emb = s_emb + self.pos_emb[:S].unsqueeze(0)

                h_seq = s_emb
                for block in tf_blocks:
                    h_seq = block(h_seq, lengths=l)

                u_int = attn_unit(q, h_seq, l)
                interest_list.append(u_int)
        else:
            for _ in self.facets:
                interest_list.append(torch.zeros_like(cand_vid_emb))

        # FM 2nd-order interaction over tabular fields
        sum_v = emb.sum(dim=1)
        sum_v_sq = (emb ** 2).sum(dim=1)
        fm_out = 0.5 * (sum_v ** 2 - sum_v_sq).sum(dim=-1)

        # Cross and Deep input
        x0 = torch.cat([emb.view(emb.size(0), -1)] + interest_list, dim=-1)
        cross_out = self.cross_linear(self.cross_net(x0)).squeeze(-1)
        deep_out = self.mlp(x0).squeeze(-1)

        logits = linear + fm_out + cross_out + deep_out
        return logits
