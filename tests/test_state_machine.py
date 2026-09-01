from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent.cli import command_launch_inner, command_run, command_step


def git(target: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(target), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def usage_report() -> dict[str, object]:
    return {"runner": "codex", "accounting_status": "unavailable", "reason": "fixture telemetry unavailable"}


def make_target(root: Path) -> Path:
    target = root / "target"
    record = target / "research_record"
    (record / "runtime").mkdir(parents=True)
    (record / "VERSION").write_text("research-agent-record-v5\n", encoding="utf-8")
    (record / "SYSTEM_CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
    (record / "RESEARCH_METHOD.md").write_text("# Method\n", encoding="utf-8")
    (record / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
    (record / "RESEARCH_BRIEF.md").write_text("# Research Brief\n", encoding="utf-8")
    (record / "RESEARCH_RECORD.yaml").write_text("experiments: []\nmanual_interventions: []\n", encoding="utf-8")
    (record / "EXPLORE.md").write_text("# Explore\n", encoding="utf-8")
    (record / "OPTIMIZE.md").write_text("# Task Optimization\n", encoding="utf-8")
    (record / "ENGINEERING.md").write_text("# Engineering\n", encoding="utf-8")
    (record / "KNOWLEDGE.md").write_text("# Knowledge\n", encoding="utf-8")
    (record / "RESEARCH_INTUITION.md").write_text("# Research Intuition\n\n## Intuitions\n", encoding="utf-8")
    (record / "DO_BETTER.md").write_text("# How to Do Better\n\n## Lessons\n", encoding="utf-8")
    (target / "AGENTS.md").write_text("# Project instructions\n", encoding="utf-8")
    (target / "task.md").write_text("task\n", encoding="utf-8")
    (target / "PERSONAL.md").write_text("environment\n", encoding="utf-8")
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
        "research_record/archive/\n",
        encoding="utf-8",
    )

    git(target, "init", "-q")
    git(target, "config", "user.email", "research-agent@example.invalid")
    git(target, "config", "user.name", "Research Agent Test")
    git(target, "add", ".")
    git(target, "commit", "-qm", "baseline")
    return target


def write_brief(target: Path, cycle_id: int) -> None:
    runtime = target / "research_record" / "runtime"
    (runtime / "current-brief.json").write_text(
        json.dumps({
            "schema_version": 2,
            "cycle_id": cycle_id,
            "concerns": ["Execute one bounded iteration and return control."],
            "constraints": [],
            "budget": {},
        }),
        encoding="utf-8",
    )


def simulate_scientist_iteration(
    target: Path,
    environment: dict[str, str],
    *,
    offset: int = 0,
) -> int:
    cycle_id = int(environment["RESEARCH_AGENT_START_CYCLE"]) + offset
    write_brief(target, cycle_id)
    record = target / "research_record" / "RESEARCH_RECORD.yaml"
    record.write_text(f"experiments: []\nmanual_interventions: []\n# cycle {cycle_id}\n", encoding="utf-8")
    return cycle_id


def write_meta_result(environment: dict[str, str], *, status: str) -> None:
    Path(environment["RESEARCH_AGENT_CYCLE_RESULT_FILE"]).write_text(
        json.dumps({
            "status": status,
            "summary": f"run ended with {status}",
            "next_action": "continue from project state" if status == "continue" else "stop",
        }),
        encoding="utf-8",
    )


class StateMachineTests(unittest.TestCase):
    def test_separate_steps_use_monotonic_target_cycle_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = make_target(root)
            observed: list[int] = []

            def fake_run(_invocation: object, *, environment: dict[str, str], **_kwargs: object) -> int:
                observed.append(simulate_scientist_iteration(target, environment))
                write_meta_result(environment, status="converged")
                return 0

            args = argparse.Namespace(
                target=target, cli="codex", allow_edits=True,
                output_mode="quiet", model=None,
            )
            with (
                patch("research_agent.cli.create_run_directory", side_effect=(("run-1", root / "run-1"), ("run-2", root / "run-2"))),
                patch("research_agent.cli.collect", side_effect=lambda *_args, **_kwargs: usage_report()),
                patch("research_agent.cli.run_invocation", side_effect=fake_run),
            ):
                self.assertEqual(command_step(args), 0)
                self.assertEqual(command_step(args), 0)

            self.assertEqual(observed, [1, 2])

    def test_run_uses_one_meta_process_for_multiple_scientist_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = make_target(root)

            def fake_run(invocation: object, *, environment: dict[str, str], **_kwargs: object) -> int:
                self.assertIn('model_reasoning_effort="max"', invocation.argv)  # type: ignore[attr-defined]
                self.assertIn("--effort max", invocation.stdin_text or "")  # type: ignore[attr-defined]
                self.assertEqual(environment["RESEARCH_AGENT_META_EFFORT"], "max")
                self.assertEqual(environment["RESEARCH_AGENT_SCIENTIST_EFFORT"], "max")
                self.assertEqual(simulate_scientist_iteration(target, environment, offset=0), 1)
                self.assertEqual(simulate_scientist_iteration(target, environment, offset=1), 2)
                write_meta_result(environment, status="converged")
                return 0

            args = argparse.Namespace(
                command="run", target=target, cli="codex",
                allow_edits=True, max_cycles=5, output_mode="quiet", model=None, effort="max",
            )
            with (
                patch("research_agent.cli.create_run_directory", return_value=("run-id", root / "run")),
                patch("research_agent.cli.collect", side_effect=lambda *_args, **_kwargs: usage_report()),
                patch("research_agent.cli.run_invocation", side_effect=fake_run) as runner,
            ):
                self.assertEqual(command_run(args), 0)
            self.assertEqual(runner.call_count, 1)
            run_metadata = json.loads((root / "run" / "run.json").read_text(encoding="utf-8"))
            self.assertNotIn("cycles_completed", run_metadata)
            self.assertEqual(run_metadata["terminal_status"], "converged")
            meta = root / "run" / "meta"
            self.assertTrue((meta / "result.json").is_file())
            self.assertTrue((meta / "usage.json").is_file())
            self.assertFalse((meta / "session.json").exists())
            self.assertFalse((meta / "usage-before.json").exists())
            self.assertFalse((meta / "usage-after.json").exists())

    def test_launch_inner_does_not_enforce_delegated_cycle_range(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = make_target(Path(temporary))
            args = argparse.Namespace(target=target, cli="codex", allow_edits=True, model=None, prompt=None)
            environment = {
                "RESEARCH_AGENT_START_CYCLE": "4",
                "RESEARCH_AGENT_MAX_CYCLES": "2",
                "RESEARCH_AGENT_META_SESSION": "1",
                "RESEARCH_AGENT_ROLE": "META",
            }
            write_brief(target, 99)
            with (
                patch.dict(os.environ, environment, clear=False),
                patch("research_agent.cli.run_invocation", return_value=0) as runner,
            ):
                self.assertEqual(command_launch_inner(args), 0)
            self.assertEqual(runner.call_count, 1)

    def test_direct_launch_inner_is_supported_without_meta_session(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = make_target(Path(temporary))
            args = argparse.Namespace(target=target, cli="codex", allow_edits=True, model=None, prompt=None)
            write_brief(target, 1)
            environment = os.environ.copy()
            environment.pop("RESEARCH_AGENT_META_SESSION", None)
            environment.pop("RESEARCH_AGENT_ROLE", None)
            with (
                patch.dict(os.environ, environment, clear=True),
                patch("research_agent.cli.run_invocation", return_value=0) as runner,
            ):
                self.assertEqual(command_launch_inner(args), 0)
            self.assertEqual(runner.call_count, 1)

    def test_missing_handoff_requires_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = make_target(root)
            args = argparse.Namespace(
                target=target, cli="codex", allow_edits=True,
                output_mode="quiet", model=None,
            )
            with (
                patch("research_agent.cli.create_run_directory", return_value=("run-id", root / "run")),
                patch("research_agent.cli.collect", side_effect=lambda *_args, **_kwargs: usage_report()),
                patch("research_agent.cli.run_invocation", return_value=0),
            ):
                self.assertEqual(command_step(args), 4)

    def test_missing_injected_meta_file_closes_the_run_as_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = make_target(root)
            (target / "AGENTS.md").unlink()
            args = argparse.Namespace(
                target=target, cli="codex", allow_edits=True,
                output_mode="quiet", model=None,
            )
            with (
                patch("research_agent.cli.create_run_directory", return_value=("run-id", root / "run")),
                patch("research_agent.cli.collect", side_effect=lambda *_args, **_kwargs: usage_report()),
                patch("research_agent.cli.run_invocation") as runner,
            ):
                self.assertEqual(command_step(args), 127)

            metadata = json.loads((root / "run" / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["status"], "closed")
            self.assertEqual(metadata["terminal_status"], "failed")
            self.assertEqual(metadata["exit_code"], 127)
            self.assertIn("cannot inject META_PROJECT_INSTRUCTIONS", (root / "run/meta/meta.log").read_text(encoding="utf-8"))
            runner.assert_not_called()

    def test_cycle_keeps_research_memory_outside_git(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = make_target(root)

            def fake_run(_invocation: object, *, environment: dict[str, str], **_kwargs: object) -> int:
                simulate_scientist_iteration(target, environment)
                write_meta_result(environment, status="converged")
                return 0

            args = argparse.Namespace(
                target=target, cli="codex", allow_edits=True,
                output_mode="quiet", model=None,
            )
            with (
                patch("research_agent.cli.create_run_directory", return_value=("run-id", root / "run")),
                patch("research_agent.cli.collect", side_effect=lambda *_args, **_kwargs: usage_report()),
                patch("research_agent.cli.run_invocation", side_effect=fake_run),
            ):
                self.assertEqual(command_step(args), 0)

            self.assertEqual(git(target, "log", "-1", "--format=%s"), "baseline")
            tracked = set(git(target, "ls-files").splitlines())
            self.assertNotIn("research_record/RESEARCH_RECORD.yaml", tracked)
            self.assertIn("# cycle 1", (target / "research_record" / "RESEARCH_RECORD.yaml").read_text(encoding="utf-8"))
            self.assertFalse((target / "research_record" / "control").exists())


if __name__ == "__main__":
    unittest.main()
