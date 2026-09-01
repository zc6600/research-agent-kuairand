from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CompetitionDataError(RuntimeError):
    """Raised when a development-only data view cannot be prepared safely."""


@dataclass(frozen=True)
class DataContract:
    train_first_date: int = 20220408
    train_last_date: int = 20220421
    public_first_date: int = 20220422
    public_last_date: int = 20220428
    evaluation_last_date: int = 20220508
    train_rows: int = 1_141_112
    public_rows: int = 124_909


MANIFEST_VERSION = 4
TRAIN_SOURCE = "log_standard_4_08_to_4_21_pure.csv"
EVALUATION_SOURCE = "log_standard_4_22_to_5_08_pure.csv"
RANDOM_SOURCE = "log_random_4_22_to_5_08_pure.csv"
PUBLIC_OUTPUT = "log_public_4_22_to_4_28_pure.csv"
RANDOM_PUBLIC_OUTPUT = "log_random_4_22_to_4_28_pure.csv"
USER_FEATURES = "user_features_pure.csv"
VIDEO_BASIC = "video_features_basic_pure.csv"


def _contract_dict(contract: DataContract) -> dict[str, int]:
    return {
        "train_first_date": contract.train_first_date,
        "train_last_date": contract.train_last_date,
        "public_first_date": contract.public_first_date,
        "public_last_date": contract.public_last_date,
        "evaluation_last_date": contract.evaluation_last_date,
        "train_rows": contract.train_rows,
        "public_rows": contract.public_rows,
    }


