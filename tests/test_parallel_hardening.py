from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent import parallel_support
from research_agent.bootstrap import BootstrapError
from research_agent.cli import build_parser
from research_agent.parallel import promote_parallel_branch
from research_agent.runtime import write_json


def git(target: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(target), *args],
        check=True, capture_output=True, text=True,
    )
    return completed.stdout.strip()


def has_ref(target: Path, ref: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(target), "show-ref", "--verify", "--quiet", ref],
        check=False,
    ).returncode == 0


def record_text(message: str) -> str:
    return (
        "experiments:\n"
        "  - id: E1\n"
        f"    record: {message}\n"
        "    primary_metric: {name: null, value: null}\n"
        "    official_score: false\n"
        "    resulting_state: null\n"
        "    evidence: []\n"
        "manual_interventions: []\n"
    )


class ParallelHardeningTests(unittest.TestCase):
    def make_target(self, root: Path) -> Path:
        target = root / "target"
        target.mkdir()
        git(target, "init", "-q")
        git(target, "config", "user.email", "research-agent@example.invalid")
        git(target, "config", "user.name", "Research Agent Test")
        (target / ".gitignore").write_text(
            "research_record/RESEARCH_RECORD.yaml\n"
            "research_record/RESEARCH_BRIEF.md\n"
            "research_record/EXPLORE.md\n"
            "research_record/OPTIMIZE.md\n"
            "research_record/ENGINEERING.md\n"
            "research_record/KNOWLEDGE.md\n"
            "research_record/RESEARCH_INTUITION.md\n"
            "research_record/DO_BETTER.md\n"
            "research_record/logs/\n"
            "research_record/archive/\n"
            "research_record/runtime/\n",
            encoding="utf-8",
        )
        record = target / "research_record"
        record.mkdir()
        (record / "VERSION").write_text("research-agent-record-v5\n", encoding="utf-8")
        (record / "SYSTEM_CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
        (record / "RESEARCH_METHOD.md").write_text("# Method\n", encoding="utf-8")
        (record / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        (record / "RESEARCH_BRIEF.md").write_text("# Research Brief\n", encoding="utf-8")
        (record / "RESEARCH_RECORD.yaml").write_text(
            "experiments: []\nmanual_interventions: []\n", encoding="utf-8"
        )
        (record / "EXPLORE.md").write_text("# Explore\nbase\n", encoding="utf-8")
        (record / "OPTIMIZE.md").write_text("# Task Optimization\n", encoding="utf-8")
        (record / "ENGINEERING.md").write_text("# Engineering\n", encoding="utf-8")
        (record / "KNOWLEDGE.md").write_text("# Knowledge\n", encoding="utf-8")
        (record / "RESEARCH_INTUITION.md").write_text(
            "# Research Intuition\n\n## Intuitions\n", encoding="utf-8"
        )
        (record / "DO_BETTER.md").write_text(
            "# How to Do Better\n\n## Lessons\n", encoding="utf-8"
        )
        reports = record / "reports"
        reports.mkdir(exist_ok=True)
        (reports / "init.md").write_text("# Init\n", encoding="utf-8")
        (record / "STATE.yaml").write_text(
            "id: S001\ngit_tag: state/S001\nderived_from: null\n"
            "scientist_report: research_record/reports/init.md\n",
            encoding="utf-8",
        )
        (target / "task.md").write_text("research task\n", encoding="utf-8")
        (target / "PERSONAL.md").write_text("test environment\n", encoding="utf-8")
        (target / "system").mkdir()
        (target / "system/model.py").write_text("MODEL = 'baseline'\n", encoding="utf-8")
        git(target, "add", "-A")
        git(target, "commit", "-qm", "state S001")
        git(target, "tag", "-a", "state/S001", "-m", "S001")
        return target

    def copy_memory(self, source: Path, destination: Path) -> None:
        parallel_support.snapshot_memory(source, destination, include_meta=False)

    def candidate(
        self,
        target: Path,
        *,
        source_commit: str,
        workspace: Path,
        state_id: str,
        derived_from: str,
        model: str,
    ) -> str:
        subprocess.run(
            ["git", "-C", str(target), "worktree", "add", "--detach", str(workspace), source_commit],
            check=True, capture_output=True, text=True,
        )
        (workspace / "system/model.py").write_text(f"MODEL = '{model}'\n", encoding="utf-8")
        (workspace / "research_record/STATE.yaml").write_text(
            f"id: {state_id}\ngit_tag: state/{state_id}\nderived_from: {derived_from}\n"
            "scientist_report: research_record/reports/init.md\n",
            encoding="utf-8",
        )
        git(workspace, "add", "system", "research_record/STATE.yaml")
        git(workspace, "commit", "-qm", f"candidate {state_id}")
        return git(workspace, "rev-parse", "HEAD")

    def test_parallel_synthesis_is_explicit_opt_in(self) -> None:
        base = [
            "parallel", "--target", "/tmp/project", "--cli", "codex", "--allow-edits",
        ]
        disabled = build_parser().parse_args(base)
        enabled = build_parser().parse_args([*base, "--synthesis"])
        self.assertFalse(disabled.synthesis)
        self.assertTrue(enabled.synthesis)

    def test_promote_creates_every_state_tag_on_accepted_ancestry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.make_target(root)
            base_commit = git(target, "rev-parse", "HEAD")
            parent = root / "parent"
            parent_commit = self.candidate(
                target,
                source_commit=base_commit,
                workspace=parent,
                state_id="P1-r1b1",
                derived_from="S001",
                model="parent",
            )
            child = root / "child"
            child_commit = self.candidate(
                target,
                source_commit=parent_commit,
                workspace=child,
                state_id="P1-r2b1",
                derived_from="P1-r1b1",
                model="child",
            )
            (child / "research_record/RESEARCH_RECORD.yaml").write_text(
                record_text("accepted child research"), encoding="utf-8"
            )
            (child / "research_record/EXPLORE.md").write_bytes(
                (target / "research_record/EXPLORE.md").read_bytes()
            )

            parallel_dir = target / "research_record/runtime/parallel-hardening"
            base_memory = parallel_dir / "base-memory"
            child_memory = parallel_dir / "branches/r2b1-memory"
            self.copy_memory(target, base_memory)
            self.copy_memory(child, child_memory)
            write_json(parallel_dir / "manifest.json", {
                "schema_version": 1,
                "kind": "parallel",
                "parallel_id": "P1",
                "target": str(target.resolve()),
                "base_commit": base_commit,
                "base_memory_snapshot": str(base_memory),
                "rounds_log": [
                    {
                        "round": 1,
                        "branches": [{
                            "kind": "replica",
                            "branch_id": "r1b1",
                            "parent_branch": "root",
                            "base_commit": base_commit,
                            "base_state": {"id": "S001", "git_tag": "state/S001"},
                            "workspace": str(parent),
                            "candidate_commit": parent_commit,
                            "candidate_state_id": "P1-r1b1",
                            "system_state_dirty": False,
                            "status": "completed",
                        }],
                    },
                    {
                        "round": 2,
                        "branches": [{
                            "kind": "replica",
                            "branch_id": "r2b1",
                            "parent_branch": "r1b1",
                            "base_commit": parent_commit,
                            "base_state": {"id": "P1-r1b1", "git_tag": "state/P1-r1b1"},
                            "workspace": str(child),
                            "candidate_commit": child_commit,
                            "candidate_state_id": "P1-r2b1",
                            "memory_snapshot": str(child_memory),
                            "system_state_dirty": False,
                            "status": "completed",
                        }],
                    },
                ],
            })
            write_json(parallel_dir / "result.json", {
                "schema_version": 1,
                "parallel_id": "P1",
                "status": "completed",
                "selected_branches": ["r2b1"],
            })

            result = promote_parallel_branch(
                target=target,
                parallel_dir=parallel_dir,
                branch_id="r2b1",
            )

            self.assertEqual(result["states_promoted"], ["P1-r1b1", "P1-r2b1"])
            self.assertEqual(result["state_id"], "P1-r2b1")
            self.assertEqual(git(target, "rev-parse", "HEAD"), child_commit)
            self.assertEqual(
                git(target, "rev-parse", "state/P1-r1b1^{commit}"), parent_commit
            )
            self.assertEqual(
                git(target, "rev-parse", "state/P1-r2b1^{commit}"), child_commit
            )
            self.assertIn(
                "derived_from: P1-r1b1",
                (target / "research_record/STATE.yaml").read_text(encoding="utf-8"),
            )

    def test_promotion_rolls_back_state_tags_head_and_memory_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.make_target(root)
            base_commit = git(target, "rev-parse", "HEAD")
            workspace = root / "candidate"
            candidate_commit = self.candidate(
                target,
                source_commit=base_commit,
                workspace=workspace,
                state_id="P1-r1b1",
                derived_from="S001",
                model="candidate",
            )
            (workspace / "research_record/RESEARCH_RECORD.yaml").write_text(
                record_text("candidate memory"), encoding="utf-8"
            )
            (workspace / "research_record/EXPLORE.md").write_bytes(
                (target / "research_record/EXPLORE.md").read_bytes()
            )

            parallel_dir = target / "research_record/runtime/parallel-rollback"
            base_memory = parallel_dir / "base-memory"
            branch_memory = parallel_dir / "branches/r1b1-memory"
            self.copy_memory(target, base_memory)
            self.copy_memory(workspace, branch_memory)
            write_json(parallel_dir / "manifest.json", {
                "schema_version": 1,
                "kind": "parallel",
                "parallel_id": "P1",
                "target": str(target.resolve()),
                "base_commit": base_commit,
                "base_memory_snapshot": str(base_memory),
                "rounds_log": [{
                    "round": 1,
                    "branches": [{
                        "kind": "replica",
                        "branch_id": "r1b1",
                        "parent_branch": "root",
                        "base_commit": base_commit,
                        "base_state": {"id": "S001", "git_tag": "state/S001"},
                        "workspace": str(workspace),
                        "candidate_commit": candidate_commit,
                        "candidate_state_id": "P1-r1b1",
                        "memory_snapshot": str(branch_memory),
                        "system_state_dirty": False,
                        "status": "completed",
                    }],
                }],
            })
            write_json(parallel_dir / "result.json", {
                "schema_version": 1,
                "parallel_id": "P1",
                "status": "completed",
                "selected_branches": ["r1b1"],
            })
            original_manifest = (parallel_dir / "manifest.json").read_bytes()
            original_memory = (target / "research_record/RESEARCH_RECORD.yaml").read_bytes()
            real_adopt = parallel_support.adopt_memory
            calls = 0

            def fail_once(snapshot: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise OSError("simulated memory adoption failure")
                real_adopt(snapshot, destination)

            with patch("research_agent.parallel_support.adopt_memory", side_effect=fail_once):
                with self.assertRaises(BootstrapError):
                    promote_parallel_branch(
                        target=target,
                        parallel_dir=parallel_dir,
                        branch_id="r1b1",
                    )

            self.assertEqual(git(target, "rev-parse", "HEAD"), base_commit)
            self.assertFalse(has_ref(target, "refs/tags/state/P1-r1b1"))
            self.assertEqual(
                (target / "system/model.py").read_text(encoding="utf-8"),
                "MODEL = 'baseline'\n",
            )
            self.assertEqual(
                (target / "research_record/RESEARCH_RECORD.yaml").read_bytes(),
                original_memory,
            )
            self.assertEqual((parallel_dir / "manifest.json").read_bytes(), original_manifest)


if __name__ == "__main__":
    unittest.main()
