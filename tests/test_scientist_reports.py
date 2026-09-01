from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_agent.parallel_support import adopt_memory, snapshot_memory

ROOT = Path(__file__).resolve().parents[1]


class ScientistReportTests(unittest.TestCase):
    def test_template_ignores_reports_outside_state_history(self) -> None:
        ignore = (
            ROOT / "assets" / "project-template" / ".gitignore"
        ).read_text(encoding="utf-8")
        self.assertIn("research_record/reports/", ignore)

    def test_parallel_snapshot_and_adoption_preserve_reports_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            snapshot = root / "snapshot"
            target = root / "target"
            report = source / "research_record" / "reports" / "branch-r1b1.md"
            report.parent.mkdir(parents=True)
            report.write_text(
                "I think the evaluator may be rewarding a different mechanism.\n"
                "Not sure yet; the failed run is still interesting.\n",
                encoding="utf-8",
            )

            snapshot_memory(source, snapshot)
            copied = snapshot / "research_record" / "reports" / "branch-r1b1.md"
            self.assertEqual(copied.read_bytes(), report.read_bytes())

            adopt_memory(snapshot, target)
            adopted = target / "research_record" / "reports" / "branch-r1b1.md"
            self.assertEqual(adopted.read_bytes(), report.read_bytes())

    def test_production_parallel_handoff_has_no_reflection_field(self) -> None:
        source = (
            ROOT / "src" / "research_agent" / "parallel_support.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn('"reflection":', source)


if __name__ == "__main__":
    unittest.main()
