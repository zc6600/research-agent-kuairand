from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_agent.ui.parsers.research_record import parse_research_record
from research_agent.ui.status import inspect_snapshot


class ResearchUiParserTests(unittest.TestCase):
    def test_lightweight_ledger_uses_only_official_scores_for_frontier(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "RESEARCH_RECORD.yaml"
            path.write_text(
                """
experiments:
  - id: E1
    record: medium proxy
    primary_metric: {name: primary, value: 0.64}
    official_score: false
    resulting_state: S2
  - id: E2
    record: full validation
    primary_metric: {name: primary, value: 0.61}
    official_score: true
    resulting_state: S3
  - id: E3
    record: later failed proxy
    primary_metric: {name: primary, value: 0.70}
    official_score: false
    resulting_state: null
""",
                encoding="utf-8",
            )
            parsed = parse_research_record(path)
            self.assertEqual(parsed.best_metric, "primary: 0.61")
            self.assertEqual(parsed.best_experiment_id, "E2")
            self.assertEqual(parsed.best_state_id, "S3")
            self.assertEqual(parsed.experiment_id, "E3")
            self.assertEqual(parsed.experiment_metric, "primary: 0.7")


    def test_lightweight_ledger_without_official_score_has_no_frontier(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "RESEARCH_RECORD.yaml"
            path.write_text(
                """
experiments:
  - id: E1
    record: diagnostic
    primary_metric: {name: proxy, value: 0.99}
    official_score: false
""",
                encoding="utf-8",
            )
            parsed = parse_research_record(path)
            self.assertIsNone(parsed.best_metric)
            self.assertIsNone(parsed.best_experiment_id)

    def test_legacy_bottleneck_format_uses_real_yaml_not_indentation_regex(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "RESEARCH_RECORD.yaml"
            path.write_text(
                """
bottlenecks:
- {id: B9, status: active, description: "Tail recall is weak", hypotheses: [
    {id: H9, description: "Exposure is sparse", experiments: [
      {id: E9, evaluation: {status: completed}}
    ]}
  ]}
""",
                encoding="utf-8",
            )
            parsed = parse_research_record(path)
            self.assertEqual(parsed.focus_kind, "bottleneck")
            self.assertEqual(parsed.focus_id, "B9")
            self.assertEqual(parsed.hypothesis_id, "H9")
            self.assertEqual(parsed.experiment_id, "E9")
            self.assertEqual(parsed.experiment_status, "completed")

    def test_thread_like_format_maps_to_same_stable_ui_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "demo"
            record = target / "research_record"
            runtime = record / "runtime"
            runtime.mkdir(parents=True)
            (record / "STATE.yaml").write_text("id: S2\n", encoding="utf-8")
            (record / "RESEARCH_INTUITION.md").write_text("# Research Intuition\n\n## Intuitions\n", encoding="utf-8")
            (record / "RESEARCH_RECORD.yaml").write_text(
                """
research_threads:
  - id: T1
    question: Why does tail recall collapse?
    candidate_explanations:
      - id: H1
        explanation: Sparse exposure limits representation.
        interventions:
          - id: E1
            status: completed
""",
                encoding="utf-8",
            )
            snapshot = inspect_snapshot(target)
            self.assertEqual(snapshot.focus_kind, "research thread")
            self.assertEqual(snapshot.focus_id, "T1")
            self.assertEqual(snapshot.focus, "Why does tail recall collapse?")
            self.assertEqual(snapshot.hypothesis_id, "H1")
            self.assertEqual(snapshot.experiment_id, "E1")
            self.assertIsNone(snapshot.bottleneck_id)

    def test_malformed_yaml_degrades_to_empty_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "RESEARCH_RECORD.yaml"
            path.write_text("bottlenecks: [this is: not valid", encoding="utf-8")
            parsed = parse_research_record(path)
            self.assertIsNone(parsed.focus_id)
            self.assertIsNone(parsed.hypothesis_id)


if __name__ == "__main__":
    unittest.main()
