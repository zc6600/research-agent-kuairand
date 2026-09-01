from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent.bootstrap import BootstrapError, require_supported_record
from research_agent.cli import reject_nested_meta_cycle
from research_agent.launcher import build_inner_invocation
from research_agent.runners import get_adapter, supported_runners

ROOT = Path(__file__).resolve().parents[1]


class RuntimeBoundaryTests(unittest.TestCase):
    def test_uninitialized_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            with self.assertRaisesRegex(BootstrapError, "not initialized"):
                require_supported_record(target)

    def test_scientist_cannot_launch_another_scientist(self) -> None:
        with patch.dict(os.environ, {"RESEARCH_AGENT_ROLE": "SCIENTIST"}):
            with self.assertRaisesRegex(BootstrapError, "cannot launch another Scientist"):
                build_inner_invocation(
                    cli="codex",
                    target=Path("/tmp/project"),
                    allow_edits=True,
                    prompt=None,
                )

    def test_parallel_reviewer_cannot_launch_another_agent(self) -> None:
        with patch.dict(os.environ, {"RESEARCH_AGENT_ROLE": "PARALLEL_REVIEWER"}):
            with self.assertRaisesRegex(BootstrapError, "Parallel Reviewer cannot launch another agent"):
                build_inner_invocation(
                    cli="codex",
                    target=Path("/tmp/project"),
                    allow_edits=True,
                    prompt=None,
                )

    def test_scientist_cannot_launch_outer_cycle_command(self) -> None:
        with patch.dict(os.environ, {"RESEARCH_AGENT_ROLE": "SCIENTIST"}):
            with self.assertRaisesRegex(BootstrapError, "active SCIENTIST session"):
                reject_nested_meta_cycle("run")

    def test_pyproject_has_no_legacy_workspace(self) -> None:
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertNotIn("[tool.uv.workspace]", text)
        self.assertNotIn("projects/kuairand-pure", text)

    def test_removed_runner_alias_is_not_supported(self) -> None:
        self.assertNotIn("antigravity", supported_runners())
        with self.assertRaisesRegex(ValueError, "unsupported CLI"):
            get_adapter("antigravity")

    def test_checkout_wrapper_keeps_research_agent_on_path(self) -> None:
        script = (ROOT / "scripts" / "research-agent").read_text(encoding="utf-8")
        self.assertIn('export PATH="$SCRIPT_DIR:$PATH"', script)
        self.assertIn('export RESEARCH_AGENT_STATE_TOOL="$SCRIPT_DIR/research-agent"', script)
        self.assertIn('exec uv run --project "$SKILL_ROOT" python -m research_agent "$@"', script)

    def test_checkout_wrapper_exports_its_own_state_tool_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            capture = directory / "environment.txt"
            fake_python = directory / "python3"
            fake_python.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' \"${RESEARCH_AGENT_STATE_TOOL-}\" > \"$CAPTURE\"\n"
                "printf '%s\\n' \"$PATH\" >> \"$CAPTURE\"\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)
            fake_uv = directory / "uv"
            fake_uv.write_text(
                "#!/bin/sh\n"
                "exec \"$FAKE_PYTHON\" \"$@\"\n",
                encoding="utf-8",
            )
            fake_uv.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{directory}{os.pathsep}{environment['PATH']}"
            environment["CAPTURE"] = str(capture)
            environment["FAKE_PYTHON"] = str(fake_python)
            environment.pop("RESEARCH_AGENT_STATE_TOOL", None)

            subprocess.run(
                [str(ROOT / "scripts" / "research-agent"), "--help"],
                check=True,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            lines = capture.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], str(ROOT / "scripts" / "research-agent"))
            self.assertEqual(lines[1].split(os.pathsep)[0], str(ROOT / "scripts"))


if __name__ == "__main__":
    unittest.main()
