"""Command-line entry points for the gpt-5.6-luna direct-control baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .baseline_api import run_optimized_ranker, run_popularity_baseline, smoke_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m system.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("smoke", help="Run the synthetic API smoke check")

    evaluate = subparsers.add_parser("evaluate-pop", help="Run smoothed item popularity on local KuaiRand data")
    evaluate.add_argument("--data-dir", type=Path, help="Directory containing KuaiRand-Pure CSV files")
    evaluate.add_argument("--split", default="valid", choices=("valid", "test"))
    evaluate.add_argument("--prior", type=float, default=20.0)

    rank = subparsers.add_parser("evaluate-fm", help="Run the validated FM ranker on local KuaiRand data")
    rank.add_argument("--data-dir", type=Path, help="Directory containing KuaiRand-Pure CSV files")
    rank.add_argument("--split", default="valid", choices=("valid", "test"))
    rank.add_argument("--k", type=int, default=16)
    rank.add_argument("--lr", type=float, default=0.001)
    rank.add_argument("--epochs", type=int, default=40)
    rank.add_argument("--seed", type=int, default=0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "smoke":
        result = smoke_result()
    elif args.command == "evaluate-pop":
        result = run_popularity_baseline(args.data_dir, split=args.split, prior=args.prior)
    elif args.command == "evaluate-fm":
        result = run_optimized_ranker(
            args.data_dir,
            split=args.split,
            k=args.k,
            lr=args.lr,
            epochs=args.epochs,
            seed=args.seed,
        )
    else:
        raise AssertionError(f"unhandled command: {args.command}")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
