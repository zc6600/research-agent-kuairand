"""Multi-Task Multi-gate Mixture-of-Experts with Target Attention (MMoE-DIN)."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from system.models.din import TargetAttention


class MultiTaskDINModel(nn.Module):
    """MMoE architecture combined with Multi-Facet Target Attention."""
    def __init__(self, field_dims, vid_field_idx, auth_field_idx=None, tag_field_idx=None,
                 facets=['vid', 'auth', 'eng_vid'], embed_dim=16, num_experts=4,
                 expert_hidden_dim=128, task_hidden_dims=[64, 32], num_tasks=5,
                 dropout_rate=0.1):
        super().__init__()
        self.field_dims = field_dims
        self.vid_field_idx = vid_field_idx
        self.auth_field_idx = auth_field_idx
        self.tag_field_idx = tag_field_idx
        self.facets = facets
        self.embed_dim = embed_dim
        self.num_fields = len(field_dims)
        self.total_dim = int(sum(field_dims))
        self.num_experts = num_experts
        self.num_tasks = num_tasks

        offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int64)
        self.register_buffer('offsets', torch.from_numpy(offsets).unsqueeze(0))
        self.vid_offset = offsets[vid_field_idx]
        self.auth_offset = offsets[auth_field_idx] if auth_field_idx is not None else None
        self.tag_offset = offsets[tag_field_idx] if tag_field_idx is not None else None

        # Shared Embeddings
        self.embedding = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.01)

        # Multi-facet attention units
        self.attentions = nn.ModuleDict()
        for f in self.facets:
            self.attentions[f] = TargetAttention(embed_dim)

        input_dim = (self.num_fields + len(self.facets)) * embed_dim

        # Shared Experts
        self.experts = nn.ModuleList()
        for _ in range(num_experts):
            self.experts.append(nn.Sequential(
                nn.Linear(input_dim, expert_hidden_dim),
                nn.LayerNorm(expert_hidden_dim),
                nn.SiLU(),
                nn.Dropout(dropout_rate) if dropout_rate > 0 else nn.Identity(),
                nn.Linear(expert_hidden_dim, expert_hidden_dim),
                nn.LayerNorm(expert_hidden_dim),
                nn.SiLU()
            ))

        # Task Gates
        self.gates = nn.ModuleList([
            nn.Linear(input_dim, num_experts) for _ in range(num_tasks)
        ])

        # Task Prediction Towers
        self.task_towers = nn.ModuleList()
        for _ in range(num_tasks):
            t_layers = []
            in_d = expert_hidden_dim
            for h in task_hidden_dims:
                t_layers.append(nn.Linear(in_d, h))
                t_layers.append(nn.LayerNorm(h))
                t_layers.append(nn.SiLU())
                in_d = h
            t_layers.append(nn.Linear(in_d, 1))
            self.task_towers.append(nn.Sequential(*t_layers))

    def forward(self, x, seqs=None, seq_lens=None):
        x_off = x + self.offsets
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

        x_in = torch.cat([emb.view(emb.size(0), -1)] + interest_list, dim=-1)

        # Expert outputs: (B, num_experts, expert_hidden_dim)
        expert_outs = [exp(x_in).unsqueeze(1) for exp in self.experts]
        expert_tensor = torch.cat(expert_outs, dim=1)

        task_logits = []
        for t in range(self.num_tasks):
            gate_w = F.softmax(self.gates[t](x_in), dim=-1).unsqueeze(-1)  # (B, num_experts, 1)
            task_repr = torch.sum(gate_w * expert_tensor, dim=1)  # (B, expert_hidden_dim)
            t_logit = self.task_towers[t](task_repr).squeeze(-1)
            task_logits.append(t_logit)

        all_logits = torch.stack(task_logits, dim=-1)
        target_logit = task_logits[0]  # long_view is index 0
        return target_logit, all_logits
