from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_agent.cycle import STATUSES, next_cycle_id, read_cycle_result

ROOT = Path(__file__).resolve().parents[1]


class CycleResultTests(unittest.TestCase):
    def test_schema_uses_small_outer_loop_handoff(self) -> None:
        schema = json.loads(
            (
                ROOT
                / "assets"
                / "project-template"
                / "research_record"
                / "schema"
                / "CYCLE_RESULT.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(set(schema["required"]), {"status", "summary", "next_action"})
        self.assertEqual(set(schema["properties"]["status"]["enum"]), set(STATUSES))
        self.assertNotIn("brief_digest", schema["properties"])
        self.assertNotIn("evidence_refs", schema["properties"])

    def test_valid_continue_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            path.write_text(
                json.dumps(
                    {
                        "status": "continue",
                        "summary": "Experiment completed and audited.",
                        "next_action": "Test the registered follow-up.",
                    }
                ),
                encoding="utf-8",
            )
            result = read_cycle_result(path)
            self.assertEqual(result.status, "continue")
            self.assertEqual(result.summary, "Experiment completed and audited.")

    def test_missing_result_returns_control_for_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = read_cycle_result(Path(temporary) / "missing.json")
            self.assertEqual(result.status, "needs_human")

    def test_unknown_status_returns_control_for_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            path.write_text(
                json.dumps(
                    {
                        "status": "keep-going-maybe",
                        "summary": "ambiguous",
                        "next_action": "ambiguous",
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(read_cycle_result(path).status, "needs_human")

    def test_extra_metadata_does_not_become_a_binding_protocol(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            path.write_text(
                json.dumps(
                    {
                        "status": "continue",
                        "summary": "audited",
                        "next_action": "continue",
                        "experiment": "E004",
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(read_cycle_result(path).status, "continue")


class CycleNumberingTests(unittest.TestCase):
    def test_next_cycle_id_starts_at_one_without_brief(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(next_cycle_id(Path(temporary)), 1)

    def test_next_cycle_id_uses_current_brief(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            runtime = target / "research_record" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "current-brief.json").write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "cycle_id": 11,
                        "concerns": [],
                        "constraints": [],
                        "budget": {},
                    }
                ),
                encoding="utf-8",
            )

            self.assertEqual(next_cycle_id(target), 12)

    def test_unrelated_runtime_files_do_not_affect_cycle_numbering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            runtime = target / "research_record" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "some-summary.json").write_text(
                json.dumps({"cycle_id": 99}), encoding="utf-8"
            )

            self.assertEqual(next_cycle_id(target), 1)


if __name__ == "__main__":
    unittest.main()
