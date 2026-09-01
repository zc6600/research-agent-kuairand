# KuaiRand-Pure Research Agent Implementation

## Submitted Score-Bearing Implementation

1. **Primary Score-Bearing Implementation: Research Agent submission** (`system/ensemble_46.py`)
   - 46-field comprehensive representation: 38 demographic/video baseline features + 8 leak-free historical user preference/affinity profiles (top tag, top tab, long-view rate bucket, interaction count bucket, tag match, tab match, secondary video tag, video upload age).
   - Trained across 8 diverse seeds on `log_standard_4_08_to_4_21_pure.csv` with per-seed early stopping on deterministic 25% complete-user Medium partition.
   - Evaluated with organizer's unchanged `starter_kit/evaluate.py` on full public validation (`log_public_4_22_to_4_28_pure.csv`, 124,909 rows / 22,377 users).
   - **Validation Metrics**: GAUC **0.6728421**, nDCG@5 **0.5390304**, primary **0.6059363** (Delta vs official baseline: GAUC +0.0054421, nDCG@5 +0.0033304, primary +0.0043363; Delta vs prior 38-field ensemble: primary +0.0015074).
   - **Reproduction**:
     ```bash
     uv run --with numpy python system/ensemble_46.py \
       --seeds 0 1 2 3 4 5 6 7 --k 16 --lr 0.001 --l2 1e-5 --full \
       --output system/evidence/cycle4-fm-rich46-ensemble8-full.json
     ```

2. **Field-weighted Factorization Machine (FwFM) Ensemble** (`system/fast_fwfm_ensemble.py`)
   - 46-field Field-weighted Factorization Machine learning explicit $(46 \times 46)$ field-pair interaction weights alongside latent embeddings.
   - **Validation Metrics (4 Seeds)**: GAUC **0.6724305**, nDCG@5 **0.5385388**, primary **0.6054846**.
   - **Reproduction**:
     ```bash
     uv run --with numpy python system/fast_fwfm_ensemble.py \
       --seeds 0 1 2 3 --k 16 --lr 0.001 --l2 1e-5 --full \
       --output system/evidence/cycle4-fwfm-rich46-ensemble4-full.json
     ```

3. **38-Field Multi-Seed FM Ensemble** (`system/ensemble_fm.py`)
   - Earlier 8-seed ensemble baseline (primary 0.6044289).

4. **Single-Seed 38-Field Rich FM** (`system/fast_fm.py`)
   - Baseline single-seed FM ranker.

## Diagnostic & Exploratory Implementations

- `catboost_ranker.py`: Tree-based GBDT ranking (Logloss / Pairwise).
- `deep_ranker.py` / `neural_ranker.py`: PyTorch DeepFM and Multi-Task DeepFM.
- `train_evaluate.py`: Standalone historical target-encoding ranker.
- `ensemble_ranker.py`: FM + Target-encoding blend experiment.
