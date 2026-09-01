from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_agent.ui.lifecycle import latest_run, read_run
from research_agent.ui.progress import diff_status
from research_agent.ui.render import render_status
from research_agent.ui.status import ResearchStatus, inspect_status
from research_agent.ui.web import RAW_FILES, DashboardState


class ResearchUiTests(unittest.TestCase):
    def test_status_projects_existing_research_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "demo-project"
            runtime = target / "research_record" / "runtime"
            runtime.mkdir(parents=True)
            record = target / "research_record"
            run = runtime / "tmp" / "run-1"
            meta = run / "meta"
            meta.mkdir(parents=True)

            (runtime / "current-brief.json").write_text(
                json.dumps({"cycle_id": 8, "concerns": ["Avoid repeating low-information interventions."]}),
                encoding="utf-8",
            )
            (record / "VERSION").write_text("research-agent-record-v5\n", encoding="utf-8")
            (run / "run.json").write_text(
                json.dumps({
                    "run_id": "run-1",
                    "kind": "run",
                    "started_at": "2026-08-29T01:00:00+00:00",
                    "ended_at": "2026-08-29T01:10:00+00:00",
                    "status": "closed",
                    "terminal_status": "continue",
                }),
                encoding="utf-8",
            )
            (meta / "result.json").write_text(
                json.dumps({"status": "continue", "summary": "Useful diagnostic.", "next_action": "Continue."}),
                encoding="utf-8",
            )
            (meta / "usage.json").write_text(
                json.dumps({"accounting_status": "measured", "scope": "run_delta", "total": 482000}),
                encoding="utf-8",
            )
            (record / "STATE.yaml").write_text(
                "id: S014\n"
                "git_tag: state/S014\n"
                "derived_from: S013\n"
                "scientist_report: research_record/reports/cycle-8.md\n"
                "summary: >\n"
                "  Current retained implementation.\n"
                "performance:\n"
                "  validation:\n"
                "    GAUC: 0.701\n"
                "    nDCG@5: 0.512\n"
                "    primary: 0.6065\n"
                "  baseline_delta:\n"
                "    primary: 0.0045\n"
                "  evidence_ref: system/evidence/final.json\n",
                encoding="utf-8",
            )
            (record / "RESEARCH_INTUITION.md").write_text(
                "# Research Intuition\n\n## Intuitions\n\nThe system appears coverage-limited rather than capacity-limited.\n",
                encoding="utf-8",
            )
            (record / "RESEARCH_RECORD.yaml").write_text(
                "bottlenecks:\n"
                "  - id: B003\n"
                "    description: >\n"
                "      Tail-item candidate recall is weak.\n"
                "    status: active\n"
                "    hypotheses:\n"
                "      - id: H007\n"
                "        description: >\n"
                "          Sparse exposure limits tail representation.\n"
                "        experiments:\n"
                "          - id: E023\n"
                "            actual_result: >\n"
                "              Tail recall improved on the fixed holdout.\n"
                "            evaluation:\n"
                "              status: completed\n"
                "              primary_metric:\n"
                "                name: recall_at_10\n"
                "                value: 0.731\n"
                "              compared_with_state: S013\n"
                "              improvement_over_comparator: 0.021\n"
                "            fidelity: full\n"
                "            official_score: true\n"
                "            resulting_state: S014\n"
                "            evidence:\n"
                "              - research_record/evidence/E023.json\n"
                "            conclusion: >\n"
                "              The result supports the coverage hypothesis.\n",
                encoding="utf-8",
            )

            status = inspect_status(target)
            self.assertEqual(status.cycle_id, 8)
            self.assertEqual(status.state_id, "S014")
            self.assertEqual(status.focus_kind, "bottleneck")
            self.assertEqual(status.focus_id, "B003")
            self.assertEqual(status.bottleneck_id, "B003")
            self.assertEqual(status.hypothesis_id, "H007")
            self.assertEqual(status.experiment_id, "E023")
            self.assertEqual(status.experiment_status, "completed")
            self.assertEqual(status.experiment_result, "Tail recall improved on the fixed holdout.")
            self.assertEqual(status.experiment_metric, "recall_at_10: 0.731 · Δ 0.021 vs S013")
            self.assertEqual(status.experiment_conclusion, "The result supports the coverage hypothesis.")
            self.assertEqual(status.experiment_fidelity, "full")
            self.assertTrue(status.experiment_official_score)
            self.assertEqual(status.experiment_resulting_state, "S014")
            self.assertEqual(status.experiment_evidence_count, 1)
            self.assertEqual(status.record_version, "research-agent-record-v5")
            self.assertEqual(status.state_summary, "Current retained implementation.")
            self.assertEqual(status.state_scientist_report, "research_record/reports/cycle-8.md")
            self.assertEqual(status.research_cycle_id, 8)
            self.assertEqual(
                status.state_validation_metrics,
                (
                    {"name": "GAUC", "value": 0.701},
                    {"name": "nDCG@5", "value": 0.512},
                    {"name": "primary", "value": 0.6065},
                ),
            )
            self.assertEqual(status.state_baseline_deltas, ({"name": "primary", "value": 0.0045},))
            self.assertEqual(status.state_evidence_ref, "system/evidence/final.json")
            self.assertEqual(status.last_status, "continue")
            self.assertEqual(status.last_summary, "Useful diagnostic.")
            self.assertEqual(status.usage_total, 482000)
            self.assertIn("coverage-limited", status.intuition or "")

            rendered = render_status(status)
            self.assertIn("Research focus · Bottleneck", rendered)
            self.assertIn("Latest recorded hypothesis", rendered)
            self.assertNotIn("Current hypothesis", rendered)
            self.assertIn("Latest recorded experiment", rendered)
            self.assertIn("Experiment result", rendered)
            self.assertIn("recall_at_10: 0.731", rendered)
            self.assertIn("Experiment conclusion", rendered)
            self.assertIn("✦ Research intuition", rendered)
            self.assertIn("482,000 tokens", rendered)

    def test_best_score_uses_completed_full_public_validation_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "demo-project"
            record = target / "research_record"
            record.mkdir(parents=True)
            (record / "RESEARCH_RECORD.yaml").write_text(
                "bottlenecks:\n"
                "  - id: B001\n"
                "    status: active\n"
                "    hypotheses:\n"
                "      - id: H001\n"
                "        experiments:\n"
                "          - id: E001\n"
                "            starting_state: S001\n"
                "            resulting_state: S002\n"
                "            evaluation:\n"
                "              status: completed\n"
                "              fidelity: full\n"
                "              split: public_validation\n"
                "              primary_metric:\n"
                "                name: primary\n"
                "                value: 0.612\n"
                "          - id: E002\n"
                "            starting_state: S002\n"
                "            resulting_state: S003\n"
                "            evaluation:\n"
                "              status: completed\n"
                "              fidelity: medium\n"
                "              split: public_validation\n"
                "              primary_metric:\n"
                "                name: primary\n"
                "                value: 0.99\n"
                "          - id: E003\n"
                "            starting_state: S003\n"
                "            resulting_state: S004\n"
                "            evaluation:\n"
                "              status: completed\n"
                "              fidelity: full\n"
                "              split: public_validation\n"
                "              primary_metric:\n"
                "                name: primary\n"
                "                value: 0.625\n"
                "          - id: E004\n"
                "            starting_state: S004\n"
                "            evaluation:\n"
                "              status: failed\n"
                "              fidelity: full\n"
                "              split: public_validation\n"
                "              primary_metric:\n"
                "                name: primary\n"
                "                value: 0.999\n"
                "          - id: E005\n"
                "            starting_state: S004\n"
                "            evaluation:\n"
                "              status: completed\n"
                "              fidelity: full\n"
                "              split: train_holdout\n"
                "              primary_metric:\n"
                "                name: primary\n"
                "                value: 0.998\n",
                encoding="utf-8",
            )

            status = inspect_status(target)
            self.assertEqual(status.best_metric, "primary: 0.625")
            self.assertEqual(status.best_experiment_id, "E003")
            self.assertEqual(status.best_state_id, "S004")

    def test_running_latest_run_does_not_reuse_stale_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "demo-project"
            runtime = target / "research_record" / "runtime"
            old_meta = runtime / "tmp" / "old" / "meta"
            new_run = runtime / "tmp" / "new"
            old_meta.mkdir(parents=True)
            new_run.mkdir(parents=True)
            (runtime / "current-brief.json").write_text(json.dumps({"cycle_id": 2, "concerns": []}))
            (old_meta.parent / "run.json").write_text(json.dumps({
                "run_id": "old", "kind": "run", "started_at": "2026-08-29T00:00:00+00:00",
                "status": "closed", "terminal_status": "converged",
            }))
            (old_meta / "usage.json").write_text(json.dumps({"accounting_status": "measured", "total": 999}))
            (new_run / "run.json").write_text(json.dumps({
                "run_id": "new", "kind": "run", "started_at": "2026-08-29T01:00:00+00:00",
                "status": "running",
            }))

            status = inspect_status(target)
            self.assertIsNone(status.usage_total)
            self.assertIsNone(status.usage_status)

    def test_progress_reports_semantic_changes_only(self) -> None:
        previous = ResearchStatus(project="demo", cycle_id=3, state_id="S004")
        current = ResearchStatus(
            project="demo",
            cycle_id=4,
            state_id="S005",
            hypothesis_id="H009",
            hypothesis="Coverage is limiting recall.",
            intuition="The system may be coverage-limited.",
        )
        events = diff_status(previous, current)
        self.assertIn("→ Cycle 4", events)
        self.assertTrue(any("H009" in event for event in events))
        self.assertIn("✓ State · S005", events)
        self.assertIn("✦ Research intuition formed", events)

    def test_run_lifecycle_reads_latest_and_closed_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "demo-project"
            runs = target / "research_record" / "runtime" / "tmp"
            first = runs / "run-old"
            second = runs / "run-new"
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            (first / "run.json").write_text(
                json.dumps({"run_id": "run-old", "kind": "run", "started_at": "2026-08-29T00:00:00+00:00", "status": "closed", "terminal_status": "converged"}),
                encoding="utf-8",
            )
            (second / "run.json").write_text(
                json.dumps({"run_id": "run-new", "kind": "resume", "started_at": "2026-08-29T01:00:00+00:00", "status": "running"}),
                encoding="utf-8",
            )

            latest = latest_run(target)
            self.assertIsNotNone(latest)
            assert latest is not None
            self.assertEqual(latest.run_id, "run-new")
            self.assertEqual(latest.status, "running")

            (second / "run.json").write_text(
                json.dumps({"run_id": "run-new", "kind": "resume", "started_at": "2026-08-29T01:00:00+00:00", "ended_at": "2026-08-29T01:30:00+00:00", "status": "closed", "terminal_status": "budget_exhausted"}),
                encoding="utf-8",
            )
            closed = read_run(target, "run-new")
            self.assertIsNotNone(closed)
            assert closed is not None
            self.assertEqual(closed.status, "closed")
            self.assertEqual(closed.terminal_status, "budget_exhausted")

    def test_dashboard_accumulates_read_only_semantic_events(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "demo-project"
            record = target / "research_record"
            runtime = record / "runtime"
            run_dir = runtime / "tmp" / "run-demo"
            run_dir.mkdir(parents=True)
            (record / "STATE.yaml").write_text("id: S001\n", encoding="utf-8")
            (record / "RESEARCH_RECORD.yaml").write_text("bottlenecks:\n", encoding="utf-8")
            (record / "RESEARCH_INTUITION.md").write_text("# Research Intuition\n\n## Intuitions\n", encoding="utf-8")
            (run_dir / "run.json").write_text(
                json.dumps({
                    "run_id": "run-demo",
                    "kind": "run",
                    "started_at": "2026-08-29T01:00:00+00:00",
                    "status": "running",
                }),
                encoding="utf-8",
            )

            dashboard = DashboardState(target)
            initial = dashboard.payload()
            self.assertEqual(initial["run"]["status"], "running")
            started = next(event for event in initial["events"] if "started" in event["text"])
            self.assertEqual(started["at"], "2026-08-29T01:00:00+00:00")

            (record / "STATE.yaml").write_text("id: S002\n", encoding="utf-8")
            (record / "RESEARCH_INTUITION.md").write_text(
                "# Research Intuition\n\n## Intuitions\n\nCoverage appears more limiting than capacity.\n",
                encoding="utf-8",
            )
            (run_dir / "run.json").write_text(
                json.dumps({
                    "run_id": "run-demo",
                    "kind": "run",
                    "started_at": "2026-08-29T01:00:00+00:00",
                    "ended_at": "2026-08-29T01:30:00+00:00",
                    "status": "closed",
                    "terminal_status": "converged",
                }),
                encoding="utf-8",
            )

            final = dashboard.payload()
            event_text = [event["text"] for event in final["events"]]
            self.assertIn("✓ State · S002", event_text)
            self.assertIn("✦ Research intuition formed", event_text)
            self.assertTrue(any("converged" in event for event in event_text))
            finished = next(event for event in final["events"] if "converged" in event["text"])
            self.assertEqual(finished["at"], "2026-08-29T01:30:00+00:00")
            self.assertEqual(final["run"]["terminal_status"], "converged")
            self.assertEqual(set(dashboard.raw_files()), set(RAW_FILES) | {"usage"})

    def test_dashboard_reads_baseline_run_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "demo-project"
            run_dir = target / ".git" / "research-agent-baseline" / "baseline-1"
            session = run_dir / "baseline"
            session.mkdir(parents=True)
            (run_dir / "run.json").write_text(
                json.dumps({
                    "run_id": "baseline-1",
                    "kind": "baseline",
                    "started_at": "2026-08-29T02:00:00+00:00",
                    "status": "closed",
                    "terminal_status": "completed",
                }),
                encoding="utf-8",
            )
            (session / "result.json").write_text(
                json.dumps({"status": "completed", "summary": "Blank control finished."}),
                encoding="utf-8",
            )
            (session / "model-usage.json").write_text(
                json.dumps({
                    "accounting_status": "measured",
                    "total": 1234,
                    "models": [{"role": "baseline", "runner": "codex", "model": "default", "total": 1234}],
                }),
                encoding="utf-8",
            )

            status = inspect_status(target)
            self.assertEqual(status.last_status, "completed")
            self.assertEqual(status.last_summary, "Blank control finished.")
            self.assertEqual(status.usage_total, 1234)
            self.assertEqual(latest_run(target).kind, "baseline")
            self.assertEqual(DashboardState(target).payload()["run"]["kind"], "baseline")

    def test_dashboard_projects_parallel_review_and_dynamic_raw_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "demo-project"
            record = target / "research_record"
            run_dir = record / "runtime" / "tmp" / "parallel-1"
            parallel = run_dir / "parallel"
            meta = run_dir / "meta"
            parallel.mkdir(parents=True)
            meta.mkdir(parents=True)
            (run_dir / "run.json").write_text(
                json.dumps({
                    "run_id": "parallel-1",
                    "kind": "parallel",
                    "started_at": "2026-08-29T03:00:00+00:00",
                    "status": "closed",
                    "terminal_status": "completed",
                }),
                encoding="utf-8",
            )
            (parallel / "manifest.json").write_text(
                json.dumps({
                    "parallel_id": "Pparallel",
                    "rounds": 2,
                    "rounds_log": [{
                        "round": 1,
                        "selected_branches": ["r1b2"],
                        "synthesis": {"status": "requested"},
                        "branches": [
                            {"branch_id": "r1b1", "kind": "replica", "round": 1, "status": "failed", "summary": "Rejected."},
                            {"branch_id": "r1b2", "kind": "replica", "round": 1, "status": "completed", "summary": "Selected."},
                        ],
                    }],
                }),
                encoding="utf-8",
            )
            (parallel / "result.json").write_text(
                json.dumps({
                    "parallel_id": "Pparallel",
                    "status": "completed",
                    "summary": "Parallel run completed.",
                    "rounds_completed": 1,
                    "selected_branches": ["r1b2"],
                    "synthesis": {"status": "disabled"},
                }),
                encoding="utf-8",
            )
            (parallel / "aggregate.md").write_text("# Aggregate\n", encoding="utf-8")
            (meta / "model-usage.json").write_text(
                json.dumps({"accounting_status": "measured", "total": 50, "models": []}),
                encoding="utf-8",
            )

            status = inspect_status(target)
            self.assertEqual(status.parallel_id, "Pparallel")
            self.assertEqual(status.parallel_rounds_completed, 1)
            self.assertEqual(status.parallel_rounds_total, 2)
            self.assertEqual(status.parallel_selected_branches, ("r1b2",))
            self.assertEqual(status.parallel_synthesis_status, "disabled")
            self.assertEqual(len(status.parallel_branches), 2)
            raw = DashboardState(target).raw_files()
            self.assertIn("parallel-manifest", raw)
            self.assertIn("parallel-result", raw)
            self.assertIn("parallel-aggregate", raw)

            (parallel / "result.json").unlink()
            active = inspect_status(target)
            self.assertEqual(active.parallel_selected_branches, ("r1b2",))
            self.assertEqual(active.parallel_synthesis_status, "requested")

    def test_dashboard_static_assets_exist(self) -> None:
        static_root = Path(__file__).resolve().parents[1] / "src" / "research_agent" / "ui" / "static"
        for name in ("index.html", "style.css", "app.js"):
            self.assertTrue((static_root / name).is_file(), name)
        index = (static_root / "index.html").read_text(encoding="utf-8")
        style = (static_root / "style.css").read_text(encoding="utf-8")
        app = (static_root / "app.js").read_text(encoding="utf-8")
        self.assertIn("experiment-result", index)
        self.assertIn("Run Summary", index)
        self.assertIn('id="best-score"', index)
        self.assertIn("Official Frontier", index)
        self.assertIn('id="token-total"', index)
        self.assertIn('id="parallel-card"', index)
        self.assertIn('id="final-result-primary"', index)
        self.assertIn('id="final-result-delta"', index)
        self.assertIn("grid-template-columns: repeat(7", style)
        self.assertIn("overflow-y: auto", style)
        self.assertIn('text("best-score"', app)
        self.assertIn("renderFinalResult", app)
        self.assertIn('id="run-duration"', index)
        self.assertIn('id="cycle-note"', index)
        self.assertIn("formatDuration", app)
        self.assertIn("research_cycle_id", app)


if __name__ == "__main__":
    unittest.main()
