#!/usr/bin/env python3
"""Multi-seed ensemble of the 38-field rich FM ranker for KuaiRand-Pure.

Trains M diverse seeds of the rich FM representation on the historical training log.
Combines predictions via logit averaging.
Evaluates on deterministic 25% complete-user Medium slice or Full public validation.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from fast_fm import clean_metrics, evaluate, load_data, medium_user, FastFM


def train_single_seed(encoded, dim, actual_fields, seed, k=16, lr=0.001, l2=1e-5, epochs=25, patience=4):
    xtr, ytr, _ = encoded["train"]
    xva, yva, uva = encoded["valid"]

    mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    xmed, ymed = xva[mask], yva[mask]
    umed = [u for u, keep in zip(uva, mask) if keep]

    model = FastFM(dim, k=k, lr=lr, l2=l2, optimizer="adam", seed=seed)
    rng = np.random.default_rng(seed)

    best_primary = -1.0
    best_state = None
    best_epoch = 0
    history = []
    bad = 0

    print(f"--- Training seed {seed} (k={k}, lr={lr}, l2={l2}) ---")
    for ep in range(1, epochs + 1):
        order = rng.permutation(len(ytr))
        losses = []
        t0 = time.time()
        for start in range(0, len(order), 8192):
            idx = order[start:start + 8192]
            losses.append(model.step(xtr[idx], ytr[idx]))

        preds_med = model.predict(xmed)
        med_m = clean_metrics(evaluate(umed, ymed, preds_med))
        dur = time.time() - t0
        history.append({
            "epoch": ep, "loss": float(np.mean(losses)), "duration": dur, **med_m,
        })
        print(f"  Seed {seed} Ep {ep:2d} | loss {np.mean(losses):.4f} | Med GAUC {med_m['GAUC']:.5f} nDCG@5 {med_m['nDCG@5']:.5f} primary {med_m['primary']:.5f} | {dur:.1f}s", flush=True)

        if med_m["primary"] > best_primary + 1e-5:
            best_primary = med_m["primary"]
            best_epoch = ep
            best_state = (model.V.copy(), model.W.copy(), np.float32(model.b))
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                print(f"  Seed {seed} early stopped at epoch {ep}")
                break

    model.V, model.W, model.b = best_state
    med_preds = model.predict(xmed)
    full_preds = model.predict(xva)

    return model, {
        "seed": seed,
        "best_epoch": best_epoch,
        "best_medium": history[best_epoch - 1],
        "med_preds": med_preds,
        "full_preds": full_preds,
        "history": history,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    parser.add_argument("--k", type=int, default=16)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--l2", type=float, default=1e-5)
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    started = time.time()
    fields_all = [
        "user_id", "video_id", "author_id", "tab", "dur_bucket", "hour", "weekday",
        "video_type", "upload_type", "music_type", "tag", "aspect",
        "active", "is_lowactive", "is_live_streamer", "is_video_author",
        "follow_range", "fans_range", "friend_range", "register_range",
        *[f"onehot_{i}" for i in range(18)],
    ]

    encoded, dim, actual_fields = load_data(fields_all, include_crosses=False)
    xva, yva, uva = encoded["valid"]
    mask = np.fromiter((medium_user(u) for u in uva), dtype=bool, count=len(uva))
    umed = [u for u, keep in zip(uva, mask) if keep]
    ymed = yva[mask]

    seed_details = []
    med_preds_list = []
    full_preds_list = []

    for s in args.seeds:
        model, detail = train_single_seed(
            encoded, dim, actual_fields, seed=s,
            k=args.k, lr=args.lr, l2=args.l2,
            epochs=args.epochs, patience=args.patience,
        )
        med_preds_list.append(detail.pop("med_preds"))
        full_preds_list.append(detail.pop("full_preds"))
        seed_details.append(detail)

    # Individual scores
    individual_med_scores = []
    for i, s in enumerate(args.seeds):
        m_score = clean_metrics(evaluate(umed, ymed, med_preds_list[i]))
        individual_med_scores.append({"seed": s, **m_score})
        print(f"Seed {s} Medium Score: GAUC {m_score['GAUC']:.5f} nDCG@5 {m_score['nDCG@5']:.5f} primary {m_score['primary']:.5f}")

    # Ensemble Medium Score
    ens_med_preds = np.mean(med_preds_list, axis=0)
    ens_med_score = clean_metrics(evaluate(umed, ymed, ens_med_preds))
    print(f"\n=== Ensemble ({len(args.seeds)} seeds) Medium Score ===")
    print(f"GAUC: {ens_med_score['GAUC']:.7f}, nDCG@5: {ens_med_score['nDCG@5']:.7f}, primary: {ens_med_score['primary']:.7f}")

    ens_full_score = None
    individual_full_scores = []
    if args.full:
        for i, s in enumerate(args.seeds):
            f_score = clean_metrics(evaluate(uva, yva, full_preds_list[i]))
            individual_full_scores.append({"seed": s, **f_score})
            print(f"Seed {s} Full Score: GAUC {f_score['GAUC']:.7f} nDCG@5 {f_score['nDCG@5']:.7f} primary {f_score['primary']:.7f}")

        ens_full_preds = np.mean(full_preds_list, axis=0)
        ens_full_score = clean_metrics(evaluate(uva, yva, ens_full_preds))
        print(f"\n=== Ensemble ({len(args.seeds)} seeds) Full Validation Score ===")
        print(f"GAUC: {ens_full_score['GAUC']:.7f}, nDCG@5: {ens_full_score['nDCG@5']:.7f}, primary: {ens_full_score['primary']:.7f}")
        # Official baseline deltas
        base_gauc, base_ndcg, base_primary = 0.6674, 0.5357, 0.6016
        print(f"Delta vs baseline: GAUC {ens_full_score['GAUC'] - base_gauc:+.7f}, nDCG@5 {ens_full_score['nDCG@5'] - base_ndcg:+.7f}, primary {ens_full_score['primary'] - base_primary:+.7f}")

    payload = {
        "experiment": "rich_all_fm_ensemble",
        "seeds": args.seeds,
        "k": args.k,
        "lr": args.lr,
        "l2": args.l2,
        "num_fields": len(actual_fields),
        "dim": dim,
        "individual_medium_scores": individual_med_scores,
        "ensemble_medium_score": ens_med_score,
        "individual_full_scores": individual_full_scores if args.full else None,
        "ensemble_full_score": ens_full_score,
        "seed_details": seed_details,
        "elapsed_seconds": time.time() - started,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
