"""Behavior Sequence Transformer (BST) with Self-Attention and Target Attention for KuaiRand."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from system.models.din import TargetAttention


class BSTTransformerBlock(nn.Module):
    """Transformer Encoder block with Multi-Head Self-Attention, LayerNorm, and FFN."""
    def __init__(self, embed_dim=16, num_heads=2, ffn_dim=64, dropout_rate=0.1):
        super().__init__()
        self.mha = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout_rate, batch_first=True)
        self.norm1 = nn.LayerNorm(embed_dim)
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, ffn_dim),
            nn.SiLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(ffn_dim, embed_dim)
        )
        self.norm2 = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(dropout_rate)

    def forward(self, seq_emb, lengths=None):
        """
        seq_emb: (B, S, D)
        lengths: (B,)
        """
        B, S, D = seq_emb.shape
        if lengths is not None:
            # key_padding_mask: True where padding
            # To avoid NaNs when lengths == 0, make sure at least the first position is unmasked,
            # then zero out the final result for zero-length sequences.
            safe_lengths = torch.clamp(lengths, min=1)
            key_padding_mask = torch.arange(S, device=seq_emb.device).unsqueeze(0) >= safe_lengths.unsqueeze(1)
            attn_out, _ = self.mha(seq_emb, seq_emb, seq_emb, key_padding_mask=key_padding_mask)
            # Mask out padding in attention output
            valid_mask = (torch.arange(S, device=seq_emb.device).unsqueeze(0) < lengths.unsqueeze(1)).unsqueeze(-1)
            attn_out = attn_out.masked_fill(~valid_mask, 0.0)
        else:
            attn_out, _ = self.mha(seq_emb, seq_emb, seq_emb)

        x = self.norm1(seq_emb + self.dropout(attn_out))
        ffn_out = self.ffn(x)
        if lengths is not None:
            ffn_out = ffn_out.masked_fill(~valid_mask, 0.0)
        out = self.norm2(x + self.dropout(ffn_out))
        if lengths is not None:
            out = out * valid_mask.float()
        return out


class BSTModel(nn.Module):
    """Behavior Sequence Transformer (BST) combining Self-Attention with Target Attention."""
    def __init__(self, field_dims, vid_field_idx, auth_field_idx=None, tag_field_idx=None,
                 facets=['vid'], embed_dim=16, max_seq_len=20, num_heads=2, ffn_dim=64,
                 num_transformer_layers=1, mlp_hidden_dims=[256, 128, 64], dropout_rate=0.1):
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

        # Positional Embeddings for Sequence: (max_seq_len, embed_dim)
        self.pos_emb = nn.Parameter(torch.empty(max_seq_len, embed_dim))
        nn.init.normal_(self.pos_emb, mean=0.0, std=0.02)

        # Linear component
        self.linear_emb = nn.Embedding(self.total_dim, 1)
        nn.init.zeros_(self.linear_emb.weight)
        self.bias = nn.Parameter(torch.zeros(1))

        # Shared Embeddings
        self.embedding = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.01)

        # Transformer blocks for sequence facets
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

        # Deep MLP
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

                # Sequence embedding + positional embedding
                s_emb = self.embedding(s)  # (B, S, D)
                S = s_emb.size(1)
                s_emb = s_emb + self.pos_emb[:S].unsqueeze(0)

                # Pass through Transformer Self-Attention blocks
                h_seq = s_emb
                for block in tf_blocks:
                    h_seq = block(h_seq, lengths=l)

                # Target Attention over transformed sequence representations
                u_int = attn_unit(q, h_seq, l)
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
