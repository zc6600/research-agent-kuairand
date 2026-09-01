from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent.telemetry import collect_runner, subtract_reports


class TelemetryTests(unittest.TestCase):
    def test_unavailable_telemetry_does_not_invent_zero_counters(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            with patch("research_agent.telemetry.Path.home", return_value=home):
                report = collect_runner("opencode", (home / "target",))
            self.assertEqual(report["accounting_status"], "unavailable")
            self.assertNotIn("sessions", report)
            for field in ("input", "output", "reasoning", "cache_read", "cache_write", "total"):
                self.assertNotIn(field, report)

    def test_opencode_uses_session_counters_for_selected_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            database = home / ".local" / "share" / "opencode" / "opencode.db"
            database.parent.mkdir(parents=True)
            connection = sqlite3.connect(database)
            connection.execute(
                "create table session (id text, directory text, tokens_input integer, tokens_output integer, "
                "tokens_reasoning integer, tokens_cache_read integer, tokens_cache_write integer)"
            )
            connection.execute(
                "insert into session values (?, ?, ?, ?, ?, ?, ?)",
                ("selected", str(home / "target"), 10, 5, 2, 3, 1),
            )
            connection.execute(
                "insert into session values (?, ?, ?, ?, ?, ?, ?)",
                ("unrelated", str(home / "other"), 100, 100, 100, 100, 100),
            )
            connection.commit()
            connection.close()
            with patch("research_agent.telemetry.Path.home", return_value=home):
                report = collect_runner("opencode", (home / "target",))
            self.assertEqual(report["sessions"], 1)
            self.assertEqual(report["total"], 21)

    def test_manual_collection_can_include_multiple_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            projects = home / ".claude" / "projects" / "sample"
            projects.mkdir(parents=True)
            values = [
                {
                    "type": "assistant",
                    "uuid": "one",
                    "sessionId": "meta",
                    "cwd": str(home / "extra"),
                    "message": {"usage": {"input_tokens": 10, "output_tokens": 2}},
                },
                {
                    "type": "assistant",
                    "uuid": "two",
                    "sessionId": "scientist",
                    "cwd": str(home / "target"),
                    "message": {
                        "usage": {
                            "input_tokens": 5,
                            "output_tokens": 1,
                            "cache_read_input_tokens": 4,
                            "cache_creation_input_tokens": 3,
                        }
                    },
                },
            ]
            (projects / "session.jsonl").write_text(
                "".join(json.dumps(value) + "\n" for value in values), encoding="utf-8"
            )
            with patch("research_agent.telemetry.Path.home", return_value=home):
                report = collect_runner("claude", (home / "target", home / "extra"))
            self.assertEqual(report["sessions"], 2)
            self.assertEqual(report["total"], 25)

    def test_codex_manual_collection_can_include_an_extra_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_home = root / "codex"
            codex_home.mkdir()
            rollout = root / "rollout.jsonl"
            rollout.write_text(
                json.dumps(
                    {
                        "payload": {
                            "info": {
                                "total_token_usage": {
                                    "input_tokens": 12,
                                    "output_tokens": 3,
                                    "reasoning_output_tokens": 1,
                                    "cached_input_tokens": 2,
                                    "total_tokens": 15,
                                }
                            }
                        }
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            database = codex_home / "state_5.sqlite"
            connection = sqlite3.connect(database)
            connection.execute("create table threads (id text, tokens_used integer, rollout_path text, cwd text)")
            connection.execute(
                "insert into threads values (?, ?, ?, ?)",
                ("meta", 15, str(rollout), str(root / "extra")),
            )
            connection.commit()
            connection.close()
            with patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}):
                report = collect_runner("codex", (root / "target", root / "extra"))
            self.assertEqual(report["sessions"], 1)
            self.assertEqual(report["total"], 15)

    def test_run_delta_subtracts_comparable_baseline(self) -> None:
        before = {"runner": "codex", "accounting_status": "measured", "sessions": 2, "total": 100}
        after = {"runner": "codex", "accounting_status": "measured", "sessions": 4, "total": 160}
        report = subtract_reports(after, before)
        self.assertNotIn("sessions", report)
        self.assertEqual(report["total"], 60)
        self.assertEqual(report["scope"], "run_delta")
        self.assertEqual(report["baseline_status"], "measured")

    def test_run_delta_is_unavailable_without_measured_baseline(self) -> None:
        before = {"runner": "codex", "accounting_status": "unavailable", "reason": "no session yet"}
        after = {"runner": "codex", "accounting_status": "measured", "sessions": 1, "total": 160}
        report = subtract_reports(after, before)
        self.assertEqual(report["accounting_status"], "unavailable")
        self.assertEqual(report["scope"], "run_delta")
        self.assertNotIn("total", report)
        self.assertIn("comparable measured", report["reason"])

    def test_run_delta_is_unavailable_if_counter_moves_backwards(self) -> None:
        before = {"runner": "codex", "accounting_status": "measured", "total": 160}
        after = {"runner": "codex", "accounting_status": "measured", "total": 100}
        report = subtract_reports(after, before)
        self.assertEqual(report["accounting_status"], "unavailable")
        self.assertNotIn("total", report)
        self.assertIn("moved backwards", report["reason"])

    def test_total_only_snapshot_publishes_only_total_delta(self) -> None:
        before = {
            "runner": "codex", "accounting_status": "measured", "breakdown_status": "total_only",
            "input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0, "total": 100,
        }
        after = {
            "runner": "codex", "accounting_status": "measured", "breakdown_status": "complete",
            "input": 120, "output": 30, "reasoning": 5, "cache_read": 10, "cache_write": 0, "total": 160,
        }
        report = subtract_reports(after, before)
        self.assertEqual(report["accounting_status"], "measured")
        self.assertEqual(report["breakdown_status"], "total_only")
        self.assertEqual(report["total"], 60)
        for field in ("input", "output", "reasoning", "cache_read", "cache_write"):
            self.assertNotIn(field, report)


if __name__ == "__main__":
    unittest.main()
