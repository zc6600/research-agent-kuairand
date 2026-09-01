from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from research_agent.state import create_state, materialize_state


def git(target: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(target), *args],
        check=True, capture_output=True, text=True,
    )
    return completed.stdout.strip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def state_text(state_id: str, parent: str | None, report: str) -> str:
    derived = parent if parent is not None else "null"
    return (
        f"id: {state_id}\n"
        f"git_tag: state/{state_id}\n"
        f"derived_from: {derived}\n"
        f"scientist_report: {report}\n"
    )


class StateMaterializationTests(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        target = root / "target"
        target.mkdir()
        git(target, "init", "-q")
        git(target, "config", "user.email", "research-agent@example.invalid")
        git(target, "config", "user.name", "Research Agent Test")

        # Mutable research memory belongs to the current worktree and is not
        # versioned with States. Scientist reports are append-only provenance
        # kept in that current research world.
        write(
            target / ".gitignore",
            "research_record/RESEARCH_RECORD.yaml\n"
            "research_record/EXPLORE.md\n"
            "research_record/ENGINEERING.md\n"
            "research_record/KNOWLEDGE.md\n"
            "research_record/RESEARCH_INTUITION.md\n"
            "research_record/DO_BETTER.md\n"
            "research_record/reports/\n"
            "research_record/logs/\n"
            "research_record/archive/\n",
        )
        write(target / "research_record" / "RESEARCH_RECORD.yaml", "events: [E001]\n")
        write(target / "research_record" / "EXPLORE.md", "# Explore\ninitial\n")
        write(target / "research_record" / "ENGINEERING.md", "# Engineering\ninitial\n")
        write(target / "research_record" / "KNOWLEDGE.md", "# Knowledge\ninitial\n")
        write(target / "research_record" / "RESEARCH_INTUITION.md", "# Intuition\ninitial\n")
        write(target / "research_record" / "DO_BETTER.md", "# How to Do Better\ninitial\n")
        write(target / "task.md", "current task\n")

        report1 = "research_record/reports/cycle-1.md"
        report2 = "research_record/reports/cycle-2.md"
        report3 = "research_record/reports/cycle-3.md"
        write(target / report1, "Scientist session 1\n")
        write(target / report2, "Scientist session 2\n")
        write(target / report3, "Scientist session 3\n")

        # S001 versions only the reusable system plus its matching META-authored State record.
        write(target / "system" / "model.py", "MODEL = 'S001'\n")
        write(target / "system" / "s001_only.py", "VALUE = 1\n")
        write(target / "research_record" / "STATE.yaml", state_text("S001", None, report1))
        git(target, "add", ".gitignore", "system", "research_record/STATE.yaml")
        git(target, "commit", "-qm", "state S001")
        git(target, "tag", "-a", "state/S001", "-m", "S001")

        # Research memory advances independently while later States retain new implementations.
        write(target / "research_record" / "RESEARCH_RECORD.yaml", "events: [E001, E002]\n")
        write(target / "research_record" / "EXPLORE.md", "# Explore\nlatest\n")
        write(target / "research_record" / "ENGINEERING.md", "# Engineering\nlearned E002\n")
        write(target / "system" / "model.py", "MODEL = 'S002'\n")
        (target / "system" / "s001_only.py").unlink()
        write(target / "system" / "s002_only.py", "VALUE = 2\n")
        write(target / "research_record" / "STATE.yaml", state_text("S002", "S001", report2))
        git(target, "add", "-A", "--", "system", "research_record/STATE.yaml")
        git(target, "commit", "-qm", "state S002")
        git(target, "tag", "-a", "state/S002", "-m", "S002")

        write(target / "research_record" / "RESEARCH_RECORD.yaml", "events: [E001, E002, E003]\n")
        write(target / "research_record" / "EXPLORE.md", "# Explore\nlatest\n")
        write(target / "research_record" / "ENGINEERING.md", "# Engineering\nlatest\n")
        write(target / "research_record" / "KNOWLEDGE.md", "# Knowledge\nlatest\n")
        write(target / "research_record" / "RESEARCH_INTUITION.md", "# Intuition\nlatest\n")
        write(target / "research_record" / "DO_BETTER.md", "# How to Do Better\nlatest\n")
        write(target / "system" / "model.py", "MODEL = 'S003'\n")
        (target / "system" / "s002_only.py").unlink()
        write(target / "system" / "s003_only.py", "VALUE = 3\n")
        write(target / "research_record" / "STATE.yaml", state_text("S003", "S002", report3))
        git(target, "add", "-A", "--", "system", "research_record/STATE.yaml")
        git(target, "commit", "-qm", "state S003")
        git(target, "tag", "-a", "state/S003", "-m", "S003")

        tracked = set(git(target, "ls-files").splitlines())
        self.assertIn("research_record/STATE.yaml", tracked)
        self.assertIn("system/model.py", tracked)
        self.assertNotIn("research_record/RESEARCH_RECORD.yaml", tracked)
        self.assertNotIn("research_record/EXPLORE.md", tracked)
        self.assertNotIn("research_record/ENGINEERING.md", tracked)
        self.assertNotIn("research_record/KNOWLEDGE.md", tracked)
        self.assertNotIn("research_record/RESEARCH_INTUITION.md", tracked)
        self.assertNotIn("research_record/DO_BETTER.md", tracked)
        self.assertNotIn(report1, tracked)
        return target

    def assert_latest_research_memory(self, target: Path) -> None:
        self.assertEqual((target / "research_record" / "RESEARCH_RECORD.yaml").read_text(), "events: [E001, E002, E003]\n")
        self.assertEqual((target / "research_record" / "EXPLORE.md").read_text(), "# Explore\nlatest\n")
        self.assertEqual((target / "research_record" / "ENGINEERING.md").read_text(), "# Engineering\nlatest\n")
        self.assertEqual((target / "research_record" / "KNOWLEDGE.md").read_text(), "# Knowledge\nlatest\n")
        self.assertEqual((target / "research_record" / "RESEARCH_INTUITION.md").read_text(), "# Intuition\nlatest\n")
        self.assertEqual((target / "research_record" / "DO_BETTER.md").read_text(), "# How to Do Better\nlatest\n")
        self.assertEqual((target / "task.md").read_text(), "current task\n")

    def test_continuous_materialization_changes_only_state_controlled_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_repo(Path(temporary))
            head_before = git(target, "rev-parse", "HEAD")

            result1 = materialize_state(target, "S001")
            self.assertEqual(result1.scientist_report, "research_record/reports/cycle-1.md")
            self.assertEqual((target / "system" / "model.py").read_text(), "MODEL = 'S001'\n")
            self.assertTrue((target / "system" / "s001_only.py").is_file())
            self.assertFalse((target / "system" / "s003_only.py").exists())
            self.assertEqual(
                (target / "research_record" / "STATE.yaml").read_text(),
                state_text("S001", None, "research_record/reports/cycle-1.md"),
            )
            self.assert_latest_research_memory(target)

            result2 = materialize_state(target, "S002")
            self.assertEqual(result2.scientist_report, "research_record/reports/cycle-2.md")
            self.assertEqual((target / "system" / "model.py").read_text(), "MODEL = 'S002'\n")
            self.assertTrue((target / "system" / "s002_only.py").is_file())
            self.assertFalse((target / "system" / "s001_only.py").exists())
            self.assertEqual(
                (target / "research_record" / "STATE.yaml").read_text(),
                state_text("S002", "S001", "research_record/reports/cycle-2.md"),
            )
            self.assert_latest_research_memory(target)

            result3 = materialize_state(target, "S003")
            self.assertEqual(result3.scientist_report, "research_record/reports/cycle-3.md")
            self.assertEqual((target / "system" / "model.py").read_text(), "MODEL = 'S003'\n")
            self.assertTrue((target / "system" / "s003_only.py").is_file())
            self.assertEqual(
                (target / "research_record" / "STATE.yaml").read_text(),
                state_text("S003", "S002", "research_record/reports/cycle-3.md"),
            )
            self.assert_latest_research_memory(target)
            self.assertEqual(git(target, "rev-parse", "HEAD"), head_before)

    def test_mutable_research_memory_does_not_block_materialization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_repo(Path(temporary))
            record = target / "research_record" / "RESEARCH_RECORD.yaml"
            record.write_text("events: [E001, E002, E003, E004]\n", encoding="utf-8")
            materialize_state(target, "S001")
            self.assertEqual(record.read_text(), "events: [E001, E002, E003, E004]\n")

    def test_missing_state_report_blocks_historical_materialization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_repo(Path(temporary))
            (target / "research_record" / "reports" / "cycle-1.md").unlink()
            with self.assertRaisesRegex(ValueError, "provenance is incomplete"):
                materialize_state(target, "S001")

    def test_uncommitted_system_work_blocks_materialization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_repo(Path(temporary))
            write(target / "system" / "model.py", "MODEL = 'uncommitted'\n")
            with self.assertRaisesRegex(ValueError, "uncommitted system changes"):
                materialize_state(target, "S001")

    def test_historical_state_metadata_cannot_be_edited_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_repo(Path(temporary))
            state = target / "research_record" / "STATE.yaml"
            state.write_text(state.read_text() + "performance:\n  primary: 0.9\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "historical State metadata cannot be edited"):
                materialize_state(target, "S001")

    def test_create_state_requires_existing_report_and_committed_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_repo(Path(temporary))
            write(target / "system" / "model.py", "MODEL = 'S004'\n")
            write(target / "research_record" / "STATE.yaml", "id: S004\ngit_tag: state/S004\nderived_from: S003\n")
            with self.assertRaisesRegex(ValueError, "scientist_report"):
                create_state(target, "S004")

            report = "research_record/reports/cycle-4.md"
            write(target / "research_record" / "STATE.yaml", state_text("S004", "S003", report))
            with self.assertRaisesRegex(ValueError, "Scientist report is missing"):
                create_state(target, "S004")

            write(target / report, "Scientist session 4\n")
            with self.assertRaisesRegex(ValueError, "fully committed"):
                create_state(target, "S004")

            git(target, "add", "-A", "--", "system", "research_record/STATE.yaml")
            git(target, "commit", "-qm", "state S004")
            result = create_state(target, "S004")
            self.assertEqual(result.git_tag, "state/S004")
            self.assertEqual(git(target, "rev-parse", "state/S004^{}"), git(target, "rev-parse", "HEAD"))
            with self.assertRaisesRegex(ValueError, "immutable"):
                create_state(target, "S004")


if __name__ == "__main__":
    unittest.main()
