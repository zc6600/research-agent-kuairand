id: S001
git_tag: state/S001
derived_from: null

summary: >
  AliCCP baseline using independent MLP-style CTR and CVR prediction.

system:
  dataset: AliCCP
  model: MLP baseline

  prediction:
    CTR: predicts click probability over impressions
    CVR: trained on clicked samples to predict conversion

  evaluation:
    CTR: AUC over impressions
    CVR: AUC over clicked samples

performance:
  representative:
    CTR_AUC: 0.6210
    CVR_AUC: 0.5912
    evidence_ref: E001

implementation:
  training_entry: system/src/train.py
  model: system/src/models/mlp.py
  evaluator: system/src/evaluate.py
