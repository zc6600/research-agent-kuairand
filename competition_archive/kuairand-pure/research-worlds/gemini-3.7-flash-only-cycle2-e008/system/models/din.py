"""Deep Interest Network (DIN) with Multi-Facet Target Attention and Dual-Sequence modeling."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class TargetAttention(nn.Module):
    """Target Attention module: attends over user historical item sequence using target item."""
    def __init__(self, embed_dim, hidden_units=[64, 32]):
        super().__init__()
        # Input to attention MLP is [query, key, query - key, query * key] -> 4 * embed_dim
        in_dim = 4 * embed_dim
        layers = []
        for h in hidden_units:
            layers.append(nn.Linear(in_dim, h))
            layers.append(nn.SiLU())
            in_dim = h
        layers.append(nn.Linear(in_dim, 1))
        self.mlp = nn.Sequential(*layers)

    def forward(self, query, keys, lengths=None):
        """
        query: (B, embed_dim)
        keys: (B, seq_len, embed_dim)
        lengths: (B,)
        returns: (B, embed_dim) user interest representation
        """
        B, S, D = keys.shape
        q_expanded = query.unsqueeze(1).expand(B, S, D)  # (B, S, D)

        # Concatenate features
        att_in = torch.cat([q_expanded, keys, q_expanded - keys, q_expanded * keys], dim=-1)  # (B, S, 4D)
        scores = self.mlp(att_in).squeeze(-1)  # (B, S)

        # Mask padding
        if lengths is not None:
            mask = torch.arange(S, device=keys.device).unsqueeze(0) < lengths.unsqueeze(1)  # (B, S)
            scores = scores.masked_fill(~mask, -1e9)

        weights = F.softmax(scores, dim=-1)  # (B, S)
        # Handle all masked (lengths == 0)
        weights = weights.nan_to_num(0.0)
        if lengths is not None:
            weights = weights * mask.float()

        # Weighted sum
        user_interest = torch.bmm(weights.unsqueeze(1), keys).squeeze(1)  # (B, D)
        return user_interest


class DINModel(nn.Module):
    """Full DIN architecture supporting single-facet and multi-facet target attention."""
    def __init__(self, field_dims, vid_field_idx, auth_field_idx=None, tag_field_idx=None,
                 facets=['vid'], embed_dim=16, mlp_hidden_dims=[256, 128, 64], dropout_rate=0.1):
        super().__init__()
        self.field_dims = field_dims
        self.vid_field_idx = vid_field_idx
        self.auth_field_idx = auth_field_idx
        self.tag_field_idx = tag_field_idx
        self.facets = facets  # list of facet names: 'vid', 'auth', 'tag', 'eng_vid', 'eng_auth'
        self.embed_dim = embed_dim
        self.num_fields = len(field_dims)
        self.total_dim = int(sum(field_dims))

        offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int64)
        self.register_buffer('offsets', torch.from_numpy(offsets).unsqueeze(0))
        self.vid_offset = offsets[vid_field_idx]
        self.auth_offset = offsets[auth_field_idx] if auth_field_idx is not None else None
        self.tag_offset = offsets[tag_field_idx] if tag_field_idx is not None else None

        # Linear component
        self.linear_emb = nn.Embedding(self.total_dim, 1)
        nn.init.zeros_(self.linear_emb.weight)
        self.bias = nn.Parameter(torch.zeros(1))

        # Shared Embeddings
        self.embedding = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.01)

        # Multi-facet attention units
        self.attentions = nn.ModuleDict()
        for f in self.facets:
            self.attentions[f] = TargetAttention(embed_dim)

        # Deep MLP: input is (num_fields + len(facets)) * embed_dim
        input_dim = (self.num_fields + len(self.facets)) * embed_dim
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
        seqs: (B, S) or (B, num_facets, S)
        seq_lens: (B,) or (B, num_facets)
        """
        x_off = x + self.offsets
        linear = self.linear_emb(x_off).sum(dim=1).squeeze(-1) + self.bias
        emb = self.embedding(x_off)  # (B, num_fields, embed_dim)

        cand_vid_emb = emb[:, self.vid_field_idx, :]
        cand_auth_emb = emb[:, self.auth_field_idx, :] if self.auth_field_idx is not None else None
        cand_tag_emb = emb[:, self.tag_field_idx, :] if self.tag_field_idx is not None else None

        interest_list = []
        if seqs is not None:
            # Check 2D vs 3D sequence
            is_3d = (seqs.dim() == 3)
            for f in self.facets:
                attn_unit = self.attentions[f]
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
                u_int = attn_unit(q, s_emb, l)
                interest_list.append(u_int)
        else:
            for _ in self.facets:
                interest_list.append(torch.zeros_like(cand_vid_emb))

        # FM 2nd-order interaction over tabular fields
        sum_v = emb.sum(dim=1)
        sum_v_sq = (emb ** 2).sum(dim=1)
        fm_out = 0.5 * (sum_v ** 2 - sum_v_sq).sum(dim=-1)

        # Deep input
        deep_in = torch.cat([emb.view(emb.size(0), -1)] + interest_list, dim=-1)
        deep_out = self.mlp(deep_in).squeeze(-1)

        logits = linear + fm_out + deep_out
        return logits
