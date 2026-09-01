"""Entire Space Multi-Task Model with Deep Interest Network (ESMM-DIN) for KuaiRand."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from system.models.din import TargetAttention


class ESMMDINModel(nn.Module):
    """ESMM-DIN: Entire Space Multi-Task Model modeling P(click) and P(long_view | click) via DIN."""
    def __init__(self, field_dims, vid_field_idx, auth_field_idx=None, tag_field_idx=None,
                 facets=['vid'], embed_dim=16, mlp_hidden_dims=[256, 128, 64], dropout_rate=0.1):
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
        self.auth_offset = offsets[auth_field_idx] if auth_field_idx is not None else None
        self.tag_offset = offsets[tag_field_idx] if tag_field_idx is not None else None

        # Shared Linear
        self.linear_emb = nn.Embedding(self.total_dim, 1)
        nn.init.zeros_(self.linear_emb.weight)
        self.bias = nn.Parameter(torch.zeros(1))

        # Shared Embeddings
        self.embedding = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.01)

        # Multi-facet attention units (Shared)
        self.attentions = nn.ModuleDict()
        for f in self.facets:
            self.attentions[f] = TargetAttention(embed_dim)

        input_dim = (self.num_fields + len(self.facets)) * embed_dim

        # CTR Tower: P(click | x)
        ctr_layers = []
        in_d = input_dim
        for h_dim in mlp_hidden_dims:
            ctr_layers.append(nn.Linear(in_d, h_dim))
            ctr_layers.append(nn.LayerNorm(h_dim))
            ctr_layers.append(nn.SiLU())
            if dropout_rate > 0:
                ctr_layers.append(nn.Dropout(dropout_rate))
            in_d = h_dim
        ctr_layers.append(nn.Linear(in_d, 1))
        self.ctr_mlp = nn.Sequential(*ctr_layers)

        # CVR Tower: P(long_view | click, x)
        cvr_layers = []
        in_d = input_dim
        for h_dim in mlp_hidden_dims:
            cvr_layers.append(nn.Linear(in_d, h_dim))
            cvr_layers.append(nn.LayerNorm(h_dim))
            cvr_layers.append(nn.SiLU())
            if dropout_rate > 0:
                cvr_layers.append(nn.Dropout(dropout_rate))
            in_d = h_dim
        cvr_layers.append(nn.Linear(in_d, 1))
        self.cvr_mlp = nn.Sequential(*cvr_layers)

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

        # FM 2nd-order interaction
        sum_v = emb.sum(dim=1)
        sum_v_sq = (emb ** 2).sum(dim=1)
        fm_out = 0.5 * (sum_v ** 2 - sum_v_sq).sum(dim=-1)

        # Deep input
        deep_in = torch.cat([emb.view(emb.size(0), -1)] + interest_list, dim=-1)
        ctr_logits = linear + fm_out + self.ctr_mlp(deep_in).squeeze(-1)
        cvr_logits = linear + fm_out + self.cvr_mlp(deep_in).squeeze(-1)

        # During training/evaluation:
        # P(click) = sigmoid(ctr_logits)
        # P(cvr) = sigmoid(cvr_logits)
        # P(ctcvr) = P(click) * P(cvr)
        # We can return (ctcvr_score, (ctr_logits, cvr_logits))
        p_ctr = torch.sigmoid(ctr_logits)
        p_cvr = torch.sigmoid(cvr_logits)
        p_ctcvr = p_ctr * p_cvr

        # Compute equivalent logit for ctcvr: log(p / (1 - p + eps))
        ctcvr_logits = torch.logit(torch.clamp(p_ctcvr, min=1e-7, max=1.0 - 1e-7))

        return ctcvr_logits, (ctr_logits, cvr_logits, p_ctr, p_cvr, p_ctcvr)
