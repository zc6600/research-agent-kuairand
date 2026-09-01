"""Multi-Task Learning Architectures (Shared-Bottom and MMoE) for KuaiRand."""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class MMoE(nn.Module):
    """Multi-gate Mixture-of-Experts module."""
    def __init__(self, input_dim, num_experts=4, expert_hidden_dim=128, num_tasks=5):
        super().__init__()
        self.num_experts = num_experts
        self.num_tasks = num_tasks

        # Experts
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(input_dim, expert_hidden_dim),
                nn.LayerNorm(expert_hidden_dim),
                nn.SiLU(),
                nn.Linear(expert_hidden_dim, expert_hidden_dim)
            ) for _ in range(num_experts)
        ])

        # Task Gates
        self.gates = nn.ModuleList([
            nn.Linear(input_dim, num_experts) for _ in range(num_tasks)
        ])

    def forward(self, x):
        # x: (B, input_dim)
        expert_outputs = torch.stack([exp(x) for exp in self.experts], dim=1)  # (B, num_experts, expert_dim)
        
        task_representations = []
        for g in self.gates:
            gate_weights = F.softmax(g(x), dim=-1).unsqueeze(-1)  # (B, num_experts, 1)
            task_rep = (expert_outputs * gate_weights).sum(dim=1)  # (B, expert_dim)
            task_representations.append(task_rep)

        return task_representations


class MultiTaskRankingModel(nn.Module):
    """Multi-task recommendation model combining Shared FM embeddings, MMoE experts, and task heads."""
    def __init__(self, field_dims, embed_dim=32, num_experts=4, expert_hidden_dim=128,
                 task_hidden_dims=[64, 32], num_tasks=5, dropout_rate=0.1):
        super().__init__()
        self.field_dims = field_dims
        self.embed_dim = embed_dim
        self.num_fields = len(field_dims)
        self.total_dim = int(sum(field_dims))
        self.num_tasks = num_tasks

        offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int64)
        self.register_buffer('offsets', torch.from_numpy(offsets).unsqueeze(0))

        # Linear
        self.linear_emb = nn.Embedding(self.total_dim, 1)
        nn.init.zeros_(self.linear_emb.weight)
        self.bias = nn.Parameter(torch.zeros(1))

        # Embeddings
        self.embedding = nn.Embedding(self.total_dim, embed_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.01)

        input_dim = self.num_fields * embed_dim

        # MMoE module
        self.mmoe = MMoE(input_dim, num_experts=num_experts, expert_hidden_dim=expert_hidden_dim, num_tasks=num_tasks)

        # Task-specific Towers
        self.task_towers = nn.ModuleList()
        for _ in range(num_tasks):
            t_layers = []
            in_d = expert_hidden_dim
            for h in task_hidden_dims:
                t_layers.append(nn.Linear(in_d, h))
                t_layers.append(nn.LayerNorm(h))
                t_layers.append(nn.SiLU())
                if dropout_rate > 0:
                    t_layers.append(nn.Dropout(dropout_rate))
                in_d = h
            t_layers.append(nn.Linear(in_d, 1))
            self.task_towers.append(nn.Sequential(*t_layers))

    def forward(self, x):
        """
        x: (B, num_fields)
        returns:
          target_logit: (B,) logit for long_view
          all_logits: (B, num_tasks) logits for all tasks
        """
        x_off = x + self.offsets
        linear = self.linear_emb(x_off).sum(dim=1).squeeze(-1) + self.bias

        emb = self.embedding(x_off)  # (B, num_fields, embed_dim)
        
        # FM 2nd order
        sum_v = emb.sum(dim=1)
        sum_v_sq = (emb ** 2).sum(dim=1)
        fm_out = 0.5 * (sum_v ** 2 - sum_v_sq).sum(dim=-1)

        # MMoE inputs
        flat_emb = emb.view(emb.size(0), -1)
        task_reps = self.mmoe(flat_emb)  # list of (B, expert_dim)

        task_logits = []
        for i, (rep, tower) in enumerate(zip(task_reps, self.task_towers)):
            out = tower(rep).squeeze(-1)
            # Add linear and FM interaction to target task
            if i == 0:
                out = out + linear + fm_out
            task_logits.append(out)

        stacked_logits = torch.stack(task_logits, dim=-1)  # (B, num_tasks)
        return stacked_logits[:, 0], stacked_logits
