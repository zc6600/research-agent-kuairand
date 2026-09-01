"""Command-line entry points for the direct Codex Agent baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .baseline_api import (
    run_fm_baseline,
    run_popularity_baseline,
    smoke_result,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m system.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("smoke", help="Run the synthetic API smoke check")

    evaluate = subparsers.add_parser("evaluate-pop", help="Run smoothed item popularity on local KuaiRand data")
    evaluate.add_argument("--data-dir", type=Path, help="Directory containing KuaiRand-Pure CSV files")
    evaluate.add_argument("--split", default="valid", choices=("valid", "random_valid"))
    evaluate.add_argument("--prior", type=float, default=20.0)

    fm = subparsers.add_parser("evaluate-fm", help="Run the official five-field FM")
    fm.add_argument("--data-dir", type=Path, help="Directory containing KuaiRand-Pure CSV files")
    fm.add_argument("--split", default="valid", choices=("valid", "random_valid"))
    fm.add_argument("--factors", type=int, default=16)
    fm.add_argument("--learning-rate", type=float, default=0.001)
    fm.add_argument("--epochs", type=int, default=40)
    fm.add_argument("--batch-size", type=int, default=8192)
    fm.add_argument("--patience", type=int, default=4)
    fm.add_argument("--seed", type=int, default=0)

    pairwise = subparsers.add_parser(
        "evaluate-fm-pairwise", help="Run the within-user pairwise FM"
    )
    pairwise.add_argument("--data-dir", type=Path, help="Directory containing KuaiRand-Pure CSV files")
    pairwise.add_argument("--split", default="valid", choices=("valid", "random_valid"))
    pairwise.add_argument("--factors", type=int, default=8)
    pairwise.add_argument("--learning-rate", type=float, default=0.00025)
    pairwise.add_argument("--epochs", type=int, default=40)
    pairwise.add_argument("--batch-size", type=int, default=8192)
    pairwise.add_argument("--patience", type=int, default=4)
    pairwise.add_argument("--seed", type=int, default=0)
    pairwise.add_argument("--negatives-per-positive", type=int, default=1)
    pairwise.add_argument(
        "--extra-field",
        action="append",
        choices=("user_tab", "user_author", "user_video", "video_tab", "author_tab"),
        default=[],
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "smoke":
        result = smoke_result()
    elif args.command == "evaluate-pop":
        result = run_popularity_baseline(args.data_dir, split=args.split, prior=args.prior)
    elif args.command == "evaluate-fm":
        result = run_fm_baseline(
            args.data_dir,
            split=args.split,
            factors=args.factors,
            learning_rate=args.learning_rate,
            epochs=args.epochs,
            batch_size=args.batch_size,
            patience=args.patience,
            seed=args.seed,
        )
    elif args.command == "evaluate-fm-pairwise":
        from .baseline_api import run_fm_pairwise_baseline

        result = run_fm_pairwise_baseline(
            args.data_dir,
            split=args.split,
            factors=args.factors,
            learning_rate=args.learning_rate,
            epochs=args.epochs,
            batch_size=args.batch_size,
            patience=args.patience,
            seed=args.seed,
            negatives_per_positive=args.negatives_per_positive,
            extra_fields=args.extra_field,
        )
    else:
        raise AssertionError(f"unhandled command: {args.command}")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
