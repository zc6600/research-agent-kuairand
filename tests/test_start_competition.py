from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPETITION_SCRIPT = ROOT / "scripts" / "competition.sh"
RESEARCH_AGENT_SCRIPT = ROOT / "scripts" / "research-agent"
STARTER_FILES = (
    "README.md",
    "ablation_features.py",
    "baseline.py",
    "baseline_scores.json",
    "data.py",
    "evaluate.py",
    "submit.py",
)
DATA_FILES = (
    "log_random_4_22_to_5_08_pure.csv",
    "log_standard_4_08_to_4_21_pure.csv",
    "log_standard_4_22_to_5_08_pure.csv",
    "user_features_pure.csv",
    "video_features_basic_pure.csv",
    "video_features_statistic_pure.csv",
)


class CompetitionScriptTests(unittest.TestCase):
    def fixture(self, workspace: Path) -> tuple[Path, dict[str, str], Path, Path]:
        target = workspace / "projects" / "kuairand-pure"
        task = workspace / "task.md"
        personal = workspace / "PERSONAL.md"
        archive = workspace / "kuairand-starter-kit.zip"
        data_root = workspace / "data" / "KuaiRand-Pure"
        codex_args = workspace / "codex-args.json"
        codex_count = workspace / "codex-count.txt"
        fake_bin = workspace / "bin"
        fake_bin.mkdir()
        task.write_text("# Task\n", encoding="utf-8")
        personal.write_text("# Runtime\n", encoding="utf-8")

        data_dir = data_root / "data"
        data_dir.mkdir(parents=True)
        fields = ["date", "user_id", "video_id", "tab", "duration_ms", "long_view"]
        with (data_dir / DATA_FILES[1]).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(
                [
                    {"date": "20220408", "user_id": "t1", "video_id": "v1", "tab": "1", "duration_ms": "1", "long_view": "0"},
                    {"date": "20220421", "user_id": "t2", "video_id": "v2", "tab": "1", "duration_ms": "2", "long_view": "1"},
                ]
            )
        with (data_dir / DATA_FILES[2]).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(
                [
                    {"date": "20220422", "user_id": "p1", "video_id": "v1", "tab": "1", "duration_ms": "3", "long_view": "1"},
                    {"date": "20220429", "user_id": "HIDDEN_SENTINEL", "video_id": "secret", "tab": "9", "duration_ms": "999", "long_view": "1"},
                    {"date": "20220428", "user_id": "p2", "video_id": "v2", "tab": "1", "duration_ms": "4", "long_view": "0"},
                ]
            )
        with (data_dir / DATA_FILES[0]).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(
                [
                    {"date": "20220423", "user_id": "r1", "video_id": "rv1", "tab": "0", "duration_ms": "5", "long_view": "0"},
                    {"date": "20220501", "user_id": "RANDOM_HIDDEN_SENTINEL", "video_id": "random-secret", "tab": "0", "duration_ms": "6", "long_view": "1"},
                    {"date": "20220427", "user_id": "r2", "video_id": "rv2", "tab": "0", "duration_ms": "7", "long_view": "1"},
                ]
            )
        (data_dir / DATA_FILES[3]).write_text("user_id\n", encoding="utf-8")
        (data_dir / DATA_FILES[4]).write_text("video_id,author_id\nv1,a1\nv2,a2\n", encoding="utf-8")
        (data_dir / DATA_FILES[5]).write_text("fixture statistic features\n", encoding="utf-8")

        with zipfile.ZipFile(archive, "w") as starter_zip:
            starter_zip.writestr("kuairand-starter-kit/", "")
            for name in STARTER_FILES:
                starter_zip.writestr(f"kuairand-starter-kit/{name}", f"fixture for {name}\n")
        archive_sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()

        fake_codex = fake_bin / "codex"
        fake_codex.write_text(
            """#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import sys

role = os.environ.get("RESEARCH_AGENT_ROLE")
count_path = pathlib.Path(os.environ["FAKE_CODEX_COUNT_FILE"])
if role == "SCIENTIST":
    count = int(count_path.read_text()) + 1 if count_path.exists() else 1
    count_path.write_text(str(count))
    raise SystemExit(0)

pathlib.Path(os.environ["FAKE_CODEX_ARGS_FILE"]).write_text(json.dumps(sys.argv[1:]))
pathlib.Path(os.environ["FAKE_CODEX_ENV_FILE"]).write_text(json.dumps({
    "raw": os.environ.get("RESEARCH_AGENT_COMPETITION_DATA_ROOT"),
    "development": os.environ.get("RESEARCH_AGENT_DEVELOPMENT_DATA_ROOT"),
}))
target = pathlib.Path(os.environ["RESEARCH_AGENT_TARGET"])
start_cycle = int(os.environ["RESEARCH_AGENT_START_CYCLE"])
max_cycles = int(os.environ["RESEARCH_AGENT_MAX_CYCLES"])
requested_status = os.environ.get("FAKE_CODEX_STATUS", "converged")
iterations = max_cycles if requested_status == "continue" else 1
for offset in range(iterations):
    cycle_id = start_cycle + offset
    brief_path = target / "research_record/runtime/current-brief.json"
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(json.dumps({
        "schema_version": 2,
        "cycle_id": cycle_id,
        "concerns": ["fixture iteration"],
        "constraints": [],
        "budget": {},
    }))
    subprocess.run([
        os.environ["FAKE_RESEARCH_AGENT"], "launch-inner",
        "--target", str(target), "--cli", os.environ["RESEARCH_AGENT_CLI"], "--allow-edits",
    ], check=True, env=os.environ.copy())
pathlib.Path(os.environ["RESEARCH_AGENT_CYCLE_RESULT_FILE"]).write_text(json.dumps({
    "status": requested_status,
    "summary": "fixture complete",
    "next_action": "none",
}))
""",
            encoding="utf-8",
        )
        fake_codex.chmod(0o755)

        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{fake_bin}{os.pathsep}{environment['PATH']}",
                "FAKE_CODEX_ARGS_FILE": str(codex_args),
                "FAKE_CODEX_COUNT_FILE": str(codex_count),
                "FAKE_CODEX_ENV_FILE": str(workspace / "codex-env.json"),
                "FAKE_RESEARCH_AGENT": str(RESEARCH_AGENT_SCRIPT),
                "RESEARCH_AGENT_COMPETITION_CLI": "codex",
                "RESEARCH_AGENT_COMPETITION_TARGET": str(target),
                "RESEARCH_AGENT_COMPETITION_TASK": str(task),
                "RESEARCH_AGENT_COMPETITION_PERSONAL": str(personal),
                "RESEARCH_AGENT_COMPETITION_STARTER_KIT": str(archive),
                "RESEARCH_AGENT_COMPETITION_STARTER_KIT_SHA256": archive_sha256,
                "RESEARCH_AGENT_COMPETITION_DATA_ROOT": str(data_root),
                "RESEARCH_AGENT_COMPETITION_EXPECTED_TRAIN_ROWS": "2",
                "RESEARCH_AGENT_COMPETITION_EXPECTED_PUBLIC_ROWS": "2",
                "GIT_AUTHOR_NAME": "Research Agent Test",
                "GIT_AUTHOR_EMAIL": "research-agent@example.invalid",
                "GIT_COMMITTER_NAME": "Research Agent Test",
                "GIT_COMMITTER_EMAIL": "research-agent@example.invalid",
            }
        )
        return target, environment, codex_args, codex_count

    def run_script(self, *arguments: str, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [COMPETITION_SCRIPT, *arguments],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )

    def assert_success(self, completed: subprocess.CompletedProcess[str]) -> None:
        details = f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        match = re.search(r"log=([^\s]+)", completed.stdout)
        if match:
            log_path = Path(match.group(1))
            if log_path.is_file():
                details += f"\nMETA log:\n{log_path.read_text(encoding='utf-8', errors='replace')}"
        self.assertEqual(completed.returncode, 0, details)

    def assert_target_ready(self, target: Path) -> None:
        git_root = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        self.assertEqual(Path(git_root), target.resolve())
        self.assertEqual((target / "research_record" / "VERSION").read_text().strip(), "research-agent-record-v5")
        self.assertEqual(
            sorted(path.name for path in (target / "starter_kit").iterdir()),
            sorted(STARTER_FILES),
        )
        development = target / "competition_data"
        manifest = json.loads((development / "manifest.json").read_text(encoding="utf-8"))
        self.assertNotIn("validation_runner", manifest["files"])
        self.assertNotIn("source_fingerprints", manifest)
        exposed = {path.name for path in (development / "data").iterdir()}
        self.assertIn("log_standard_4_08_to_4_21_pure.csv", exposed)
        self.assertIn("log_public_4_22_to_4_28_pure.csv", exposed)
        self.assertIn("log_random_4_22_to_4_28_pure.csv", exposed)
        self.assertNotIn("log_standard_4_22_to_5_08_pure.csv", exposed)
        self.assertNotIn("log_random_4_22_to_5_08_pure.csv", exposed)
        self.assertNotIn("video_features_statistic_pure.csv", exposed)
        random_public = (development / "data" / "log_random_4_22_to_4_28_pure.csv").read_text(encoding="utf-8")
        self.assertNotIn("RANDOM_HIDDEN_SENTINEL", random_public)
        self.assertNotIn("random-secret", random_public)

    def test_setup_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target, environment, codex_args, _ = self.fixture(Path(temporary))
            first = self.run_script("setup", "--quiet", environment=environment)
            second = self.run_script("setup", "--quiet", environment=environment)
            self.assert_success(first)
            self.assert_success(second)
            self.assertFalse(codex_args.exists())
            self.assert_target_ready(target)

    def test_existing_starter_kit_is_pinned_to_the_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target, environment, _, _ = self.fixture(Path(temporary))
            self.assert_success(self.run_script("setup", "--quiet", environment=environment))
            Path(environment["RESEARCH_AGENT_COMPETITION_STARTER_KIT"]).unlink()
            environment["RESEARCH_AGENT_COMPETITION_STARTER_KIT_SHA256"] = "0" * 64

            completed = self.run_script("setup", "--quiet", environment=environment)

            self.assert_success(completed)
            self.assert_target_ready(target)

    def test_existing_curated_view_does_not_require_raw_data_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target, environment, _, _ = self.fixture(Path(temporary))
            self.assert_success(self.run_script("setup", "--quiet", environment=environment))
            environment["RESEARCH_AGENT_COMPETITION_DATA_ROOT"] = str(Path(temporary) / "missing-data")
            self.assert_success(self.run_script("setup", "--quiet", environment=environment))
            self.assert_target_ready(target)

    def test_existing_stale_record_is_rejected_during_setup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target, environment, _, _ = self.fixture(Path(temporary))
            target.mkdir(parents=True)
            (target / "task.md").write_text("task\n", encoding="utf-8")
            (target / "PERSONAL.md").write_text("personal\n", encoding="utf-8")
            record = target / "research_record"
            record.mkdir()
            (record / "VERSION").write_text("research-agent-record-v3\n", encoding="utf-8")

            completed = self.run_script("setup", "--quiet", environment=environment)

            self.assertEqual(completed.returncode, 2)
            self.assertIn("expected 'research-agent-record-v5'", completed.stderr)
            self.assertFalse((target / "starter_kit").exists())
            self.assertFalse((target / "competition_data").exists())

    def test_step_uses_luna_for_one_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target, environment, codex_args, codex_count = self.fixture(Path(temporary))
            completed = self.run_script("step", "--quiet", "--model", "luna", environment=environment)
            self.assert_success(completed)
            self.assertEqual(codex_count.read_text(encoding="utf-8"), "1")
            self.assert_target_ready(target)
            invocation_args = json.loads(codex_args.read_text(encoding="utf-8"))
            model_index = invocation_args.index("--model")
            self.assertEqual(invocation_args[model_index + 1], "gpt-5.6-luna")
            runner_environment = json.loads((target.parents[1] / "codex-env.json").read_text())
            self.assertIsNone(runner_environment["raw"])
            self.assertEqual(Path(runner_environment["development"]).resolve(), (target / "competition_data").resolve())

    def test_first_setup_fails_before_launch_when_raw_data_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, environment, codex_args, _ = self.fixture(Path(temporary))
            environment["RESEARCH_AGENT_COMPETITION_DATA_ROOT"] = str(Path(temporary) / "missing-data")
            completed = self.run_script("step", "--quiet", environment=environment)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("KuaiRand-Pure data root must contain data/", completed.stderr)
            self.assertFalse(codex_args.exists())

    def test_run_preserves_meta_continue_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target, environment, _, codex_count = self.fixture(Path(temporary))
            environment["FAKE_CODEX_STATUS"] = "continue"
            completed = self.run_script("run", "--quiet", "--max-cycles", "2", environment=environment)
            self.assert_success(completed)
            self.assertEqual(codex_count.read_text(encoding="utf-8"), "2")
            self.assertIn("continue", completed.stdout)
            self.assertNotIn("budget_exhausted", completed.stdout)
            self.assert_target_ready(target)


if __name__ == "__main__":
    unittest.main()
