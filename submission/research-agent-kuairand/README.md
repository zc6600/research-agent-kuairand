# KuaiRand-Pure Research Agent submission

This directory is the sanitized, public evidence package for the E001–E013 Research Agent trajectory described in the [complete public report](https://github.com/zc6600/research-agent-kuairand/blob/main/docs/FINAL_REPORT.md). It contains the final submitted implementation and intentionally excludes raw datasets, caches, credentials, personal paths, and later local experiments.

## Verified result

| Checkpoint | GAUC | nDCG@5 | Primary | Delta vs official validation primary |
|---|---:|---:|---:|---:|
| Official five-field FM | 0.6674000 | 0.5357000 | 0.6016000 | — |
| **Research Agent submission: eight-seed 46-field FM** | **0.6728421** | **0.5390304** | **0.6059363** | **+0.0043363** |

Public repository commit containing the submitted implementation:
`c73e7035bf4a51ebd73068dc148a3d07c5ccd592`. The SHA-256 of
`system/ensemble_46.py` is
`c6fc9c91386012d437d18251d528d8aa7b13c10e8b1784bb5e117c6a2a304205`.

The final prediction file contains 170,588 test rows and passed the organizer's unchanged Starter Kit alignment checker. No hidden-test metric was used for development or checkpoint selection.

## Contents

- [`system/ensemble_46.py`](system/ensemble_46.py): submitted Research Agent scorer plus final test-output support.
- [`system/evidence/`](system/evidence/): raw JSON evidence for E001–E013.
- [`research_record/RESEARCH_RECORD.yaml`](research_record/RESEARCH_RECORD.yaml): ledger truncated after E013.
- [`research_record/reports/`](research_record/reports/): original Scientist reports for cycles 1–4.
- [`research_record/STATE.yaml`](research_record/STATE.yaml): descriptive implementation and provenance metadata.
- [`diffs/`](diffs/): code-only State transition patches for cycles 1–4;
  cycle 3 is intentionally empty because that State crystallization changed
  only metadata and evidence.
- [`telemetry/`](telemetry/): sanitized run lifecycle and measured model-usage JSON for all four retained cycles.
- [`final/research-agent-run.json`](final/research-agent-run.json): exact reproduction result.
- [`final/research-agent-test.csv`](final/research-agent-test.csv): checked final prediction artifact.
- [`final/submit-check.txt`](final/submit-check.txt): checker result and checksum.
- [`starter_kit/`](starter_kit/): unchanged organizer evaluator and submission checker.

## Data

Download KuaiRand-Pure separately and point `--data-dir` to its `data/` directory. The directory must contain:

```text
log_standard_4_08_to_4_21_pure.csv
log_standard_4_22_to_5_08_pure.csv
user_features_pure.csv
video_features_basic_pure.csv
```

Data is not redistributed in this repository.

## Reproduce the Research Agent submission

Run from this directory with `uv`:

```bash
uv run --python 3.12.11 --with numpy==2.5.2 \
  python system/ensemble_46.py \
  --data-dir /absolute/path/to/KuaiRand-Pure/data \
  --seeds 0 1 2 3 4 5 6 7 \
  --k 16 --lr 0.001 --l2 1e-5 --full \
  --submission final/research-agent-test.csv \
  --output final/research-agent-run.json
```

The script always selects per-seed checkpoints on the deterministic 25% complete-user public-validation slice. Test labels are not read by the model; test rows are used only after the submitted recipe is fixed to emit prediction scores.

Validate the generated file with the unchanged organizer checker:

```bash
uv run --python 3.12.11 --with numpy==2.5.2 \
  python starter_kit/submit.py final/research-agent-test.csv \
  --data_dir /absolute/path/to/KuaiRand-Pure/data \
  --split test --check
```

Expected output:

```text
✓ 格式与对齐校验通过：170,588 行，split=test
```

## Resource accounting

Across the four retained E001–E013 cycle runs:

- agent-loop iterations: **4 autonomous cycles out of the 50-iteration cap**;
  the 13 named E001–E013 records are experiments nested within those cycles;
- total LLM input + output including cache-read input: **48,240,128 tokens**;
- non-cache input + output: 4,020,880 tokens;
- cache-read input: 44,219,248 tokens;
- combined agent wall-clock: 1h 55m 29s;
- training/evaluation GPU use: 0 GPU-hours.

AGY reports cache-read input separately from `input`, while Codex includes it
inside `input`; the totals above normalize those runner-specific semantics
without double-counting cache-read tokens. The telemetry `model` fields use the normalized agent-model labels
`gemini-3.7-flash`, `gpt-5.6-sol`, and `gpt-5.6-luna`. The low-level `cli` and
`runner` fields retain the historical launcher identifiers so the raw records
remain reproducible.

The final eight-seed reproduction in [`final/research-agent-run.json`](final/research-agent-run.json) took 870.07 seconds on the current CPU environment; the original competition evidence recorded 764.74 seconds on the competition run environment. Both runs reproduce the same validation metrics.
