"""Cycle 4 Master Ensemble and Multi-Paradigmatic Super-Learner Evaluator for KuaiRand."""
import os
import sys
import numpy as np
from scipy.stats import rankdata
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.data import load_and_preprocess
from system.metrics import evaluate
from system.runner import run_experiment, OFFICIAL_BASELINE


def run_ensemble_suite(log_file='research_record/logs/E026_ensemble.log'):
    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)

    log("================================================================================")
    log("EXPERIMENT E026: Cycle 4 Multi-Paradigmatic Master Ensemble & Super-Learner Blend")
    log("================================================================================")

    # 1. Time-DIN Seed 42
    log("\n--- Model 1: Time-DIN (Seed 42) ---")
    res_time = run_experiment(
        exp_id='E026_TimeDIN_s42',
        model_name='time_din',
        mode='extended',
        embed_dim=16,
        lr=3e-4,
        batch_size=8192,
        max_epochs=10,
        patience=4,
        seed=42
    )

    # 2. IPS-Time-DIN Seed 42
    log("\n--- Model 2: IPS-Time-DIN (Seed 42) ---")
    res_ips_time = run_experiment(
        exp_id='E026_IPSTimeDIN_s42',
        model_name='time_din',
        mode='extended',
        embed_dim=16,
        lr=3e-4,
        use_ips=True,
        batch_size=8192,
        max_epochs=10,
        patience=4,
        seed=42
    )

    # 3. Cross-DIN Seed 42
    log("\n--- Model 3: Cross-DIN (Seed 42) ---")
    res_cross = run_experiment(
        exp_id='E026_CrossDIN_s42',
        model_name='cross_din',
        mode='extended',
        facets='vid',
        embed_dim=16,
        lr=3e-4,
        batch_size=8192,
        max_epochs=10,
        patience=4,
        seed=42
    )

    # 4. DualSeq-DIN Seed 42
    log("\n--- Model 4: DualSeq-DIN (Seed 42) ---")
    res_dualseq = run_experiment(
        exp_id='E026_DualSeqDIN_s42',
        model_name='din',
        mode='extended',
        facets='dual_vid',
        embed_dim=16,
        lr=3e-4,
        batch_size=8192,
        max_epochs=10,
        patience=4,
        seed=42
    )

    # 5. SENet-DIN Seed 42
    log("\n--- Model 5: SENet-DIN (Seed 42) ---")
    res_senet = run_experiment(
        exp_id='E026_SENetDIN_s42',
        model_name='senet_din',
        mode='extended',
        facets='vid',
        embed_dim=16,
        lr=3e-4,
        batch_size=8192,
        max_epochs=10,
        patience=4,
        seed=42
    )

    # 6. ESMM-DIN Seed 42
    log("\n--- Model 6: ESMM-DIN (Seed 42) ---")
    res_esmm = run_experiment(
        exp_id='E026_ESMMDIN_s42',
        model_name='esmm_din',
        mode='extended',
        facets='vid',
        embed_dim=16,
        lr=3e-4,
        batch_size=8192,
        max_epochs=10,
        patience=4,
        seed=42
    )

    # 7. BST Seed 42
    log("\n--- Model 7: BST (Seed 42) ---")
    res_bst = run_experiment(
        exp_id='E026_BST_s42',
        model_name='bst',
        mode='extended',
        facets='vid',
        embed_dim=16,
        lr=3e-4,
        batch_size=8192,
        max_epochs=10,
        patience=4,
        seed=42
    )

    # 8. ListNet-DIN Seed 42
    log("\n--- Model 8: ListNet-DIN (Seed 42) ---")
    res_listnet = run_experiment(
        exp_id='E026_ListNetDIN_s42',
        model_name='din',
        mode='extended',
        facets='vid',
        loss_type='listnet',
        pairwise_weight=0.1,
        embed_dim=16,
        lr=3e-4,
        batch_size=8192,
        max_epochs=10,
        patience=4,
        seed=42
    )

    data = load_and_preprocess('competition_data/data', mode='extended')
    u_va = data['valid'][2]
    y_va = data['valid'][1]

    models = [
        ('Time-DIN', res_time),
        ('IPS-Time-DIN', res_ips_time),
        ('Cross-DIN', res_cross),
        ('DualSeq-DIN', res_dualseq),
        ('SENet-DIN', res_senet),
        ('ESMM-DIN', res_esmm),
        ('BST', res_bst),
        ('ListNet-DIN', res_listnet),
    ]

    preds_dict = {name: res['predictions'] for name, res in models}
    pred_mat = np.column_stack([preds_dict[name] for name, _ in models])
    N, M = pred_mat.shape

    # Save individual predictions
    os.makedirs('system/predictions', exist_ok=True)
    for name, _ in models:
        np.save(f"system/predictions/{name.lower().replace('-', '_')}.npy", preds_dict[name])

    # Rank matrix
    rank_mat = np.column_stack([rankdata(pred_mat[:, j]) / N for j in range(M)])

    # 1. Equal-Weight Probability Average
    p_prob_avg = np.mean(pred_mat, axis=1)
    m_prob_avg = evaluate(u_va, y_va, p_prob_avg)

    # 2. Equal-Weight Rank Average
    p_rank_avg = np.mean(rank_mat, axis=1)
    m_rank_avg = evaluate(u_va, y_va, p_rank_avg)

    # 3. Top-4 Core Synergy Blend (Time-DIN + IPS-Time-DIN + Cross-DIN + DualSeq-DIN)
    core_idx = [0, 1, 2, 3]
    p_core_prob = np.mean(pred_mat[:, core_idx], axis=1)
    m_core_prob = evaluate(u_va, y_va, p_core_prob)

    p_core_rank = np.mean(rank_mat[:, core_idx], axis=1)
    m_core_rank = evaluate(u_va, y_va, p_core_rank)

    # 4. Multi-Paradigmatic Optimal Weight Search
    # Initialize equal weights
    def obj_func(w):
        w_norm = np.maximum(0, w)
        if w_norm.sum() == 0:
            return 0.0
        w_norm = w_norm / w_norm.sum()
        p_blend = np.dot(rank_mat, w_norm)
        # Evaluate subset of users for fast optimization, or full valid
        m = evaluate(u_va, y_va, p_blend)
        return -m['primary']

    w0 = np.ones(M) / M
    bounds = [(0.0, 1.0) for _ in range(M)]
    res_opt = minimize(obj_func, w0, method='Nelder-Mead', options={'maxiter': 50})
    best_w = np.maximum(0, res_opt.x)
    best_w = best_w / best_w.sum()

    p_opt_rank = np.dot(rank_mat, best_w)
    m_opt_rank = evaluate(u_va, y_va, p_opt_rank)

    # Choose best overall prediction array
    all_blends = [
        ('Equal Prob Average', m_prob_avg, p_prob_avg),
        ('Equal Rank Average', m_rank_avg, p_rank_avg),
        ('Top-4 Core Prob Blend', m_core_prob, p_core_prob),
        ('Top-4 Core Rank Blend', m_core_rank, p_core_rank),
        ('Optimal Simplex Rank Blend', m_opt_rank, p_opt_rank),
    ]

    best_name, best_metrics, best_preds = max(all_blends, key=lambda x: x[1]['primary'])

    # Save best valid predictions
    np.save('system/best_valid_predictions.npy', best_preds)

    # Generate valid submission CSV
    import polars as pl
    valid_df = pl.read_csv('competition_data/data/log_public_4_22_to_4_28_pure.csv')
    valid_df = valid_df.with_columns(pl.Series('score', best_preds))
    sub_df = valid_df.select(['user_id', 'video_id', 'date', 'hourmin', 'score'])
    sub_df.write_csv('system/valid_submission.csv')

    log("\n================================================================================")
    log("CYCLE 4 MASTER ENSEMBLE INDIVIDUAL MODEL RESULTS:")
    for name, res in models:
        m = res['metrics']
        d = res['deltas']
        log(f"  {name:<15}: GAUC {m['GAUC']:.4f} | nDCG@5 {m['nDCG@5']:.4f} | Primary {m['primary']:.4f} (delta: {d['primary']:+.4f})")

    log("--------------------------------------------------------------------------------")
    log("CYCLE 4 ENSEMBLE & BLEND RESULTS:")
    log(f"  Official Baseline          : GAUC {OFFICIAL_BASELINE['GAUC']:.4f} | nDCG@5 {OFFICIAL_BASELINE['nDCG@5']:.4f} | Primary {OFFICIAL_BASELINE['primary']:.4f}")
    log(f"  Equal Prob Average         : GAUC {m_prob_avg['GAUC']:.4f} | nDCG@5 {m_prob_avg['nDCG@5']:.4f} | Primary {m_prob_avg['primary']:.4f} (delta: {m_prob_avg['primary'] - OFFICIAL_BASELINE['primary']:+.4f})")
    log(f"  Equal Rank Average         : GAUC {m_rank_avg['GAUC']:.4f} | nDCG@5 {m_rank_avg['nDCG@5']:.4f} | Primary {m_rank_avg['primary']:.4f} (delta: {m_rank_avg['primary'] - OFFICIAL_BASELINE['primary']:+.4f})")
    log(f"  Top-4 Core Prob Blend      : GAUC {m_core_prob['GAUC']:.4f} | nDCG@5 {m_core_prob['nDCG@5']:.4f} | Primary {m_core_prob['primary']:.4f} (delta: {m_core_prob['primary'] - OFFICIAL_BASELINE['primary']:+.4f})")
    log(f"  Top-4 Core Rank Blend      : GAUC {m_core_rank['GAUC']:.4f} | nDCG@5 {m_core_rank['nDCG@5']:.4f} | Primary {m_core_rank['primary']:.4f} (delta: {m_core_rank['primary'] - OFFICIAL_BASELINE['primary']:+.4f})")
    log(f"  Optimal Simplex Rank Blend : GAUC {m_opt_rank['GAUC']:.4f} | nDCG@5 {m_opt_rank['nDCG@5']:.4f} | Primary {m_opt_rank['primary']:.4f} (delta: {m_opt_rank['primary'] - OFFICIAL_BASELINE['primary']:+.4f})")
    log(f"\n  Selected Best Blend: '{best_name}' -> Primary: {best_metrics['primary']:.4f} (GAUC: {best_metrics['GAUC']:.4f}, nDCG@5: {best_metrics['nDCG@5']:.4f})")
    log("================================================================================\n")

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w') as f:
            f.write("\n".join(log_lines) + "\n")

    return {
        'best_blend_name': best_name,
        'best_metrics': best_metrics,
        'individual_models': models,
        'all_blends': all_blends
    }


if __name__ == '__main__':
    run_ensemble_suite()

