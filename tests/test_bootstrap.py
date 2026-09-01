from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent.bootstrap import (
    BootstrapError,
    copy_project_inputs,
    ensure_target_git_root,
    initialize_project,
    prepare_target,
    require_supported_record,
)
from research_agent.cli import build_parser, command_init, command_run, command_step

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "assets" / "project-template"


def git(target: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(target), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


class BootstrapTests(unittest.TestCase):
    def test_existing_project_is_initialized_without_replacing_agents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "competition"
            target.mkdir()
            (target / "task.md").write_text("# Task\n", encoding="utf-8")
            (target / "PERSONAL.md").write_text("# Environment\n", encoding="utf-8")
            (target / "AGENTS.md").write_text("# Existing rules\n", encoding="utf-8")
            (target / ".gitignore").write_text("custom-output/\n", encoding="utf-8")

            result = initialize_project(target, TEMPLATE_ROOT)

            record = target / "research_record"
            for name in (
                "SKILL.md",
                "SYSTEM_CONTRACT.md",
                "RESEARCH_METHOD.md",
                "RESEARCH_BRIEF.md",
                "RESEARCH_RECORD.yaml",
                "EXPLORE.md",
                "OPTIMIZE.md",
                "ENGINEERING.md",
                "KNOWLEDGE.md",
                "RESEARCH_INTUITION.md",
                "DO_BETTER.md",
            ):
                with self.subTest(name=name):
                    self.assertTrue((record / name).is_file())
            self.assertFalse((record / "SYSTEM_SCOPE.json").exists())
            self.assertEqual((record / "VERSION").read_text().strip(), "research-agent-record-v5")
            self.assertEqual(
                (record / "SYSTEM_CONTRACT.md").read_bytes(),
                (TEMPLATE_ROOT / "research_record" / "SYSTEM_CONTRACT.md").read_bytes(),
            )
            self.assertFalse((record / "META_POLICY.md").exists())
            self.assertFalse((record / "PROTOCOL.md").exists())
            self.assertTrue((record / "logs" / "README.md").is_file())
            self.assertTrue((record / "runtime" / ".gitignore").is_file())
            self.assertFalse((record / "control").exists())
            ignore = (target / ".gitignore").read_text(encoding="utf-8")
            for path in (
                "research_record/RESEARCH_RECORD.yaml",
                "research_record/RESEARCH_BRIEF.md",
                "research_record/EXPLORE.md",
                "research_record/OPTIMIZE.md",
                "research_record/ENGINEERING.md",
                "research_record/KNOWLEDGE.md",
                "research_record/RESEARCH_INTUITION.md",
                "research_record/DO_BETTER.md",
            ):
                with self.subTest(path=path):
                    self.assertIn(path, ignore)
            self.assertNotIn("research_record/STATE.yaml\n", ignore)
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertTrue(agents.startswith("# Existing rules\n"))
            self.assertEqual(agents.count("BEGIN research-agent project contract"), 1)
            self.assertEqual(result.agents_action, "appended")
            self.assertEqual((target / "CLAUDE.md").read_text(encoding="utf-8"), "@AGENTS.md\n")

    def test_init_tracks_contract_but_not_mutable_research_memory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            (target / "task.md").write_text("task\n", encoding="utf-8")
            (target / "PERSONAL.md").write_text("environment\n", encoding="utf-8")
            git(target, "init", "-q")
            git(target, "config", "user.email", "research-agent@example.invalid")
            git(target, "config", "user.name", "Research Agent Test")

            args = build_parser().parse_args(["init", "--target", str(target)])
            self.assertEqual(command_init(args), 0)

            tracked = set(git(target, "ls-files").splitlines())
            self.assertIn("research_record/SYSTEM_CONTRACT.md", tracked)
            self.assertIn("research_record/RESEARCH_METHOD.md", tracked)
            self.assertIn("research_record/SKILL.md", tracked)
            self.assertIn("research_record/VERSION", tracked)
            for path in (
                "research_record/RESEARCH_RECORD.yaml",
                "research_record/RESEARCH_BRIEF.md",
                "research_record/EXPLORE.md",
                "research_record/OPTIMIZE.md",
                "research_record/ENGINEERING.md",
                "research_record/KNOWLEDGE.md",
                "research_record/RESEARCH_INTUITION.md",
                "research_record/DO_BETTER.md",
            ):
                with self.subTest(path=path):
                    self.assertNotIn(path, tracked)

    def test_init_refuses_unrelated_staged_files_in_unborn_repo(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            (target / "task.md").write_text("task\n", encoding="utf-8")
            (target / "PERSONAL.md").write_text("environment\n", encoding="utf-8")
            (target / "secret.txt").write_text("do not commit\n", encoding="utf-8")
            git(target, "init", "-q")
            git(target, "config", "user.email", "research-agent@example.invalid")
            git(target, "config", "user.name", "Research Agent Test")
            git(target, "add", "secret.txt")

            args = build_parser().parse_args(["init", "--target", str(target)])
            with self.assertRaisesRegex(BootstrapError, "unrelated files are staged"):
                command_init(args)

            self.assertFalse((target / "research_record").exists())
            self.assertEqual(git(target, "diff", "--cached", "--name-only"), "secret.txt")
            self.assertNotEqual(
                subprocess.run(
                    ["git", "-C", str(target), "rev-parse", "--verify", "HEAD"],
                    check=False,
                    capture_output=True,
                    text=True,
                ).returncode,
                0,
            )

    def test_init_requires_task_and_personal_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            with self.assertRaisesRegex(BootstrapError, "task.md, PERSONAL.md"):
                initialize_project(target, TEMPLATE_ROOT)
            self.assertFalse((target / "research_record").exists())

    def test_init_refuses_to_replace_existing_research_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / "task.md").write_text("task\n", encoding="utf-8")
            (target / "PERSONAL.md").write_text("environment\n", encoding="utf-8")
            (target / "research_record").mkdir()
            with self.assertRaisesRegex(BootstrapError, "initialize a clean project"):
                initialize_project(target, TEMPLATE_ROOT)

    def test_cycle_launch_rejects_wrong_record_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            record = target / "research_record"
            record.mkdir()
            (record / "VERSION").write_text("research-agent-record-v4\n", encoding="utf-8")
            with self.assertRaisesRegex(BootstrapError, "expected 'research-agent-record-v5'"):
                require_supported_record(target)

    def test_cycle_launch_refuses_incomplete_record_v5(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            record = target / "research_record"
            record.mkdir()
            (record / "VERSION").write_text("research-agent-record-v5\n", encoding="utf-8")
            (record / "SYSTEM_CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
            (record / "RESEARCH_METHOD.md").write_text("# Method\n", encoding="utf-8")
            (record / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
            with self.assertRaisesRegex(BootstrapError, "incomplete.*[Ii]nitialize a clean project"):
                require_supported_record(target)

    def test_prepare_new_target_creates_only_the_requested_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            requested = Path(temporary) / "new-project"
            target, created = prepare_target(target=None, new_target=requested)
            self.assertTrue(created)
            self.assertEqual(target, requested.resolve())
            self.assertEqual(list(target.iterdir()), [])

    def test_generic_target_requires_own_git_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary) / "parent"
            child = parent / "child"
            child.mkdir(parents=True)
            git(parent, "init", "-q")
            with self.assertRaisesRegex(BootstrapError, "own Git root"):
                ensure_target_git_root(child, create_if_missing=False)

    def test_copy_project_inputs_preserves_explicit_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            target.mkdir()
            task = root / "source-task.md"
            personal = root / "source-personal.md"
            task.write_text("KuaiRand-Pure task\n", encoding="utf-8")
            personal.write_text("Observable environment\n", encoding="utf-8")
            copy_project_inputs(target, task_source=task, personal_source=personal)
            self.assertEqual((target / "task.md").read_text(), "KuaiRand-Pure task\n")
            self.assertEqual((target / "PERSONAL.md").read_text(), "Observable environment\n")

    def test_init_requires_explicit_target_or_new(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["init"])

    def test_migrate_command_does_not_exist(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["migrate", "--target", "/tmp/project"])

    def test_new_init_requires_task_and_personal(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["init", "--new", "/tmp/project"])
        with self.assertRaisesRegex(BootstrapError, "--new requires both --task and --personal"):
            command_init(args)

    def test_cycle_output_modes_parse(self) -> None:
        parser = build_parser()
        normal = parser.parse_args(["step", "--cli", "codex", "--target", "/tmp/project", "--allow-edits"])
        verbose = parser.parse_args(["step", "--cli", "codex", "--target", "/tmp/project", "--allow-edits", "--verbose"])
        quiet = parser.parse_args(["step", "--cli", "codex", "--target", "/tmp/project", "--allow-edits", "--quiet"])
        luna = parser.parse_args(["step", "--cli", "codex", "--model", "gpt-5.6-luna", "--target", "/tmp/project", "--allow-edits"])
        max_effort = parser.parse_args(["step", "--cli", "codex", "--effort", "max", "--target", "/tmp/project", "--allow-edits"])
        self.assertEqual(normal.output_mode, "normal")
        self.assertEqual(verbose.output_mode, "verbose")
        self.assertEqual(quiet.output_mode, "quiet")
        self.assertEqual(luna.model, "gpt-5.6-luna")
        self.assertEqual(max_effort.effort, "max")

    def test_cycle_commands_require_existing_targets(self) -> None:
        parser = build_parser()
        for command in ("step", "run", "resume"):
            argv = [command, "--cli", "codex", "--new", "/tmp/project", "--allow-edits"]
            if command != "step":
                argv.extend(["--max-cycles", "2"])
            with self.subTest(command=command), self.assertRaises(SystemExit):
                parser.parse_args(argv)

    def test_active_meta_cannot_recursively_launch_cycle_commands(self) -> None:
        step = build_parser().parse_args(["step", "--cli", "codex", "--target", "/tmp/project", "--allow-edits"])
        run = build_parser().parse_args(["run", "--cli", "codex", "--target", "/tmp/project", "--allow-edits", "--max-cycles", "2"])
        with patch.dict("os.environ", {"RESEARCH_AGENT_META_SESSION": "1"}):
            with self.assertRaisesRegex(BootstrapError, "active META session"):
                command_step(step)
            with self.assertRaisesRegex(BootstrapError, "active META session"):
                command_run(run)


if __name__ == "__main__":
    unittest.main()