def _copy_csv_window(
    source: Path,
    destination: Path,
    *,
    first_date: int,
    last_date: int,
    source_first_date: int,
    source_last_date: int,
) -> tuple[int, list[str]]:
    rows_written = 0
    with source.open(newline="", encoding="utf-8") as source_handle:
        reader = csv.DictReader(source_handle)
        if not reader.fieldnames or "date" not in reader.fieldnames:
            raise CompetitionDataError(f"CSV is missing required date column: {source}")
        fieldnames = list(reader.fieldnames)
        with destination.open("w", newline="", encoding="utf-8") as destination_handle:
            writer = csv.DictWriter(destination_handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            for row in reader:
                try:
                    date = int(row["date"])
                except (TypeError, ValueError) as error:
                    raise CompetitionDataError(f"CSV contains an invalid date in {source}") from error
                if not source_first_date <= date <= source_last_date:
                    raise CompetitionDataError(
                        f"CSV date {date} is outside the declared source window in {source}"
                    )
                if first_date <= date <= last_date:
                    writer.writerow(row)
                    rows_written += 1
    return rows_written, fieldnames


def _file_record(path: Path, *, relative_to: Path, rows: int | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {"path": path.relative_to(relative_to).as_posix()}
    if rows is not None:
        record["rows"] = rows
    return record


def _manifest_version(destination: Path) -> int | None:
    manifest_path = destination / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    version = manifest.get("schema_version")
    return version if isinstance(version, int) and not isinstance(version, bool) else None


def _reuse_development_view(
    destination: Path, *, contract: DataContract
) -> dict[str, Any]:
    manifest_path = destination / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise CompetitionDataError(f"development-data manifest is invalid: {manifest_path}") from error

    if manifest.get("schema_version") != MANIFEST_VERSION:
        raise CompetitionDataError(
            f"unsupported development-data manifest version; expected {MANIFEST_VERSION}"
        )
    if manifest.get("access_scope") != "development_only_no_hidden_test":
        raise CompetitionDataError("development-data manifest has an unsafe access scope")
    if manifest.get("contract") != _contract_dict(contract):
        raise CompetitionDataError("development-data manifest contract does not match the task")

    expected = {
        "train": f"data/{TRAIN_SOURCE}",
        "public_validation": f"data/{PUBLIC_OUTPUT}",
        "public_random_exposure": f"data/{RANDOM_PUBLIC_OUTPUT}",
        "user_features": f"data/{USER_FEATURES}",
        "video_features_basic": f"data/{VIDEO_BASIC}",
    }
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != set(expected):
        raise CompetitionDataError("development-data manifest files map is incomplete")

    for key, relative_path in expected.items():
        record = files[key]
        if not isinstance(record, dict) or record.get("path") != relative_path:
            raise CompetitionDataError(f"development-data manifest has an unexpected path: {key}")
        if not (destination / relative_path).is_file():
            raise CompetitionDataError(f"development-data file is missing: {relative_path}")

    if files["train"].get("rows") != contract.train_rows:
        raise CompetitionDataError("development-data manifest has the wrong training row count")
    if files["public_validation"].get("rows") != contract.public_rows:
        raise CompetitionDataError("development-data manifest has the wrong public-validation row count")
    random_rows = files["public_random_exposure"].get("rows")
    if not isinstance(random_rows, int) or isinstance(random_rows, bool) or random_rows < 0:
        raise CompetitionDataError("development-data manifest has an invalid public random-exposure row count")
    return manifest


def prepare_development_view(
    source_root: Path,
    destination: Path,
    *,
    contract: DataContract = DataContract(),
) -> dict[str, Any]:
    destination = destination.expanduser().resolve()
    if destination.exists() and _manifest_version(destination) == MANIFEST_VERSION:
        return _reuse_development_view(destination, contract=contract)

    source_root = source_root.expanduser().resolve()
    source_data = source_root / "data"
    if not source_data.is_dir():
        raise CompetitionDataError(f"KuaiRand-Pure data root must contain data/: {source_root}")
    required = (TRAIN_SOURCE, EVALUATION_SOURCE, RANDOM_SOURCE, USER_FEATURES, VIDEO_BASIC)
    missing = [name for name in required if not (source_data / name).is_file()]
    if missing:
        raise CompetitionDataError(f"source data is missing required files: {', '.join(missing)}")

    if destination.exists():
        shutil.rmtree(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".competition-data-", dir=destination.parent))
    try:
        output_data = temporary / "data"
        output_data.mkdir()

        train_output = output_data / TRAIN_SOURCE
        train_rows, train_fields = _copy_csv_window(
            source_data / TRAIN_SOURCE,
            train_output,
            first_date=contract.train_first_date,
            last_date=contract.train_last_date,
            source_first_date=contract.train_first_date,
            source_last_date=contract.train_last_date,
        )
        if train_rows != contract.train_rows:
            raise CompetitionDataError(
                f"training row count mismatch: expected {contract.train_rows}, got {train_rows}"
            )

        public_output = output_data / PUBLIC_OUTPUT
        public_rows, public_fields = _copy_csv_window(
            source_data / EVALUATION_SOURCE,
            public_output,
            first_date=contract.public_first_date,
            last_date=contract.public_last_date,
            source_first_date=contract.public_first_date,
            source_last_date=contract.evaluation_last_date,
        )
        if public_rows != contract.public_rows:
            raise CompetitionDataError(
                f"public-validation row count mismatch: expected {contract.public_rows}, got {public_rows}"
            )
        if public_fields != train_fields:
            raise CompetitionDataError("train and public-validation CSV schemas differ")

        random_public_output = output_data / RANDOM_PUBLIC_OUTPUT
        random_public_rows, _random_fields = _copy_csv_window(
            source_data / RANDOM_SOURCE,
            random_public_output,
            first_date=contract.public_first_date,
            last_date=contract.public_last_date,
            source_first_date=contract.public_first_date,
            source_last_date=contract.evaluation_last_date,
        )

        for name in (USER_FEATURES, VIDEO_BASIC):
            shutil.copyfile(source_data / name, output_data / name)

        manifest: dict[str, Any] = {
            "schema_version": MANIFEST_VERSION,
            "dataset": "KuaiRand-Pure",
            "access_scope": "development_only_no_hidden_test",
            "contract": _contract_dict(contract),
            "files": {
                "train": _file_record(train_output, relative_to=temporary, rows=train_rows),
                "public_validation": _file_record(public_output, relative_to=temporary, rows=public_rows),
                "public_random_exposure": _file_record(
                    random_public_output,
                    relative_to=temporary,
                    rows=random_public_rows,
                ),
                "user_features": _file_record(output_data / USER_FEATURES, relative_to=temporary),
                "video_features_basic": _file_record(output_data / VIDEO_BASIC, relative_to=temporary),
            },
        }
        (temporary / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        for path in temporary.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
        os.replace(temporary, destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a hidden-test-free development data view")
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--expected-train-rows", type=int, default=DataContract.train_rows)
    parser.add_argument("--expected-public-rows", type=int, default=DataContract.public_rows)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    contract = DataContract(
        train_rows=args.expected_train_rows,
        public_rows=args.expected_public_rows,
    )
    try:
        prepare_development_view(
            args.source_root,
            args.destination,
            contract=contract,
        )
    except CompetitionDataError as error:
        print(f"error: {error}", file=os.sys.stderr)
        return 2
    print(f"development data ready: {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
