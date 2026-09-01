from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "competitions" / "kuairand" / "task.md"
OPTIMIZE = ROOT / "competitions" / "kuairand" / "OPTIMIZE.md"
METHOD = ROOT / "assets" / "project-template" / "research_record" / "RESEARCH_METHOD.md"
RUNNER = ROOT / "competitions" / "kuairand" / "runner.py"


class KuaiRandTaskContractTests(unittest.TestCase):
    def test_task_keeps_objective_and_official_accounting(self) -> None:
        task = TASK.read_text(encoding="utf-8")

        self.assertIn("## Optimization objective", task)
        self.assertIn("maximize the valid public-validation `primary` score", task)
        self.assertIn("ε = 0.002, N = 3 consecutive Full evaluations", task)
        self.assertIn("Smoke and Medium evaluations", task)
        self.assertIn("std 0.0008", task)

    def test_task_specific_strategy_lives_in_optimize(self) -> None:
        task = TASK.read_text(encoding="utf-8")
        optimize = OPTIMIZE.read_text(encoding="utf-8")

        for phrase in (
            "addressable impact on `primary`",
            "intervention path",
            "validation-best valid checkpoint",
            "treat Full evaluations as scarce decision points",
            "not a statistical-significance threshold",
            "**Objective impact**",
            "**Information value**",
        ):
            self.assertIn(phrase, optimize)

        self.assertNotIn("addressable impact on `primary`", task)
        self.assertNotIn("intervention path", task)
        self.assertNotIn("**Objective impact**", task)
        self.assertNotIn("Do not turn these priorities into fabricated numeric utilities", task)

    def test_full_gate_is_task_strategy_not_universal_method(self) -> None:
        optimize = OPTIMIZE.read_text(encoding="utf-8")
        method = METHOD.read_text(encoding="utf-8")

        self.assertIn("Smoke and Medium evaluations are neutral", optimize)
        self.assertIn("This is a task-specific resource strategy", optimize)
        self.assertIn("tools rather than universally required gates", method)
        self.assertIn("preserve the grouping unit relevant to the evaluator", method)
        self.assertNotIn("must have a gate", method)

    def test_competition_setup_seeds_optimize_without_owning_future_updates(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("def seed_competition_optimize", runner)
        self.assertIn("RESEARCH_AGENT_COMPETITION_OPTIMIZE", runner)
        self.assertIn('"competitions" / "kuairand" / "OPTIMIZE.md"', runner)
        self.assertIn("if current.strip() and current != generic", runner)
        self.assertIn("seed_competition_optimize(target, optimize_source)", runner)

    def test_competition_wrapper_preserves_role_specific_runner_configuration(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")

        for flag in (
            "--meta-cli",
            "--scientist-cli",
            "--meta-model",
            "--scientist-model",
            "--meta-effort",
            "--scientist-effort",
        ):
            self.assertIn(flag, runner)

        for name in (
            "RESEARCH_AGENT_COMPETITION_META_CLI",
            "RESEARCH_AGENT_COMPETITION_SCIENTIST_CLI",
            "RESEARCH_AGENT_COMPETITION_META_MODEL",
            "RESEARCH_AGENT_COMPETITION_SCIENTIST_MODEL",
            "RESEARCH_AGENT_COMPETITION_META_EFFORT",
            "RESEARCH_AGENT_COMPETITION_SCIENTIST_EFFORT",
        ):
            self.assertIn(name, runner)

        self.assertIn('step.add_argument("-e", "--effort", choices=EFFORT_LEVELS)', runner)
        self.assertIn('run.add_argument("-e", "--effort", choices=EFFORT_LEVELS)', runner)
        self.assertIn('runner_args.extend(["--meta-cli", meta_cli, "--scientist-cli", scientist_cli])', runner)
        self.assertIn('runner_args.extend(["--meta-model", meta_model])', runner)
        self.assertIn('runner_args.extend(["--scientist-model", scientist_model])', runner)
        self.assertIn('runner_args.extend(["--meta-effort", meta_effort])', runner)
        self.assertIn('runner_args.extend(["--scientist-effort", scientist_effort])', runner)


if __name__ == "__main__":
    unittest.main()
