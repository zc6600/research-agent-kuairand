from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent.baseline import BASELINE_PROMPT, baseline_main
from research_agent.baseline import build_parser as build_baseline_parser
from research_agent.runners import get_adapter
from research_agent.runners.agy import AgyAdapter
from research_agent.runners.claude import ClaudeAdapter
from research_agent.runners.codex import CodexAdapter
from research_agent.usage_capture import (
    _agy_entries,
    _delta,
    _gemini_entries,
    _subtract_scientists,
    model_usage_report,
)


class ModelUsageTests(unittest.TestCase):
    def test_gemini_json_is_split_by_actual_model(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "gemini.json"
            path.write_text(
                json.dumps(
                    {
                        "response": "done",
                        "stats": {
                            "models": {
                                "gemini-pro": {
                                    "tokens": {
                                        "prompt": 100,
                                        "candidates": 50,
                                        "thoughts": 25,
                                        "cached": 10,
                                        "total": 175,
                                    }
                                },
                                "gemini-flash": {"tokens": {"total": 40}},
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            entries = _gemini_entries(path, role="scientist", configured_model="auto")
            report = model_usage_report(entries)

        self.assertEqual(report["accounting_status"], "measured")
        self.assertEqual(report["total"], 215)
        self.assertEqual([item["model"] for item in report["models"]], ["gemini-flash", "gemini-pro"])

    def test_agy_json_uses_official_session_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "agy.json"
            path.write_text(
                json.dumps(
                    {
                        "conversation_id": "example",
                        "status": "SUCCESS",
                        "response": "done",
                        "usage": {
                            "input_tokens": 10415,
                            "output_tokens": 657,
                            "thinking_tokens": 616,
                            "cache_read_tokens": 8113,
                            "total_tokens": 11072,
                        },
                    }
                ),
                encoding="utf-8",
            )
            entries = _agy_entries(path, role="scientist", configured_model="gemini-3.7-flash")
            report = model_usage_report(entries)

        self.assertEqual(report["accounting_status"], "measured")
        self.assertEqual(report["total"], 11072)
        model = report["models"][0]
        self.assertEqual(model["runner"], "agy")
        self.assertEqual(model["model"], "gemini-3.7-flash")
        self.assertEqual(model["input"], 10415)
        self.assertEqual(model["output"], 657)
        self.assertEqual(model["reasoning"], 616)
        self.assertEqual(model["cache_read"], 8113)

    def test_empty_before_snapshot_is_a_valid_zero_baseline(self) -> None:
        before = {
            "runner": "codex",
            "accounting_status": "unavailable",
            "reason": "No matching Codex sessions were found",
        }
        after = {
            "runner": "codex",
            "accounting_status": "measured",
            "total": 500,
            "input": 300,
            "output": 200,
        }
        delta = _delta(after, before)
        self.assertEqual(delta["accounting_status"], "measured")
        self.assertEqual(delta["total"], 500)
        self.assertEqual(delta["baseline_status"], "empty")

    def test_same_runner_scientist_usage_is_removed_from_meta_total(self) -> None:
        total = {
            "role": "meta",
            "runner": "codex",
            "model": "meta-model",
            "accounting_status": "measured",
            "input": 700,
            "output": 300,
            "total": 1000,
        }
        scientist = [
            {
                "role": "scientist",
                "runner": "codex",
                "model": "scientist-model",
                "accounting_status": "measured",
                "input": 400,
                "output": 200,
                "total": 600,
            }
        ]
        meta = _subtract_scientists(total, scientist)
        self.assertEqual(meta["input"], 300)
        self.assertEqual(meta["output"], 100)
        self.assertEqual(meta["total"], 400)

    def test_gemini_adapter_requests_json_metrics(self) -> None:
        invocation = get_adapter("gemini").invoke(
            target=Path("/tmp/project"),
            prompt="improve",
            allow_edits=True,
            model="flash",
        )
        index = invocation.argv.index("--output-format")
        self.assertEqual(invocation.argv[index + 1], "json")

    def test_agy_adapter_requests_json_metrics(self) -> None:
        invocation = get_adapter("agy").invoke(
            target=Path("/tmp/project"),
            prompt="improve",
            allow_edits=True,
            model="gemini-3.7-flash",
        )
        index = invocation.argv.index("--output-format")
        self.assertEqual(invocation.argv[index + 1], "json")


class BlankControlTests(unittest.TestCase):
    def test_baseline_prompt_excludes_research_agent_method(self) -> None:
        self.assertIn("Do not use research_record/** as guidance", BASELINE_PROMPT)
        self.assertIn("do not adopt META or Scientist roles", BASELINE_PROMPT)
        self.assertIn("do not invoke research-agent", BASELINE_PROMPT)
        self.assertIn("Improve this task's measured performance directly", BASELINE_PROMPT)

    def test_baseline_cli_requires_explicit_runner_and_target(self) -> None:
        args = build_baseline_parser().parse_args(
            [
                "--target",
                "/tmp/project",
                "--cli",
                "codex",
                "--model",
                "gpt-control",
                "--effort",
                "max",
                "--allow-edits",
            ]
        )
        self.assertEqual(args.cli, "codex")
        self.assertEqual(args.model, "gpt-control")
        self.assertEqual(args.effort, "max")
        self.assertTrue(args.allow_edits)

    def test_codex_baseline_builds_a_goal_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            (target / ".git").mkdir(parents=True)
            with (
                patch("research_agent.baseline._prepare_target", return_value=target),
                patch("research_agent.baseline.get_adapter", return_value=CodexAdapter()),
                patch("research_agent.baseline.run_invocation", return_value=0) as run,
            ):
                self.assertEqual(
                    baseline_main(
                        [
                            "--target",
                            str(target),
                            "--cli",
                            "codex",
                            "--allow-edits",
                            "--quiet",
                        ]
                    ),
                    0,
                )

            invocation = run.call_args.args[0]
            self.assertTrue(invocation.interactive)
            self.assertTrue(invocation.input_text.startswith("/goal "))
            metadata = json.loads(
                next((target / ".git" / "research-agent-baseline").glob("*/run.json")).read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(metadata["mode"], "goal")

    def test_agy_baseline_builds_a_goal_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            (target / ".git").mkdir(parents=True)
            with (
                patch("research_agent.baseline._prepare_target", return_value=target),
                patch("research_agent.baseline.get_adapter", return_value=AgyAdapter()),
                patch("research_agent.baseline.run_invocation", return_value=0) as run,
            ):
                self.assertEqual(
                    baseline_main(
                        [
                            "--target",
                            str(target),
                            "--cli",
                            "agy",
                            "--allow-edits",
                            "--quiet",
                        ]
                    ),
                    0,
                )

            invocation = run.call_args.args[0]
            self.assertEqual(invocation.argv[-2], "--print")
            self.assertIn("/goal ", invocation.argv[-1])
            self.assertIsNone(invocation.stdin_text)
            metadata = json.loads(
                next((target / ".git" / "research-agent-baseline").glob("*/run.json")).read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(metadata["mode"], "goal")

    def test_claude_baseline_builds_a_goal_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target"
            (target / ".git").mkdir(parents=True)
            with (
                patch("research_agent.baseline._prepare_target", return_value=target),
                patch("research_agent.baseline.get_adapter", return_value=ClaudeAdapter()),
                patch("research_agent.baseline.run_invocation", return_value=0) as run,
            ):
                self.assertEqual(
                    baseline_main(
                        [
                            "--target",
                            str(target),
                            "--cli",
                            "claude",
                            "--model",
                            "glm-4-flash",
                            "--allow-edits",
                            "--quiet",
                        ]
                    ),
                    0,
                )

            invocation = run.call_args.args[0]
            self.assertIn("/goal ", invocation.stdin_text or "")
            self.assertIn("--model", invocation.argv)
            model_index = invocation.argv.index("--model")
            self.assertEqual(invocation.argv[model_index + 1], "glm-4-flash")
            metadata = json.loads(
                next((target / ".git" / "research-agent-baseline").glob("*/run.json")).read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(metadata["mode"], "goal")
            self.assertEqual(metadata["model"], "glm-4-flash")


if __name__ == "__main__":
    unittest.main()
