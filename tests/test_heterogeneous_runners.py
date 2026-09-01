from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from research_agent.bootstrap import BootstrapError
from research_agent.cli import build_parser, resolved_role_config
from research_agent.launcher import build_inner_invocation, build_meta_invocation
from research_agent.runners import get_adapter, supported_runners


class HeterogeneousRunnerTests(unittest.TestCase):
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
        (record / "SKILL.md").write_text("# Injected Scientist Skill\n", encoding="utf-8")
        for name in (
            "SYSTEM_CONTRACT.md",
            "RESEARCH_METHOD.md",
            "RESEARCH_BRIEF.md",
            "EXPLORE.md",
            "OPTIMIZE.md",
            "ENGINEERING.md",
            "KNOWLEDGE.md",
            "RESEARCH_INTUITION.md",
            "DO_BETTER.md",
        ):
            (record / name).write_text(f"# {name}\n", encoding="utf-8")
        (record / "RESEARCH_RECORD.yaml").write_text("experiments: []\n", encoding="utf-8")
        (record / "runtime" / "current-brief.json").write_text(
            '{"schema_version": 2, "cycle_id": 3, "concerns": [], "constraints": [], "budget": {}}\n',
            encoding="utf-8",
        )

    def test_gemini_is_a_supported_runner(self) -> None:
        self.assertIn("gemini", supported_runners())

    def test_gemini_editable_invocation_is_headless_and_noninteractive(self) -> None:
        invocation = get_adapter("gemini").invoke(
            target=self.target,
            prompt="Run one Scientist iteration.",
            allow_edits=True,
            model="flash",
        )
        self.assertEqual(invocation.cwd, self.target)
        self.assertEqual(invocation.argv[0], "gemini")
        self.assertIn("--skip-trust", invocation.argv)
        self.assertIn("--approval-mode=yolo", invocation.argv)
        self.assertNotIn("--prompt", invocation.argv)
        self.assertEqual(invocation.stdin_text, "Run one Scientist iteration.")
        model_index = invocation.argv.index("--model")
        self.assertEqual(invocation.argv[model_index + 1], "flash")

    def test_gemini_read_only_invocation_uses_plan_mode(self) -> None:
        invocation = get_adapter("gemini").invoke(
            target=self.target,
            prompt="Inspect only.",
            allow_edits=False,
            model=None,
        )
        self.assertIn("--approval-mode=plan", invocation.argv)
        self.assertNotIn("--model", invocation.argv)

    def test_noninteractive_runners_receive_prompt_through_their_supported_channel(self) -> None:
        prompt = "unique injected prompt marker"
        for cli in supported_runners():
            with self.subTest(cli=cli):
                invocation = get_adapter(cli).invoke(
                    target=self.target,
                    prompt=prompt,
                    allow_edits=True,
                    model=None,
                )
                if cli == "agy":
                    self.assertEqual(invocation.argv[-2:], ("--print", prompt))
                    self.assertIsNone(invocation.stdin_text)
                else:
                    self.assertEqual(invocation.stdin_text, prompt)
                    self.assertNotIn(prompt, invocation.argv)

    def test_shared_cli_remains_backward_compatible(self) -> None:
        args = argparse.Namespace(
            cli="codex",
            meta_cli=None,
            scientist_cli=None,
            model="gpt-shared",
            meta_model=None,
            scientist_model=None,
        )
        self.assertEqual(
            resolved_role_config(args),
            ("codex", "codex", "gpt-shared", "gpt-shared", None, None),
        )

    def test_role_specific_configuration_can_mix_codex_and_gemini(self) -> None:
        args = argparse.Namespace(
            cli=None,
            meta_cli="codex",
            scientist_cli="gemini",
            model=None,
            meta_model="gpt-meta",
            scientist_model="flash",
        )
        self.assertEqual(
            resolved_role_config(args),
            ("codex", "gemini", "gpt-meta", "flash", None, None),
        )

    def test_shared_cli_can_be_overridden_for_scientist_only(self) -> None:
        args = argparse.Namespace(
            cli="codex",
            meta_cli=None,
            scientist_cli="gemini",
            model=None,
            meta_model=None,
            scientist_model="pro",
        )
        self.assertEqual(
            resolved_role_config(args),
            ("codex", "gemini", None, "pro", None, None),
        )

    def test_role_specific_effort_overrides_shared_effort(self) -> None:
        args = argparse.Namespace(
            cli="codex",
            meta_cli=None,
            scientist_cli=None,
            model=None,
            meta_model=None,
            scientist_model=None,
            effort="high",
            meta_effort="low",
            scientist_effort=None,
        )
        self.assertEqual(
            resolved_role_config(args),
            ("codex", "codex", None, None, "low", "high"),
        )

    def test_missing_role_runner_is_rejected(self) -> None:
        args = argparse.Namespace(
            cli=None,
            meta_cli="codex",
            scientist_cli=None,
            model=None,
            meta_model=None,
            scientist_model=None,
        )
        with self.assertRaisesRegex(BootstrapError, "both --meta-cli and --scientist-cli"):
            resolved_role_config(args)

    def test_meta_prompt_launches_exact_delegated_scientist_runner(self) -> None:
        invocation = build_meta_invocation(
            cli="codex",
            target=self.target,
            cycle_result=Path("/runtime/result.json"),
            start_cycle_id=3,
            max_cycles=2,
            allow_edits=True,
            model="gpt-meta",
            scientist_cli="gemini",
            scientist_model="flash",
        )
        prompt = invocation.stdin_text or ""
        self.assertIn("Delegated Scientist runner: gemini / flash", prompt)
        self.assertIn("research-agent launch-inner", prompt)
        self.assertIn("--cli gemini", prompt)
        self.assertIn("--model flash", prompt)

    def test_codex_max_effort_is_forwarded_to_both_roles(self) -> None:
        meta = build_meta_invocation(
            cli="codex",
            target=self.target,
            cycle_result=Path("/runtime/result.json"),
            start_cycle_id=3,
            max_cycles=1,
            allow_edits=True,
            effort="max",
            scientist_effort="max",
        )
        inner = build_inner_invocation(
            cli="codex",
            target=self.target,
            allow_edits=True,
            prompt=None,
            effort="max",
        )
        self.assertIn('model_reasoning_effort="max"', meta.argv)
        self.assertIn('model_reasoning_effort="max"', inner.argv)
        for invocation in (meta, inner):
            self.assertIn('model_reasoning_effort="max"', invocation.argv)
        self.assertIn("--effort max", meta.stdin_text or "")

    def test_parser_accepts_explicit_role_runners_without_shared_cli(self) -> None:
        args = build_parser().parse_args([
            "run",
            "--target",
            "/work/project",
            "--meta-cli",
            "codex",
            "--scientist-cli",
            "gemini",
            "--scientist-model",
            "flash",
            "--allow-edits",
            "--max-cycles",
            "3",
            "--effort",
            "max",
        ])
        self.assertEqual(args.meta_cli, "codex")
        self.assertEqual(args.scientist_cli, "gemini")
        self.assertEqual(args.scientist_model, "flash")
        self.assertEqual(args.effort, "max")


if __name__ == "__main__":
    unittest.main()
