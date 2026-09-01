"""Training loop, loss objectives, and evaluation harness."""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader

from starter_kit.evaluate import evaluate


class RankingLoss(nn.Module):
    """Combines Pointwise BCE with within-batch Pairwise BPR Ranking Loss."""

    def __init__(self, pair_weight: float = 0.5, bce_weight: float = 1.0):
        super().__init__()
        self.pair_weight = pair_weight
        self.bce_weight = bce_weight
        self.bce = nn.BCEWithLogitsLoss()

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        loss = self.bce_weight * self.bce(logits, targets)
        
        if self.pair_weight > 0:
            pos_mask = (targets > 0.5)
            neg_mask = (targets < 0.5)
            pos_logits = logits[pos_mask]
            neg_logits = logits[neg_mask]
            
            if len(pos_logits) > 0 and len(neg_logits) > 0:
                # Sample or broadcast pairs
                n_pairs = min(len(pos_logits), len(neg_logits), 2048)
                p_sample = pos_logits[:n_pairs]
                n_sample = neg_logits[:n_pairs]
                pair_loss = -torch.mean(F.logsigmoid(p_sample - n_sample))
                loss = loss + self.pair_weight * pair_loss

        return loss


def evaluate_model(
    model: nn.Module,
    X_cat: torch.Tensor,
    X_num: torch.Tensor,
    y: torch.Tensor,
    users: List[str],
    device: torch.device,
    batch_size: int = 65536,
) -> Dict[str, Union[float, int]]:
    """Generate predictions and compute official metrics."""
    model.eval()
    all_scores = []
    
    with torch.no_grad():
        for i in range(0, len(y), batch_size):
            x_c = X_cat[i:i + batch_size].to(device)
            x_n = X_num[i:i + batch_size].to(device)
            out = model(x_c, x_n)
            if isinstance(out, dict):
                logits = out['long_view']
            else:
                logits = out
            scores = torch.sigmoid(logits).cpu().numpy()
            all_scores.append(scores)

    scores_flat = np.concatenate(all_scores) if all_scores else np.array([])
    labels = y.numpy().tolist()
    return evaluate(users, labels, scores_flat.tolist())


def train_model(
    model: nn.Module,
    X_cat_tr: torch.Tensor,
    X_num_tr: torch.Tensor,
    y_tr: torch.Tensor,
    X_cat_va: torch.Tensor,
    X_num_va: torch.Tensor,
    y_va: torch.Tensor,
    u_va: List[str],
    aux_tr: Optional[Dict[str, torch.Tensor]] = None,
    epochs: int = 15,
    batch_size: int = 4096,
    lr: float = 1e-3,
    weight_decay: float = 1e-5,
    pair_weight: float = 0.2,
    patience: int = 4,
    device: Optional[torch.device] = None,
    verbose: bool = True,
) -> Tuple[Dict[str, Union[float, int]], Dict[str, torch.Tensor]]:
    """Train neural ranking model with cosine lr schedule and validation tracking."""
    if device is None:
        device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    model.to(device)
    
    # Dataset preparation
    tensors = [X_cat_tr, X_num_tr, y_tr]
    is_multitask = aux_tr is not None and isinstance(model, nn.Module) and hasattr(model, 'tower_click')
    if is_multitask:
        tensors.extend([aux_tr['click'], aux_tr['play_ratio']])

    dataset = TensorDataset(*tensors)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs * len(loader), eta_min=1e-5)
    
    criterion = RankingLoss(pair_weight=pair_weight)
    bce_click = nn.BCEWithLogitsLoss()
    mse_play = nn.SmoothL1Loss()

    best_primary = -1.0
    best_metrics = {}
    best_state = None
    bad_epochs = 0

    for ep in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        n_batches = 0
        t0 = time.time()

        for batch in loader:
            x_c = batch[0].to(device)
            x_n = batch[1].to(device)
            y_b = batch[2].to(device)

            optimizer.zero_grad()

            if is_multitask:
                clk_b = batch[3].to(device)
                play_b = batch[4].to(device)
                out = model(x_c, x_n)
                loss_lv = criterion(out['long_view'], y_b)
                loss_clk = bce_click(out['click'], clk_b)
                loss_play = mse_play(out['play_ratio'], play_b)
                loss = loss_lv + 0.3 * loss_clk + 0.1 * loss_play
            else:
                logits = model(x_c, x_n)
                loss = criterion(logits, y_b)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()
            scheduler.step()

            total_loss += loss.item()
            n_batches += 1

        avg_loss = total_loss / max(1, n_batches)
        va_metrics = evaluate_model(model, X_cat_va, X_num_va, y_va, u_va, device)
        elapsed = time.time() - t0

        if verbose:
            print(f"Epoch {ep:2d} | loss {avg_loss:.4f} | valid GAUC {va_metrics['GAUC']:.4f} "
                  f"nDCG@5 {va_metrics['nDCG@5']:.4f} primary {va_metrics['primary']:.4f} | {elapsed:.1f}s")

        if va_metrics['primary'] > best_primary + 1e-5:
            best_primary = float(va_metrics['primary'])
            best_metrics = va_metrics
            bad_epochs = 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad_epochs += 1
            if bad_epochs >= patience:
                if verbose:
                    print(f"Early stopping at epoch {ep} (best primary: {best_primary:.4f})")
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    return best_metrics, best_state
