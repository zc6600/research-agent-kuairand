from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_agent.brief import read_cycle_brief

ROOT = Path(__file__).resolve().parents[1]


class CycleBriefTests(unittest.TestCase):
    def test_valid_brief_is_typed_supervision_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "current-brief.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "cycle_id": 7,
                        "concerns": ["Recent iterations may be repeating low-value tuning."],
                        "constraints": ["Preserve the remaining research budget."],
                        "budget": {"llm_tokens": 30000},
                    }
                ),
                encoding="utf-8",
            )

            brief = read_cycle_brief(path)

            self.assertEqual(brief.schema_version, 2)
            self.assertEqual(brief.cycle_id, 7)
            self.assertEqual(
                brief.concerns,
                ("Recent iterations may be repeating low-value tuning.",),
            )
            self.assertEqual(brief.budget["llm_tokens"], 30000)
            self.assertFalse(hasattr(brief, "objective"))
            self.assertFalse(hasattr(brief, "digest"))
            self.assertFalse(hasattr(brief, "evidence_refs"))

    def test_minimal_brief_defaults_optional_coordination_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "current-brief.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "cycle_id": 3,
                        "meta_note": "Optional extension metadata.",
                    }
                ),
                encoding="utf-8",
            )

            brief = read_cycle_brief(path)

            self.assertEqual(brief.cycle_id, 3)
            self.assertEqual(brief.concerns, ())
            self.assertEqual(brief.constraints, ())
            self.assertEqual(brief.budget, {})

    def test_brief_ignores_unknown_budget_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "current-brief.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "cycle_id": 4,
                        "budget": {
                            "wall_time_minutes": 10,
                            "estimated_cost_usd": 2.5,
                        },
                    }
                ),
                encoding="utf-8",
            )

            brief = read_cycle_brief(path)

            self.assertEqual(brief.budget, {})

    def test_brief_lists_have_no_arbitrary_count_or_length_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "current-brief.json"
            long_text = "x" * 2000
            concerns = [f"concern-{index}" for index in range(32)] + [long_text]
            constraints = [f"constraint-{index}" for index in range(32)] + [long_text]
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "cycle_id": 8,
                        "concerns": concerns,
                        "constraints": constraints,
                    }
                ),
                encoding="utf-8",
            )

            brief = read_cycle_brief(path)

            self.assertEqual(len(brief.concerns), 33)
            self.assertEqual(len(brief.constraints), 33)
            self.assertEqual(brief.concerns[-1], long_text)
            self.assertEqual(brief.constraints[-1], long_text)

    def test_schema_v1_brief_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "current-brief.json"
            path.write_text(
                json.dumps({"schema_version": 1, "cycle_id": 3}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "unsupported schema_version"):
                read_cycle_brief(path)

    def test_missing_cycle_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "current-brief.json"
            path.write_text(json.dumps({"schema_version": 2}), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing fields: cycle_id"):
                read_cycle_brief(path)

    def test_known_budget_fields_still_require_valid_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "current-brief.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "cycle_id": 5,
                        "budget": {"llm_tokens": 0},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "budget.llm_tokens"):
                read_cycle_brief(path)

    def test_schema_matches_runtime_tolerance(self) -> None:
        schema = json.loads(
            (
                ROOT
                / "assets"
                / "project-template"
                / "research_record"
                / "schema"
                / "CYCLE_BRIEF.schema.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(schema["required"], ["schema_version", "cycle_id"])
        self.assertTrue(schema["additionalProperties"])
        self.assertTrue(schema["properties"]["budget"]["additionalProperties"])
        self.assertEqual(schema["properties"]["concerns"]["default"], [])
        self.assertEqual(schema["properties"]["constraints"]["default"], [])
        self.assertEqual(schema["properties"]["budget"]["default"], {})


if __name__ == "__main__":
    unittest.main()
