"""Experiment runner and orchestration script for KuaiRand recommendation ranking."""
import os
import sys
import time
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch

from system.data import load_and_preprocess
from system.metrics import evaluate
from system.models.fm import TorchFM
from system.models.deepfm import DeepFM
from system.models.dcn import DCNv2
from system.models.din import DINModel
from system.models.cross_din import CrossDINModel
from system.models.mmoe_din import MultiTaskDINModel
from system.models.multitask import MultiTaskRankingModel
from system.models.bst import BSTModel
from system.models.cross_bst import CrossBSTModel
from system.models.esmm_din import ESMMDINModel
from system.models.mha_din import MHADINModel
from system.models.time_din import TimeDINModel
from system.models.posneg_din import PosNegDINModel
from system.models.senet_din import SENetDINModel
from system.models.time_posneg_senet import UnifiedTriRanker
from system.trainer import Trainer

OFFICIAL_BASELINE = {
    'GAUC': 0.6674,
    'nDCG@5': 0.5357,
    'primary': 0.6016
}


def set_seed(seed=42):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def run_experiment(exp_id, model_name='din', mode='extended', embed_dim=16,
                   lr=3e-4, batch_size=8192, max_epochs=20, patience=5,
                   seed=42, loss_type='bce', pairwise_weight=0.1, use_ips=False,
                   facets=None, task_weights=None, extra_params=None, log_file=None):
    set_seed(seed)
    
    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)

    log(f"================================================================================")
    log(f"EXPERIMENT {exp_id}: Model={model_name.upper()}, FeatureMode={mode}, Seed={seed}, Loss={loss_type}")
    log(f"Config: embed_dim={embed_dim}, lr={lr}, batch_size={batch_size}, max_epochs={max_epochs}, patience={patience}")
    log(f"================================================================================")

    t0 = time.time()
    data = load_and_preprocess('competition_data/data', mode=mode)
    log(f"Data loaded in {data['load_time']:.2f}s | num_fields={data['num_fields']} | total_dim={data['total_dim']:,d}")

    field_dims = data['field_dims']
    feature_names = data['feature_names']
    vid_idx = feature_names.index('video_id')
    auth_idx = feature_names.index('author_id') if 'author_id' in feature_names else None
    tag_idx = feature_names.index('tag_first') if 'tag_first' in feature_names else None

    # Facet configuration for sequence models
    if facets is None:
        facets = ['vid']
    elif isinstance(facets, str):
        if facets == 'vid':
            facets = ['vid']
        elif facets == 'dual_vid':
            facets = ['vid', 'eng_vid']
        elif facets == 'vid_auth':
            facets = ['vid', 'auth']
        elif facets == 'multi':
            facets = ['vid', 'auth', 'tag']
        elif facets == 'dual_seq':
            facets = ['vid', 'auth', 'eng_vid', 'eng_auth']
        elif facets == 'all':
            facets = ['vid', 'auth', 'tag', 'eng_vid', 'eng_auth']

    # Model instantiation
    hidden_dims = extra_params.get('hidden_dims', [256, 128, 64]) if extra_params else [256, 128, 64]
    dropout = extra_params.get('dropout', 0.1) if extra_params else 0.1

    if model_name == 'fm':
        model = TorchFM(field_dims=field_dims, embed_dim=embed_dim)
    elif model_name == 'deepfm':
        model = DeepFM(field_dims=field_dims, embed_dim=embed_dim, mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'dcn':
        num_cross = extra_params.get('num_cross_layers', 3) if extra_params else 3
        model = DCNv2(field_dims=field_dims, embed_dim=embed_dim, num_cross_layers=num_cross,
                      mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'din':
        model = DINModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                         tag_field_idx=tag_idx, facets=facets, embed_dim=embed_dim,
                         mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'cross_din':
        num_cross = extra_params.get('num_cross_layers', 3) if extra_params else 3
        model = CrossDINModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                              tag_field_idx=tag_idx, facets=facets, embed_dim=embed_dim,
                              num_cross_layers=num_cross, mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'mmoe_din':
        loss_type = 'multitask'
        num_experts = extra_params.get('num_experts', 4) if extra_params else 4
        expert_dim = extra_params.get('expert_dim', 128) if extra_params else 128
        task_dims = extra_params.get('task_dims', [64, 32]) if extra_params else [64, 32]
        model = MultiTaskDINModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                                  tag_field_idx=tag_idx, facets=facets, embed_dim=embed_dim,
                                  num_experts=num_experts, expert_hidden_dim=expert_dim,
                                  task_hidden_dims=task_dims, dropout_rate=dropout)
    elif model_name == 'bst':
        num_heads = extra_params.get('num_heads', 2) if extra_params else 2
        ffn_dim = extra_params.get('ffn_dim', 64) if extra_params else 64
        num_tf = extra_params.get('num_transformer_layers', 1) if extra_params else 1
        model = BSTModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                         tag_field_idx=tag_idx, facets=facets, embed_dim=embed_dim,
                         num_heads=num_heads, ffn_dim=ffn_dim, num_transformer_layers=num_tf,
                         mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'cross_bst':
        num_heads = extra_params.get('num_heads', 2) if extra_params else 2
        ffn_dim = extra_params.get('ffn_dim', 64) if extra_params else 64
        num_tf = extra_params.get('num_transformer_layers', 1) if extra_params else 1
        num_cross = extra_params.get('num_cross_layers', 3) if extra_params else 3
        model = CrossBSTModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                              tag_field_idx=tag_idx, facets=facets, embed_dim=embed_dim,
                              num_heads=num_heads, ffn_dim=ffn_dim, num_transformer_layers=num_tf,
                              num_cross_layers=num_cross, mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'esmm_din':
        loss_type = 'esmm'
        model = ESMMDINModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                             tag_field_idx=tag_idx, facets=facets, embed_dim=embed_dim,
                             mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'mha_din':
        num_heads = extra_params.get('num_heads', 4) if extra_params else 4
        model = MHADINModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                            tag_field_idx=tag_idx, facets=facets, embed_dim=embed_dim,
                            num_heads=num_heads, mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'time_din':
        num_tb = extra_params.get('num_time_buckets', 16) if extra_params else 16
        model = TimeDINModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                             tag_field_idx=tag_idx, embed_dim=embed_dim, num_time_buckets=num_tb,
                             mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'posneg_din':
        model = PosNegDINModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                               tag_field_idx=tag_idx, embed_dim=embed_dim,
                               mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'senet_din':
        red_ratio = extra_params.get('reduction_ratio', 4) if extra_params else 4
        model = SENetDINModel(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                              tag_field_idx=tag_idx, facets=facets, embed_dim=embed_dim,
                              reduction_ratio=red_ratio, mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'tri_ranker':
        red_ratio = extra_params.get('reduction_ratio', 4) if extra_params else 4
        num_tb = extra_params.get('num_time_buckets', 16) if extra_params else 16
        model = UnifiedTriRanker(field_dims=field_dims, vid_field_idx=vid_idx, auth_field_idx=auth_idx,
                                 tag_field_idx=tag_idx, embed_dim=embed_dim, num_time_buckets=num_tb,
                                 reduction_ratio=red_ratio, mlp_hidden_dims=hidden_dims, dropout_rate=dropout)
    elif model_name == 'multitask':
        loss_type = 'multitask'
        num_experts = extra_params.get('num_experts', 4) if extra_params else 4
        expert_dim = extra_params.get('expert_dim', 128) if extra_params else 128
        task_dims = extra_params.get('task_dims', [64, 32]) if extra_params else [64, 32]
        model = MultiTaskRankingModel(field_dims=field_dims, embed_dim=embed_dim,
                                      num_experts=num_experts, expert_hidden_dim=expert_dim,
                                      task_hidden_dims=task_dims, dropout_rate=dropout)
    else:
        raise ValueError(f"Unknown model_name: {model_name}")

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    log(f"Model parameters: {total_params:,d}")

    # Train
    trainer = Trainer(
        model=model,
        learning_rate=lr,
        batch_size=batch_size,
        max_epochs=max_epochs,
        patience=patience,
        task_weights=task_weights,
        loss_type=loss_type,
        pairwise_weight=pairwise_weight,
        use_ips=use_ips,
        verbose=True
    )

    fit_res = trainer.fit(data['train'], data['valid'])
    best_m = fit_res['best_metrics']
    best_ep = fit_res['best_epoch']

    d_gauc = best_m['GAUC'] - OFFICIAL_BASELINE['GAUC']
    d_ndcg = best_m['nDCG@5'] - OFFICIAL_BASELINE['nDCG@5']
    d_prim = best_m['primary'] - OFFICIAL_BASELINE['primary']

    total_runtime = time.time() - t0

    log(f"\n================================================================================")
    log(f"EXPERIMENT {exp_id} RESULTS (Best Epoch: {best_ep}):")
    log(f"  Valid GAUC   : {best_m['GAUC']:.4f} (delta: {d_gauc:+.4f})")
    log(f"  Valid nDCG@5 : {best_m['nDCG@5']:.4f} (delta: {d_ndcg:+.4f})")
    log(f"  Valid Primary: {best_m['primary']:.4f} (delta: {d_prim:+.4f})")
    log(f"  Total Runtime: {total_runtime:.2f}s")
    log(f"================================================================================\n")

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w') as f:
            f.write("\n".join(log_lines) + "\n")

    return {
        'exp_id': exp_id,
        'model': model_name,
        'mode': mode,
        'facets': facets,
        'loss_type': loss_type,
        'best_epoch': best_ep,
        'metrics': best_m,
        'deltas': {'GAUC': d_gauc, 'nDCG@5': d_ndcg, 'primary': d_prim},
        'runtime': total_runtime,
        'predictions': fit_res['valid_predictions'],
        'history': fit_res['history']
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp_id', default='E014')
    parser.add_argument('--model', default='din', choices=['fm', 'deepfm', 'dcn', 'din', 'cross_din', 'mmoe_din', 'bst', 'cross_bst', 'esmm_din', 'mha_din', 'multitask'])
    parser.add_argument('--mode', default='extended', choices=['base5', 'cwm13', 'extended'])
    parser.add_argument('--facets', default='vid', choices=['vid', 'dual_vid', 'vid_auth', 'multi', 'dual_seq', 'all'])
    parser.add_argument('--loss_type', default='bce', choices=['bce', 'bce_pairwise', 'user_pairwise', 'esmm', 'multitask'])
    parser.add_argument('--pairwise_weight', type=float, default=0.1)
    parser.add_argument('--embed_dim', type=int, default=16)
    parser.add_argument('--lr', type=float, default=3e-4)
    parser.add_argument('--batch_size', type=int, default=8192)
    parser.add_argument('--max_epochs', type=int, default=20)
    parser.add_argument('--patience', type=int, default=5)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--log_file', default=None)
    args = parser.parse_args()

    run_experiment(
        exp_id=args.exp_id,
        model_name=args.model,
        mode=args.mode,
        facets=args.facets,
        loss_type=args.loss_type,
        pairwise_weight=args.pairwise_weight,
        embed_dim=args.embed_dim,
        lr=args.lr,
        batch_size=args.batch_size,
        max_epochs=args.max_epochs,
        patience=args.patience,
        seed=args.seed,
        log_file=args.log_file
    )
