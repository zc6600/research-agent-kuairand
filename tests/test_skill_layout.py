from __future__ import annotations

import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillLayoutTests(unittest.TestCase):
    def test_distribution_entrypoints_exist(self) -> None:
        expected = (
            ROOT / "SKILL.md",
            ROOT / "PERSONAL.md",
            ROOT / "scripts" / "research-agent",
            ROOT / "scripts" / "competition.sh",
            ROOT / "vendor" / "kuairand-starter-kit.zip",
            ROOT / "assets" / "project-template" / ".gitignore",
            ROOT / "assets" / "project-template" / "research_record" / "SKILL.md",
            ROOT / "assets" / "project-template" / "research_record" / "SYSTEM_CONTRACT.md",
            ROOT / "assets" / "project-template" / "research_record" / "RESEARCH_METHOD.md",
            ROOT / "assets" / "project-template" / "research_record" / "EXPLORE.md",
            ROOT / "assets" / "project-template" / "research_record" / "schema" / "CYCLE_BRIEF.schema.json",
            ROOT / "assets" / "project-template" / "research_record" / "schema" / "CYCLE_RESULT.schema.json",
        )
        for path in expected:
            with self.subTest(path=path):
                self.assertTrue(path.is_file())

    def test_canonical_shell_entrypoints_are_executable(self) -> None:
        for name in ("research-agent", "competition.sh"):
            path = ROOT / "scripts" / name
            with self.subTest(path=path):
                self.assertTrue(os.access(path, os.X_OK))

    def test_legacy_shell_aliases_are_absent(self) -> None:
        for name in (
            "step.sh",
            "run_agent.sh",
            "init_project.sh",
            "launch_inner.sh",
            "collect_usage.sh",
            "doctor.sh",
            "start_competition.sh",
        ):
            with self.subTest(name=name):
                self.assertFalse((ROOT / "scripts" / name).exists())

    def test_project_template_is_the_canonical_contract_source(self) -> None:
        record = ROOT / "assets" / "project-template" / "research_record"
        self.assertTrue((record / "SYSTEM_CONTRACT.md").is_file())
        self.assertTrue((record / "RESEARCH_METHOD.md").is_file())
        self.assertFalse((record / "META_POLICY.md").exists())
        self.assertFalse((record / "PROTOCOL.md").exists())


if __name__ == "__main__":
    unittest.main()
