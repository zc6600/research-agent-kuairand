"""Hyperparameter exploration for FM on KuaiRand-Pure."""

from __future__ import annotations

import time
import numpy as np
from system.fm_experiments import load_raw_data, build_fm_dataset
from starter_kit.evaluate import evaluate
import starter_kit.baseline as B

def run_grid():
    splits = load_raw_data()
    fields = ['user_id', 'video_id', 'author_id', 'tag', 'tab', 'hour', 'dow', 'dur_bucket']
    print(f"Building dataset with fields: {fields}")
    enc, dim = build_fm_dataset(splits, fields)
    Xtr, ytr, _ = enc['train']
    Xva, yva, uva = enc['valid']
    print(f"Total encoded dim: {dim}")

    configs = [
        # (k, lr, l2, bs, desc)
        (16, 0.001, 1e-6, 8192, "k=16, lr=1e-3, l2=1e-6 (baseline cfg)"),
        (16, 0.001, 1e-5, 8192, "k=16, lr=1e-3, l2=1e-5"),
        (16, 0.001, 1e-4, 8192, "k=16, lr=1e-3, l2=1e-4"),
        (32, 0.001, 1e-6, 8192, "k=32, lr=1e-3, l2=1e-6"),
        (32, 0.001, 1e-5, 8192, "k=32, lr=1e-3, l2=1e-5"),
        (32, 0.0005, 1e-5, 8192, "k=32, lr=5e-4, l2=1e-5"),
        (48, 0.001, 1e-5, 8192, "k=48, lr=1e-3, l2=1e-5"),
        (64, 0.0008, 1e-5, 8192, "k=64, lr=8e-4, l2=1e-5"),
    ]

    results = []
    for k, lr, l2, bs, desc in configs:
        t0 = time.time()
        m = B.FM(dim, k=k, lr=lr, l2=l2, seed=0)
        rng = np.random.default_rng(0)
        best = -1.0
        best_state = None
        bad = 0
        best_ep = 0

        for ep in range(1, 35):
            idx = rng.permutation(len(ytr))
            for i in range(0, len(idx), bs):
                m.step(Xtr[idx[i:i + bs]], ytr[idx[i:i + bs]])
            va = evaluate(uva, yva, m.predict(Xva))
            if va['primary'] > best + 1e-5:
                best = va['primary']
                bad = 0
                best_ep = ep
                best_state = (m.V.copy(), m.W.copy(), np.float32(m.b))
            else:
                bad += 1
                if bad >= 4:
                    break

        m.V, m.W, m.b = best_state
        final_va = evaluate(uva, yva, m.predict(Xva))
        elapsed = time.time() - t0
        print(f"{desc:45s} | best ep {best_ep:2d} | GAUC {final_va['GAUC']:.4f} | nDCG@5 {final_va['nDCG@5']:.4f} | primary {final_va['primary']:.4f} | {elapsed:.1f}s")
        results.append((desc, final_va))

    return results

if __name__ == '__main__':
    run_grid()
