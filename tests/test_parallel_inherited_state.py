from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from research_agent.parallel import promote_parallel_branch
from research_agent.parallel_support import snapshot_memory
from research_agent.runtime import write_json


def git(target: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(target), *args],
        check=True, capture_output=True, text=True,
    )
    return completed.stdout.strip()


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


class ParallelInheritedStateTests(unittest.TestCase):
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

    def test_diagnostic_child_promotes_inherited_candidate_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.make_target(root)
            base_commit = git(target, "rev-parse", "HEAD")

            primary = root / "primary"
            subprocess.run(
                ["git", "-C", str(target), "worktree", "add", "--detach", str(primary), base_commit],
                check=True, capture_output=True, text=True,
            )
            (primary / "system/model.py").write_text("MODEL = 'primary'\n", encoding="utf-8")
            (primary / "research_record/STATE.yaml").write_text(
                "id: P1-r1b1\ngit_tag: state/P1-r1b1\nderived_from: S001\n"
                "scientist_report: research_record/reports/init.md\n",
                encoding="utf-8",
            )
            git(primary, "add", "system", "research_record/STATE.yaml")
            git(primary, "commit", "-qm", "candidate primary state")
            primary_commit = git(primary, "rev-parse", "HEAD")

            child = root / "child"
            subprocess.run(
                ["git", "-C", str(target), "worktree", "add", "--detach", str(child), primary_commit],
                check=True, capture_output=True, text=True,
            )
            (child / "research_record/EXPLORE.md").write_bytes(
                (target / "research_record/EXPLORE.md").read_bytes()
            )
            (child / "research_record/RESEARCH_RECORD.yaml").write_text(
                record_text("diagnostic synthesis learned something"),
                encoding="utf-8",
            )

            parallel_dir = target / "research_record/runtime/parallel-inherited"
            base_memory = parallel_dir / "base-memory"
            child_memory = parallel_dir / "branches/s1-memory"
            snapshot_memory(target, base_memory, include_meta=False)
            snapshot_memory(child, child_memory, include_meta=False)

            write_json(parallel_dir / "manifest.json", {
                "schema_version": 1,
                "kind": "parallel",
                "parallel_id": "P1",
                "target": str(target.resolve()),
                "base_commit": base_commit,
                "base_memory_snapshot": str(base_memory),
                "rounds_log": [{
                    "round": 1,
                    "branches": [
                        {
                            "kind": "replica",
                            "branch_id": "r1b1",
                            "parent_branch": "root",
                            "base_commit": base_commit,
                            "base_state": {"id": "S001", "git_tag": "state/S001"},
                            "workspace": str(primary),
                            "candidate_commit": primary_commit,
                            "candidate_state_id": "P1-r1b1",
                            "system_state_dirty": False,
                            "status": "completed",
                        },
                        {
                            "kind": "synthesis",
                            "branch_id": "s1",
                            "parent_branch": "r1b1",
                            "primary_branch": "r1b1",
                            "informed_by": ["r1b2"],
                            "base_commit": primary_commit,
                            "base_state": {"id": "P1-r1b1", "git_tag": "state/P1-r1b1"},
                            "workspace": str(child),
                            "candidate_commit": primary_commit,
                            "candidate_state_id": "P1-s1",
                            "memory_snapshot": str(child_memory),
                            "system_state_dirty": False,
                            "status": "completed",
                        },
                    ],
                }],
            })
            write_json(parallel_dir / "result.json", {
                "schema_version": 1,
                "parallel_id": "P1",
                "status": "completed",
                "selected_branches": ["s1"],
            })

            result = promote_parallel_branch(
                target=target,
                parallel_dir=parallel_dir,
                branch_id="s1",
            )

            self.assertTrue(result["research_memory_adopted"])
            self.assertTrue(result["state_promoted"])
            self.assertEqual(result["state_id"], "P1-r1b1")
            self.assertEqual(git(target, "rev-parse", "HEAD"), primary_commit)
            self.assertEqual(git(target, "rev-parse", "state/P1-r1b1^{commit}"), primary_commit)
            self.assertIn(
                "diagnostic synthesis learned something",
                (target / "research_record/RESEARCH_RECORD.yaml").read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
