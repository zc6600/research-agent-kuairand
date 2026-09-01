"""Optimized Trainer using direct PyTorch tensor slicing in memory."""
import os
import sys
import time
import copy
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from system.metrics import evaluate


class Trainer:
    """High-speed Trainer for CTR / Ranking models on KuaiRand."""
    def __init__(
        self,
        model,
        learning_rate=1e-3,
        weight_decay=1e-5,
        batch_size=8192,
        max_epochs=25,
        patience=5,
        device=None,
        task_weights=None,      # For multi-task [1.0, 0.5, 0.2, 0.2, 0.1]
        loss_type='bce',        # 'bce', 'bce_pairwise', 'user_pairwise', 'listnet', 'multitask', 'esmm'
        pairwise_weight=0.1,    # Weight for pairwise/listwise ranking loss
        use_ips=False,          # Whether to apply Inverse Propensity Scoring weights
        verbose=True
    ):
        self.model = model
        self.lr = learning_rate
        self.wd = weight_decay
        self.batch_size = batch_size
        self.max_epochs = max_epochs
        self.patience = patience
        self.loss_type = loss_type
        self.pairwise_weight = pairwise_weight
        self.use_ips = use_ips
        self.task_weights = task_weights if task_weights is not None else [1.0, 0.5, 0.2, 0.2, 0.1]
        self.verbose = verbose

        if device is None:
            self.device = torch.device('cpu')
        else:
            self.device = device
        self.model.to(self.device)

        self.optimizer = optim.AdamW(self.model.parameters(), lr=self.lr, weight_decay=self.wd)
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=self.max_epochs, eta_min=1e-5)
        self.criterion = nn.BCEWithLogitsLoss()

    def _compute_loss(self, logits, yb, all_logits=None, my_b=None, xb=None, ips_b=None):
        if self.loss_type == 'esmm' and all_logits is not None and my_b is not None:
            # all_logits is (ctr_logits, cvr_logits, p_ctr, p_cvr, p_ctcvr)
            ctr_logits, cvr_logits, p_ctr, p_cvr, p_ctcvr = all_logits
            y_long = yb
            y_click = my_b[:, 1]
            loss_ctr = self.criterion(ctr_logits, y_click)
            loss_ctcvr = F.binary_cross_entropy(torch.clamp(p_ctcvr, 1e-7, 1.0 - 1e-7), y_long)
            return loss_ctcvr + 0.5 * loss_ctr

        if self.loss_type == 'multitask' and all_logits is not None and my_b is not None:
            loss = 0.0
            for t_idx, w in enumerate(self.task_weights):
                task_loss = self.criterion(all_logits[:, t_idx], my_b[:, t_idx])
                loss = loss + w * task_loss
            return loss

        if self.use_ips and ips_b is not None:
            raw_bce = F.binary_cross_entropy_with_logits(logits, yb, reduction='none')
            bce_loss = (raw_bce * ips_b).mean()
        else:
            bce_loss = self.criterion(logits, yb)

        if self.loss_type == 'listnet' and xb is not None:
            # Group by user_id in batch
            user_col = xb[:, 0]
            unique_users, counts = torch.unique(user_col, return_counts=True)
            multi_users = unique_users[counts >= 2]
            if len(multi_users) > 0:
                if len(multi_users) > 100:
                    multi_users = multi_users[:100]
                list_losses = []
                for u in multi_users:
                    u_mask = (user_col == u)
                    pos_count = (yb[u_mask] == 1.0).sum()
                    if pos_count > 0:  # Has at least one positive
                        y_u = yb[u_mask]
                        s_u = logits[u_mask]
                        p_true = F.softmax(y_u / 1.0, dim=0)
                        p_pred = F.softmax(s_u / 1.0, dim=0)
                        list_loss = -torch.sum(p_true * torch.log(p_pred + 1e-7))
                        list_losses.append(list_loss)
                if list_losses:
                    total_list_loss = torch.stack(list_losses).mean()
                    return bce_loss + self.pairwise_weight * total_list_loss

        if self.loss_type == 'user_pairwise' and xb is not None:
            # Group by user_id in batch (xb[:, 0] is user_id)
            user_col = xb[:, 0]
            pos_mask = (yb == 1.0)
            neg_mask = (yb == 0.0)
            if pos_mask.any() and neg_mask.any():
                # Find users with both positive and negative impressions
                u_pos = user_col[pos_mask]
                u_neg = user_col[neg_mask]
                common_users = torch.unique(u_pos[torch.isin(u_pos, u_neg)])
                if len(common_users) > 0:
                    pair_losses = []
                    # Limit to at most 100 common users per batch for speed
                    if len(common_users) > 100:
                        common_users = common_users[:100]
                    for u in common_users:
                        u_mask_pos = (user_col == u) & pos_mask
                        u_mask_neg = (user_col == u) & neg_mask
                        pos_s = logits[u_mask_pos]
                        neg_s = logits[u_mask_neg]
                        diff = neg_s.unsqueeze(0) - pos_s.unsqueeze(1)
                        pair_losses.append(F.softplus(diff).mean())
                    if pair_losses:
                        user_pair_loss = torch.stack(pair_losses).mean()
                        return bce_loss + self.pairwise_weight * user_pair_loss

        if self.loss_type == 'bce_pairwise' and self.pairwise_weight > 0:
            pos_mask = (yb == 1.0)
            neg_mask = (yb == 0.0)
            if pos_mask.any() and neg_mask.any():
                pos_s = logits[pos_mask]
                neg_s = logits[neg_mask]
                if len(pos_s) > 1000:
                    pos_s = pos_s[torch.randperm(len(pos_s), device=self.device)[:1000]]
                if len(neg_s) > 1000:
                    neg_s = neg_s[torch.randperm(len(neg_s), device=self.device)[:1000]]
                pair_diff = neg_s.unsqueeze(0) - pos_s.unsqueeze(1)
                pair_loss = F.softplus(pair_diff).mean()
                return bce_loss + self.pairwise_weight * pair_loss
        return bce_loss

    def _train_epoch(self, X, y, multi_y=None, seqs=None, seq_lens=None, ips=None):
        self.model.train()
        N = len(y)
        perm = torch.randperm(N, device=self.device)
        total_loss = 0.0
        n_batches = 0

        is_seq_model = (hasattr(self.model, 'attentions') or hasattr(self.model, 'attention') or hasattr(self.model, 'time_vid_attention') or hasattr(self.model, 'time_attention') or hasattr(self.model, 'pos_attention')) and seqs is not None

        for i in range(0, N, self.batch_size):
            idx = perm[i:i + self.batch_size]
            xb = X[idx]
            yb = y[idx]
            ips_b = ips[idx] if ips is not None else None

            self.optimizer.zero_grad()

            if is_seq_model:
                sb = seqs[idx]
                lb = seq_lens[idx] if seq_lens is not None else None
                out = self.model(xb, sb, lb)
            else:
                out = self.model(xb)

            if isinstance(out, tuple):
                target_logits, all_logits = out
                my_b = multi_y[idx] if multi_y is not None else None
                loss = self._compute_loss(target_logits, yb, all_logits=all_logits, my_b=my_b, xb=xb, ips_b=ips_b)
            else:
                logits = out
                loss = self._compute_loss(logits, yb, xb=xb, ips_b=ips_b)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=5.0)
            self.optimizer.step()

            total_loss += loss.item()
            n_batches += 1

        self.scheduler.step()
        return total_loss / max(1, n_batches)

    @torch.no_grad()
    def predict(self, X, seqs=None, seq_lens=None, batch_size=32768):
        self.model.eval()
        N = len(X)
        scores = []
        is_seq_model = (hasattr(self.model, 'attentions') or hasattr(self.model, 'attention') or hasattr(self.model, 'time_vid_attention') or hasattr(self.model, 'time_attention') or hasattr(self.model, 'pos_attention')) and seqs is not None

        for i in range(0, N, batch_size):
            xb = X[i:i + batch_size].to(self.device)
            if is_seq_model:
                sb = seqs[i:i + batch_size].to(self.device)
                lb = seq_lens[i:i + batch_size].to(self.device) if seq_lens is not None else None
                out = self.model(xb, sb, lb)
            else:
                out = self.model(xb)

            logits = out[0] if isinstance(out, tuple) else out
            probs = torch.sigmoid(logits).cpu().numpy()
            scores.append(probs)

        return np.concatenate(scores)

    def fit(self, train_data, valid_data):
        """
        train_data: (X_tr, y_tr, u_tr, my_tr, [seqs_tr, lens_tr, ips_tr])
        valid_data: (X_va, y_va, u_va, my_va, [seqs_va, lens_va, ips_va])
        """
        X_tr, y_tr, u_tr, my_tr = train_data[:4]
        seqs_tr = train_data[4] if len(train_data) > 4 else None
        lens_tr = train_data[5] if len(train_data) > 5 else None
        ips_tr = train_data[6] if len(train_data) > 6 else None

        X_va, y_va, u_va, my_va = valid_data[:4]
        seqs_va = valid_data[4] if len(valid_data) > 4 else None
        lens_va = valid_data[5] if len(valid_data) > 5 else None

        # Convert to torch tensors in memory
        t_X_tr = torch.from_numpy(np.array(X_tr, copy=True)).long().to(self.device)
        t_y_tr = torch.from_numpy(np.array(y_tr, copy=True)).float().to(self.device)
        t_my_tr = torch.from_numpy(np.array(my_tr, copy=True)).float().to(self.device) if my_tr is not None else None
        t_seqs_tr = torch.from_numpy(np.array(seqs_tr, copy=True)).long().to(self.device) if seqs_tr is not None else None
        t_lens_tr = torch.from_numpy(np.array(lens_tr, copy=True)).long().to(self.device) if lens_tr is not None else None
        t_ips_tr = torch.from_numpy(np.array(ips_tr, copy=True)).float().to(self.device) if (ips_tr is not None and self.use_ips) else None

        t_X_va = torch.from_numpy(np.array(X_va, copy=True)).long()
        t_seqs_va = torch.from_numpy(np.array(seqs_va, copy=True)).long() if seqs_va is not None else None
        t_lens_va = torch.from_numpy(np.array(lens_va, copy=True)).long() if lens_va is not None else None

        best_score = -1.0
        best_state = None
        best_metrics = None
        best_epoch = 0
        patience_count = 0
        history = []

        if self.verbose:
            print(f"Starting training: {len(X_tr):,d} train rows, {len(X_va):,d} valid rows, batch_size={self.batch_size}", flush=True)

        for epoch in range(1, self.max_epochs + 1):
            t0 = time.time()
            train_loss = self._train_epoch(t_X_tr, t_y_tr, t_my_tr, t_seqs_tr, t_lens_tr, t_ips_tr)
            train_time = time.time() - t0

            t1 = time.time()
            val_preds = self.predict(t_X_va, t_seqs_va, t_lens_va)
            val_metrics = evaluate(u_va, y_va, val_preds)
            eval_time = time.time() - t1

            cur_primary = val_metrics['primary']
            cur_gauc = val_metrics['GAUC']
            cur_ndcg = val_metrics['nDCG@5']

            lr = self.optimizer.param_groups[0]['lr']
            epoch_log = (
                f"Epoch {epoch:2d} | Train Loss: {train_loss:.4f} | "
                f"Valid GAUC: {cur_gauc:.4f} | nDCG@5: {cur_ndcg:.4f} | Primary: {cur_primary:.4f} | "
                f"lr: {lr:.1e} | Time: {train_time:.1f}s+{eval_time:.1f}s"
            )
            history.append({
                'epoch': epoch,
                'train_loss': train_loss,
                'GAUC': cur_gauc,
                'nDCG@5': cur_ndcg,
                'primary': cur_primary
            })

            if self.verbose:
                print(epoch_log, flush=True)

            if cur_primary > best_score + 1e-5:
                best_score = cur_primary
                best_epoch = epoch
                best_metrics = val_metrics
                best_state = copy.deepcopy(self.model.state_dict())
                patience_count = 0
            else:
                patience_count += 1
                if patience_count >= self.patience:
                    if self.verbose:
                        print(f"Early stopping at epoch {epoch} (best epoch: {best_epoch}, best primary: {best_score:.4f})", flush=True)
                    break

        if best_state is not None:
            self.model.load_state_dict(best_state)

        final_preds = self.predict(t_X_va, t_seqs_va, t_lens_va)
        final_metrics = evaluate(u_va, y_va, final_preds)

        return {
            'best_epoch': best_epoch,
            'best_metrics': final_metrics,
            'history': history,
            'valid_predictions': final_preds
        }
