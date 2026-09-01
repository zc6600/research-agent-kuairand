from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from competitions.kuairand.data import (  # noqa: E402
    MANIFEST_VERSION,
    PUBLIC_OUTPUT,
    RANDOM_PUBLIC_OUTPUT,
    RANDOM_SOURCE,
    TRAIN_SOURCE,
    CompetitionDataError,
    DataContract,
    prepare_development_view,
)

FIELDS = ["date", "user_id", "video_id", "tab", "duration_ms", "long_view"]


class CompetitionDataTests(unittest.TestCase):
    def write_csv(self, path: Path, rows: list[dict[str, str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def fixture(self, root: Path) -> tuple[Path, DataContract]:
        source = root / "source"
        data = source / "data"
        data.mkdir(parents=True)
        self.write_csv(
            data / TRAIN_SOURCE,
            [
                {"date": "20220408", "user_id": "t1", "video_id": "v1", "tab": "1", "duration_ms": "1", "long_view": "0"},
                {"date": "20220421", "user_id": "t2", "video_id": "v2", "tab": "1", "duration_ms": "2", "long_view": "1"},
            ],
        )
        self.write_csv(
            data / "log_standard_4_22_to_5_08_pure.csv",
            [
                {"date": "20220422", "user_id": "p1", "video_id": "v1", "tab": "1", "duration_ms": "3", "long_view": "1"},
                {"date": "20220429", "user_id": "HIDDEN_SENTINEL", "video_id": "secret", "tab": "9", "duration_ms": "999", "long_view": "1"},
                {"date": "20220428", "user_id": "p2", "video_id": "v2", "tab": "1", "duration_ms": "4", "long_view": "0"},
            ],
        )
        self.write_csv(
            data / RANDOM_SOURCE,
            [
                {"date": "20220423", "user_id": "r1", "video_id": "rv1", "tab": "0", "duration_ms": "5", "long_view": "0"},
                {"date": "20220501", "user_id": "RANDOM_HIDDEN_SENTINEL", "video_id": "random-secret", "tab": "0", "duration_ms": "6", "long_view": "1"},
                {"date": "20220427", "user_id": "r2", "video_id": "rv2", "tab": "0", "duration_ms": "7", "long_view": "1"},
            ],
        )
        (data / "user_features_pure.csv").write_text("user_id\n", encoding="utf-8")
        (data / "video_features_basic_pure.csv").write_text(
            "video_id,author_id\nv1,a1\nv2,a2\n", encoding="utf-8"
        )
        return source, DataContract(train_rows=2, public_rows=2)

    def test_prepare_filters_hidden_rows_from_standard_and_random_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, contract = self.fixture(root)
            destination = root / "target" / "competition_data"

            manifest = prepare_development_view(source, destination, contract=contract)

            public = (destination / "data" / PUBLIC_OUTPUT).read_text(encoding="utf-8")
            random_public = (destination / "data" / RANDOM_PUBLIC_OUTPUT).read_text(encoding="utf-8")
            self.assertNotIn("HIDDEN_SENTINEL", public)
            self.assertNotIn("secret", public)
            self.assertIn("p1", public)
            self.assertIn("p2", public)
            self.assertNotIn("RANDOM_HIDDEN_SENTINEL", random_public)
            self.assertNotIn("random-secret", random_public)
            self.assertIn("r1", random_public)
            self.assertIn("r2", random_public)
            self.assertFalse((destination / "data" / "log_standard_4_22_to_5_08_pure.csv").exists())
            self.assertFalse((destination / "data" / RANDOM_SOURCE).exists())
            self.assertFalse((destination / "data" / "video_features_statistic_pure.csv").exists())
            self.assertEqual(manifest["schema_version"], MANIFEST_VERSION)
            self.assertEqual(manifest["access_scope"], "development_only_no_hidden_test")
            self.assertEqual(manifest["files"]["public_validation"]["rows"], 2)
            self.assertEqual(manifest["files"]["public_random_exposure"]["rows"], 2)
            self.assertEqual(
                set(manifest["files"]),
                {
                    "train",
                    "public_validation",
                    "public_random_exposure",
                    "user_features",
                    "video_features_basic",
                },
            )
            self.assertNotIn("source_fingerprints", manifest)
            for record in manifest["files"].values():
                self.assertNotIn("sha256", record)

    def test_existing_current_view_is_reused_without_rescanning_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, contract = self.fixture(root)
            destination = root / "competition_data"
            manifest = prepare_development_view(source, destination, contract=contract)
            public = destination / "data" / PUBLIC_OUTPUT
            public.chmod(0o644)
            public.write_text("date,user_id\nnot-a-date,changed-after-setup\n", encoding="utf-8")

            reused = prepare_development_view(source, destination, contract=contract)

            self.assertEqual(reused, manifest)
            self.assertIn("changed-after-setup", public.read_text(encoding="utf-8"))

    def test_row_count_mismatch_does_not_publish_partial_view(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, _contract = self.fixture(root)
            destination = root / "competition_data"

            with self.assertRaisesRegex(CompetitionDataError, "training row count mismatch"):
                prepare_development_view(
                    source,
                    destination,
                    contract=DataContract(train_rows=3, public_rows=2),
                )
            self.assertFalse(destination.exists())

    def test_manifest_is_json_and_contains_no_source_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, contract = self.fixture(root)
            destination = root / "competition_data"
            prepare_development_view(source, destination, contract=contract)

            raw = (destination / "manifest.json").read_text(encoding="utf-8")
            json.loads(raw)
            self.assertNotIn(str(source), raw)

    def test_old_manifest_version_is_rebuilt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, contract = self.fixture(root)
            destination = root / "competition_data"
            manifest = prepare_development_view(source, destination, contract=contract)
            manifest_path = destination / "manifest.json"
            manifest_path.chmod(0o644)
            manifest["schema_version"] = MANIFEST_VERSION - 1
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            rebuilt = prepare_development_view(source, destination, contract=contract)

            self.assertEqual(rebuilt["schema_version"], MANIFEST_VERSION)
            self.assertEqual(
                set(rebuilt["files"]),
                {
                    "train",
                    "public_validation",
                    "public_random_exposure",
                    "user_features",
                    "video_features_basic",
                },
            )


if __name__ == "__main__":
    unittest.main()
