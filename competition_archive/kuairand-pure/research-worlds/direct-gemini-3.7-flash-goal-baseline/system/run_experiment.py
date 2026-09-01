"""Experiment runner and comparison harness."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch

from system.features import KuaiRandData, ALL_CAT_FIELDS
from system.models import DeepFM, MultiTaskDeepFM, DCNv2DeepFM
from system.trainer import train_model, evaluate_model


def run_experiment(
    data_dir: str = "competition_data/data",
    model_type: str = "deepfm",
    embed_dim: int = 16,
    lr: float = 1e-3,
    batch_size: int = 4096,
    epochs: int = 15,
    pair_weight: float = 0.2,
    patience: int = 4,
    device_name: str = "cpu",
):
    print(f"=== Experiment: model={model_type}, embed_dim={embed_dim}, lr={lr}, batch_size={batch_size}, pair_weight={pair_weight} ===")
    t0 = time.time()
    data = KuaiRandData(data_dir)
    print(f"Data preprocessed in {time.time()-t0:.1f}s. Vocab size: {sum(data.field_dims)}, Fields: {len(ALL_CAT_FIELDS)}")

    t0 = time.time()
    X_cat_tr, X_num_tr, y_tr, u_tr, aux_tr = data.extract_features(data.train_logs)
    X_cat_va, X_num_va, y_va, u_va, aux_va = data.extract_features(data.valid_logs)
    print(f"Features extracted in {time.time()-t0:.1f}s.")

    total_vocab = int(sum(data.field_dims))
    num_cats = len(ALL_CAT_FIELDS)
    num_dense = X_num_tr.shape[1]

    device = torch.device(device_name)
    print(f"Using device: {device}")

    if model_type == "deepfm":
        model = DeepFM(
            total_vocab_size=total_vocab,
            num_cat_fields=num_cats,
            num_dense_features=num_dense,
            embed_dim=embed_dim,
            mlp_hidden_dims=(256, 128, 64),
            dropout=0.1
        )
    elif model_type == "multitask":
        model = MultiTaskDeepFM(
            total_vocab_size=total_vocab,
            num_cat_fields=num_cats,
            num_dense_features=num_dense,
            embed_dim=embed_dim,
            mlp_hidden_dims=(256, 128),
            tower_hidden_dims=(64, 32),
            dropout=0.1
        )
    elif model_type == "dcnv2":
        model = DCNv2DeepFM(
            total_vocab_size=total_vocab,
            num_cat_fields=num_cats,
            num_dense_features=num_dense,
            embed_dim=embed_dim,
            cross_layers=3,
            mlp_hidden_dims=(256, 128, 64),
            dropout=0.1
        )
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    num_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Model initialized with {num_params:,} trainable parameters.")

    best_metrics, best_state = train_model(
        model=model,
        X_cat_tr=X_cat_tr,
        X_num_tr=X_num_tr,
        y_tr=y_tr,
        X_cat_va=X_cat_va,
        X_num_va=X_num_va,
        y_va=y_va,
        u_va=u_va,
        aux_tr=aux_tr if model_type == "multitask" else None,
        epochs=epochs,
        batch_size=batch_size,
        lr=lr,
        pair_weight=pair_weight,
        patience=patience,
        device=device,
        verbose=True
    )

    print(f"\n>>> Best Validation Result for {model_type}:")
    print(json.dumps(best_metrics, indent=2))
    return best_metrics, model, data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="deepfm", choices=["deepfm", "multitask", "dcnv2"])
    parser.add_argument("--embed_dim", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--batch_size", type=int, default=4096)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--pair_weight", type=float, default=0.2)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    run_experiment(
        model_type=args.model,
        embed_dim=args.embed_dim,
        lr=args.lr,
        batch_size=args.batch_size,
        epochs=args.epochs,
        pair_weight=args.pair_weight,
        device_name=args.device
    )
