from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent.cli import command_launch_inner
from research_agent.launcher import build_inner_invocation, build_meta_invocation, run_invocation
from research_agent.runners import get_adapter
from research_agent.runners.base import Invocation
from research_agent.runtime import create_run_directory


def git(target: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(target), *args],
        check=True, capture_output=True, text=True,
    )
    return completed.stdout.strip()


def interrupt_when_ready(ready: Path) -> None:
    deadline = time.monotonic() + 5
    while not ready.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    os.kill(os.getpid(), signal.SIGINT)


def interrupt_fixture(directory: Path) -> tuple[Invocation, Path, Path]:
    ready = directory / "ready.txt"
    marker = directory / "signal.txt"
    script = directory / "runner.py"
    script.write_text(
        """import signal
import sys
import time
from pathlib import Path

ready = Path(sys.argv[1])
marker = Path(sys.argv[2])

def stop(_signum, _frame):
    marker.write_text('SIGINT', encoding='utf-8')
    raise SystemExit(130)

signal.signal(signal.SIGINT, stop)
ready.write_text('ready', encoding='utf-8')
while True:
    time.sleep(0.05)
""",
        encoding="utf-8",
    )
    return Invocation((sys.executable, str(script), str(ready), str(marker)), directory), ready, marker


class RunnerCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.skill_root = self.root
        self.target = Path(self.temporary.name) / "competition"
        record = self.target / "research_record"
        (record / "runtime").mkdir(parents=True)
        (self.target / "AGENTS.md").write_text("# Project instructions\n", encoding="utf-8")
        (self.target / "task.md").write_text("# Task\n", encoding="utf-8")
        (self.target / "PERSONAL.md").write_text("# Personal\n", encoding="utf-8")
        (record / "SKILL.md").write_text("# Injected Scientist Skill\nscientist instructions\n", encoding="utf-8")
        for name, heading in (
            ("SYSTEM_CONTRACT.md", "Contract"),
            ("RESEARCH_METHOD.md", "Method"),
            ("RESEARCH_BRIEF.md", "Brief"),
            ("EXPLORE.md", "Explore"),
            ("OPTIMIZE.md", "Optimize"),
            ("ENGINEERING.md", "Engineering"),
            ("KNOWLEDGE.md", "Knowledge"),
            ("RESEARCH_INTUITION.md", "Intuition"),
            ("DO_BETTER.md", "Do Better"),
        ):
            (record / name).write_text(f"# {heading}\n{name} content\n", encoding="utf-8")
        (record / "RESEARCH_RECORD.yaml").write_text("experiments: []\n", encoding="utf-8")
        (record / "runtime" / "current-brief.json").write_text(
            '{"schema_version": 2, "cycle_id": 3, "concerns": [], "constraints": [], "budget": {}}\n',
            encoding="utf-8",
        )

    def meta(self, cli: str):
        return build_meta_invocation(
            cli=cli,
            target=self.target,
            cycle_result=Path("/runtime/result.json"),
            start_cycle_id=3,
            max_cycles=4,
            allow_edits=True,
        )

    def test_all_meta_runners_use_target_as_working_directory(self) -> None:
        for cli in ("codex", "claude", "opencode", "agy"):
            with self.subTest(cli=cli):
                self.assertEqual(self.meta(cli).cwd, self.target)

    def test_meta_runners_do_not_use_workspace_mount_flags(self) -> None:
        for cli in ("codex", "claude", "agy"):
            with self.subTest(cli=cli):
                self.assertNotIn("--add-dir", self.meta(cli).argv)

    def test_claude_meta_uses_normal_project_environment(self) -> None:
        invocation = self.meta("claude")
        self.assertNotIn("--safe-mode", invocation.argv)
        self.assertIn("--permission-mode", invocation.argv)
        index = invocation.argv.index("--permission-mode")
        self.assertEqual(invocation.argv[index + 1], "acceptEdits")

    def test_codex_meta_injects_canonical_runtime_context_without_skill(self) -> None:
        invocation = self.meta("codex")
        self.assertEqual(invocation.argv[:2], ("codex", "exec"))
        self.assertIn("-C", invocation.argv)
        self.assertIn(str(self.target), invocation.argv)
        sandbox_index = invocation.argv.index("--sandbox")
        self.assertEqual(invocation.argv[sandbox_index + 1], "danger-full-access")
        self.assertEqual(invocation.argv[-1], "-")
        prompt = invocation.stdin_text or ""
        self.assertNotIn("<<< RESEARCH_AGENT_INJECTED META_SKILL >>>", prompt)
        self.assertNotIn((self.skill_root / "SKILL.md").read_text(encoding="utf-8").rstrip(), prompt)
        self.assertIn("META_TASK", prompt)
        self.assertIn("# Task", prompt)
        self.assertIn("META_RESEARCH_RECORD", prompt)
        self.assertIn("Do not open, read, search, or otherwise inspect `research_record/SKILL.md`", prompt)
        self.assertIn("target files required for META startup", prompt)
        self.assertIn("cycle ids 3 through 6", prompt)
        self.assertIn("research-agent launch-inner", prompt)
        self.assertIn("/runtime/result.json", prompt)
        self.assertIn("do not open their source files merely to retrieve them", prompt)
        self.assertGreater(prompt.index("Runtime precedence:"), prompt.index("<<< END RESEARCH_AGENT_INJECTED META_DO_BETTER >>>"))

    def test_scientist_launch_prompt_injects_startup_files_and_coordination_brief(self) -> None:
        invocation = build_inner_invocation(
            cli="codex", target=self.target,
            allow_edits=True, prompt=None,
        )
        self.assertIn("--approve-for-me", invocation.argv)
        self.assertNotIn("danger-full-access", invocation.argv)
        self.assertEqual(invocation.argv[-1], "-")
        prompt = invocation.stdin_text or ""
        brief_path = self.target / "research_record" / "runtime" / "current-brief.json"
        self.assertNotIn("<<< RESEARCH_AGENT_INJECTED SCIENTIST_SKILL >>>", prompt)
        self.assertNotIn("# Injected Scientist Skill", prompt)
        for label, content in (
            ("SCIENTIST_PROJECT_INSTRUCTIONS", "# Project instructions"),
            ("SCIENTIST_TASK", "# Task"),
            ("SCIENTIST_PERSONAL", "# Personal"),
            ("SCIENTIST_SYSTEM_CONTRACT", "# Contract"),
            ("SCIENTIST_RESEARCH_METHOD", "# Method"),
            ("SCIENTIST_EXPLORE", "# Explore"),
            ("SCIENTIST_OPTIMIZE", "# Optimize"),
            ("SCIENTIST_ENGINEERING", "# Engineering"),
            ("SCIENTIST_KNOWLEDGE", "# Knowledge"),
            ("SCIENTIST_RESEARCH_INTUITION", "# Intuition"),
            ("SCIENTIST_DO_BETTER", "# Do Better"),
        ):
            self.assertIn(f"<<< RESEARCH_AGENT_INJECTED {label} >>>", prompt)
            self.assertIn(content, prompt)
        self.assertIn(f"Source: {brief_path.resolve()}", prompt)
        self.assertIn("<<< RESEARCH_AGENT_INJECTED SERIAL_COORDINATION_INPUT >>>", prompt)
        self.assertIn(brief_path.read_text(encoding="utf-8").rstrip(), prompt)
        self.assertNotIn("RESEARCH_BRIEF.md content", prompt)
        self.assertIn("launcher-provided Scientist runtime contract", prompt)
        self.assertIn("target files required for Scientist startup", prompt)
        self.assertIn("SYSTEM_CONTRACT.md", prompt)
        self.assertIn("RESEARCH_METHOD.md", prompt)
        self.assertIn("current-brief.json", prompt)
        self.assertIn("do not open their source files merely to retrieve them", prompt)
        self.assertIn("approximately 30-minute research horizon", prompt)
        self.assertIn("genuinely worth implementing", prompt)
        self.assertIn("never as a hard timeout", prompt)
        self.assertIn("finish the current experiment", prompt)
        self.assertGreater(prompt.index("Runtime precedence:"), prompt.index("<<< END RESEARCH_AGENT_INJECTED SERIAL_COORDINATION_INPUT >>>"))

    def test_opencode_meta_points_dir_at_target(self) -> None:
        invocation = self.meta("opencode")
        index = invocation.argv.index("--dir")
        self.assertEqual(invocation.argv[index + 1], str(self.target))
        self.assertIn("--auto", invocation.argv)

    def test_model_is_forwarded_to_meta_and_scientist(self) -> None:
        meta = build_meta_invocation(
            cli="codex",
            target=self.target, cycle_result=Path("/runtime/result.json"),
            start_cycle_id=3, max_cycles=2, allow_edits=True, model="gpt-5.6-luna",
        )
        scientist = build_inner_invocation(
            cli="codex", target=self.target,
            allow_edits=True, prompt=None, model="gpt-5.6-luna",
        )
        for invocation in (meta, scientist):
            index = invocation.argv.index("--model")
            self.assertEqual(invocation.argv[index + 1], "gpt-5.6-luna")

    def test_agy_model_override_includes_default_effort(self) -> None:
        invocation = build_meta_invocation(
            cli="agy",
            target=self.target, cycle_result=Path("/runtime/result.json"),
            start_cycle_id=3, max_cycles=1, allow_edits=True,
            model="gemini-3.7-flash",
        )
        model_index = invocation.argv.index("--model")
        effort_index = invocation.argv.index("--effort")
        self.assertEqual(invocation.argv[model_index + 1], "gemini-3.7-flash")
        self.assertEqual(invocation.argv[effort_index + 1], "medium")

    def test_agy_print_mode_receives_prompt_as_print_argument(self) -> None:
        prompt = "injected runtime context"
        invocation = get_adapter("agy").invoke(
            target=self.target,
            prompt=prompt,
            allow_edits=True,
            model="gemini-3.7-flash-high",
            effort="high",
        )
        self.assertEqual(invocation.argv[-2:], ("--print", prompt))
        self.assertIsNone(invocation.stdin_text)

    def test_codex_explicit_max_effort_uses_reasoning_config(self) -> None:
        invocation = build_inner_invocation(
            cli="codex",
            target=self.target,
            allow_edits=True,
            prompt=None,
            effort="max",
        )
        self.assertIn('model_reasoning_effort="max"', invocation.argv)

    def test_run_invocation_uses_target_uv_cache_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / "runner.log"
            invocation = Invocation(
                (sys.executable, "-c", "import os; print(os.environ['UV_CACHE_DIR'])"),
                directory,
            )
            with patch.dict(
                os.environ,
                {"UV_CACHE_DIR": "", "RESEARCH_UV_CACHE_DIR": ""},
                clear=False,
            ):
                self.assertEqual(
                    run_invocation(invocation, output_path=output, stream_output=False),
                    0,
                )
            self.assertEqual(
                Path(output.read_text(encoding="utf-8").strip()),
                (directory / ".uv-cache").resolve(),
            )

    def test_run_invocation_honors_uv_cache_environment_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / "runner.log"
            configured = directory / "configured-cache"
            invocation = Invocation(
                (sys.executable, "-c", "import os; print(os.environ['UV_CACHE_DIR'])"),
                directory,
            )
            with patch.dict(
                os.environ,
                {"UV_CACHE_DIR": "", "RESEARCH_UV_CACHE_DIR": str(configured)},
                clear=False,
            ):
                self.assertEqual(
                    run_invocation(invocation, output_path=output, stream_output=False),
                    0,
                )
            self.assertEqual(Path(output.read_text(encoding="utf-8").strip()), configured)

    def test_run_invocation_sends_noninteractive_prompt_on_stdin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / "runner.log"
            prompt = "prompt that must not become a process argument"
            invocation = Invocation(
                (sys.executable, "-c", "import sys; print(sys.stdin.read(), end='')"),
                directory,
                stdin_text=prompt,
            )

            self.assertEqual(run_invocation(invocation, output_path=output, stream_output=False), 0)
            self.assertEqual(output.read_text(encoding="utf-8"), prompt)

    def test_run_scratch_lives_under_target_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            run_id, run_dir = create_run_directory(target)
            self.assertEqual(run_dir.parent, target / "research_record" / "runtime" / "tmp")
            self.assertEqual(run_dir.name, run_id)
            self.assertTrue(run_dir.is_dir())

    def test_scientist_uses_current_coordination_brief_without_hard_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            record = target / "research_record"
            record.mkdir()
            (target / "AGENTS.md").write_text("# Project instructions\n", encoding="utf-8")
            (target / "task.md").write_text("# Task\n", encoding="utf-8")
            (target / "PERSONAL.md").write_text("# Personal\n", encoding="utf-8")
            (record / "SKILL.md").write_text("# Scientist\n", encoding="utf-8")
            (record / "SYSTEM_CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
            (record / "RESEARCH_METHOD.md").write_text("# Method\n", encoding="utf-8")
            (record / "VERSION").write_text("research-agent-record-v5\n", encoding="utf-8")
            (record / "RESEARCH_BRIEF.md").write_text("# Brief\n", encoding="utf-8")
            (record / "RESEARCH_RECORD.yaml").write_text("experiments: []\n", encoding="utf-8")
            (record / "EXPLORE.md").write_text("# Explore\n", encoding="utf-8")
            (record / "OPTIMIZE.md").write_text("# Optimize\n", encoding="utf-8")
            (record / "ENGINEERING.md").write_text("# Engineering\n", encoding="utf-8")
            (record / "KNOWLEDGE.md").write_text("# Knowledge\n", encoding="utf-8")
            (record / "RESEARCH_INTUITION.md").write_text("# Intuition\n", encoding="utf-8")
            (record / "DO_BETTER.md").write_text("# Do Better\n", encoding="utf-8")
            (record / "runtime").mkdir()
            brief_path = record / "runtime" / "current-brief.json"
            brief_path.write_text(
                json.dumps({
                    "schema_version": 2,
                    "cycle_id": 1,
                    "concerns": [],
                    "constraints": [],
                    "budget": {"wall_time_minutes": 2},
                }),
                encoding="utf-8",
            )
            git(target, "init", "-q")
            git(target, "config", "user.email", "research-agent@example.invalid")
            git(target, "config", "user.name", "Research Agent Test")
            git(target, "add", ".")
            git(target, "commit", "-qm", "baseline")

            args = argparse.Namespace(
                target=target, cli="codex", model=None,
                allow_edits=True, prompt=None,
            )
            environment = os.environ.copy()
            environment.pop("RESEARCH_AGENT_ROLE", None)
            with (
                patch.dict(os.environ, environment, clear=True),
                patch.dict(os.environ, {"RESEARCH_AGENT_MODEL": "gpt-5.6-luna"}, clear=False),
                patch("research_agent.cli.run_invocation", return_value=0) as runner,
            ):
                self.assertEqual(command_launch_inner(args), 0)

            invocation = runner.call_args.args[0]
            self.assertIn(str(brief_path.resolve()), invocation.stdin_text or "")
            runner_environment = runner.call_args.kwargs["environment"]
            self.assertEqual(
                Path(runner_environment["RESEARCH_AGENT_BRIEF"]).resolve(),
                brief_path.resolve(),
            )
            self.assertNotIn("timeout_seconds", runner.call_args.kwargs)
            self.assertEqual(git(target, "log", "-1", "--format=%s"), "baseline")

    def test_invocation_timeout_is_reported_as_runtime_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            invocation = Invocation((sys.executable, "-c", "import time; time.sleep(1)"), directory)
            with self.assertRaisesRegex(RuntimeError, "wall-time budget"):
                run_invocation(invocation, timeout_seconds=0.01)

    @unittest.skipUnless(os.name == "posix", "signal forwarding is POSIX-specific")
    def test_ctrl_c_forwards_sigint_to_runner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            invocation, ready, marker = interrupt_fixture(directory)
            interrupter = threading.Thread(target=interrupt_when_ready, args=(ready,), daemon=True)
            interrupter.start()
            with self.assertRaises(KeyboardInterrupt):
                run_invocation(invocation)
            interrupter.join(timeout=1)
            self.assertEqual(marker.read_text(encoding="utf-8"), "SIGINT")


if __name__ == "__main__":
    unittest.main()
