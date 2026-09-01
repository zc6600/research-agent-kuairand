from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from competitions.kuairand import runner
from competitions.kuairand.runner import latest_project_target, next_project_target


class ProjectNamingTests(unittest.TestCase):
    def test_next_project_number_comes_from_existing_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "projects" / "p001-kuairand-pure").mkdir(parents=True)
            (workspace / "projects" / "_incomplete" / "p003-kuairand-pure-2026-08-26-171509").mkdir(parents=True)
            (workspace / "archive" / "p005-other-task").mkdir(parents=True)

            target = next_project_target(workspace, "kuairand-pure")

            self.assertEqual(target.resolve(), (workspace / "projects" / "p006-kuairand-pure").resolve())

    def test_latest_project_uses_highest_active_matching_trajectory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            projects = workspace / "projects"
            (projects / "p001-kuairand-pure").mkdir(parents=True)
            (projects / "p004-other-task").mkdir()
            (projects / "p006-kuairand-pure").mkdir()
            (projects / "_incomplete" / "p009-kuairand-pure-2026-08-29-010203").mkdir(parents=True)

            target = latest_project_target(workspace, "kuairand-pure")

            assert target is not None
            self.assertEqual(target.resolve(), (projects / "p006-kuairand-pure").resolve())

    def test_setup_creates_next_trajectory_while_step_and_run_continue_latest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            projects = workspace / "projects"
            (projects / "p001-kuairand-pure").mkdir(parents=True)
            (projects / "p003-kuairand-pure").mkdir()
            with (
                patch.object(runner, "WORKSPACE_DIR", workspace),
                patch.dict(os.environ, {"RESEARCH_AGENT_COMPETITION_TARGET": ""}, clear=False),
            ):
                self.assertEqual(
                    runner.competition_target("setup").resolve(),
                    (projects / "p004-kuairand-pure").resolve(),
                )
                self.assertEqual(
                    runner.competition_target("step").resolve(),
                    (projects / "p003-kuairand-pure").resolve(),
                )
                self.assertEqual(
                    runner.competition_target("run").resolve(),
                    (projects / "p003-kuairand-pure").resolve(),
                )

    def test_project_slug_must_be_stable_lowercase_kebab_case(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "lowercase kebab-case"):
                next_project_target(Path(temporary), "KuaiRand_Pure")


if __name__ == "__main__":
    unittest.main()
