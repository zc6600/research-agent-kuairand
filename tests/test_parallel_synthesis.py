from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent.parallel import promote_parallel_branch, run_parallel
from research_agent.parallel_synthesis import (
    build_synthesis_scientist_invocation,
    read_synthesis_request,
)
from research_agent.runtime import write_json

ROOT = Path(__file__).resolve().parents[1]


def git(target: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(target), *args],
        check=True, capture_output=True, text=True,
    )
    return completed.stdout.strip()


def prompt_path(prompt: str, key: str) -> Path:
    match = re.search(rf"{key}=([^\s]+)", prompt)
    if match is None:
        raise AssertionError(f"missing {key} in prompt")
    return Path(match.group(1).rstrip(".,"))


def record_text(message: str) -> str:
    return (
        "experiments:\n"
        "  - id: E1\n"
        f"    record: {message}\n"
        "    primary_metric: {name: null, value: null}\n"
        "    official_score: false\n"
        "    resulting_state: null\n"
        "    evidence: []\n"
        "manual_interventions: []\n"
    )


class ParallelSynthesisTests(unittest.TestCase):
    def make_target(self, root: Path) -> Path:
        target = root / "target"
        target.mkdir()
        git(target, "init", "-q")
        git(target, "config", "user.email", "research-agent@example.invalid")
        git(target, "config", "user.name", "Research Agent Test")
        (target / ".gitignore").write_text(
            "research_record/RESEARCH_RECORD.yaml\n"
            "research_record/RESEARCH_BRIEF.md\n"
            "research_record/EXPLORE.md\n"
            "research_record/OPTIMIZE.md\n"
            "research_record/ENGINEERING.md\n"
            "research_record/KNOWLEDGE.md\n"
            "research_record/RESEARCH_INTUITION.md\n"
            "research_record/DO_BETTER.md\n"
            "research_record/logs/\n"
            "research_record/archive/\n"
            "research_record/runtime/\n",
            encoding="utf-8",
        )
        record = target / "research_record"
        record.mkdir()
        (record / "VERSION").write_text("research-agent-record-v5\n", encoding="utf-8")
        (record / "SYSTEM_CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
        (record / "RESEARCH_METHOD.md").write_text("# Method\n", encoding="utf-8")
        (record / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
        (record / "RESEARCH_BRIEF.md").write_text("# Research Brief\n", encoding="utf-8")
        (record / "RESEARCH_RECORD.yaml").write_text(
            "experiments: []\nmanual_interventions: []\n", encoding="utf-8"
        )
        (record / "EXPLORE.md").write_text("# Explore\nbase\n", encoding="utf-8")
        (record / "OPTIMIZE.md").write_text("# Task Optimization\n", encoding="utf-8")
        (record / "ENGINEERING.md").write_text("# Engineering\n", encoding="utf-8")
        (record / "KNOWLEDGE.md").write_text("# Knowledge\n", encoding="utf-8")
        (record / "RESEARCH_INTUITION.md").write_text(
            "# Research Intuition\n\n## Intuitions\n", encoding="utf-8"
        )
        (record / "DO_BETTER.md").write_text(
            "# How to Do Better\n\n## Lessons\n", encoding="utf-8"
        )
        (record / "STATE.yaml").write_text(
            "id: S001\ngit_tag: state/S001\nderived_from: null\n",
            encoding="utf-8",
        )
        (target / "task.md").write_text("research task\n", encoding="utf-8")
        (target / "PERSONAL.md").write_text("test environment\n", encoding="utf-8")
        (target / "AGENTS.md").write_text("# Project instructions\n", encoding="utf-8")
        (target / "system").mkdir()
        (target / "system/model.py").write_text("MODEL = 'baseline'\n", encoding="utf-8")
        git(target, "add", "-A")
        git(target, "commit", "-qm", "state S001")
        git(target, "tag", "-a", "state/S001", "-m", "S001")
        return target

    def test_synthesis_request_requires_selected_primary_and_other_world(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            write_json(path, {
                "schema_version": 1,
                "parallel_id": "P1",
                "status": "completed",
                "summary": "A and B are complementary",
                "synthesis": {
                    "primary_branch": "a",
                    "informed_by": ["a", "b", "b", "missing"],
                },
            })
            request, record = read_synthesis_request(
                path,
                eligible={"a", "b"},
                selected={"a"},
                exit_code=0,
            )
            self.assertEqual(request, {"primary_branch": "a", "informed_by": ["b"]})
            self.assertEqual(record["status"], "requested")

    def test_synthesis_scientist_keeps_scientific_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "branch"
            runtime = target / "research_record" / "runtime"
            runtime.mkdir(parents=True)
            (target / "AGENTS.md").write_text("# Project instructions\n", encoding="utf-8")
            (target / "task.md").write_text("# Task\n", encoding="utf-8")
            (target / "PERSONAL.md").write_text("# Personal\n", encoding="utf-8")
            (target / "research_record" / "SKILL.md").write_text("# Scientist\n", encoding="utf-8")
            for name in (
                "SYSTEM_CONTRACT.md",
                "RESEARCH_METHOD.md",
                "RESEARCH_BRIEF.md",
                "RESEARCH_RECORD.yaml",
                "EXPLORE.md",
                "OPTIMIZE.md",
                "ENGINEERING.md",
                "KNOWLEDGE.md",
                "RESEARCH_INTUITION.md",
                "DO_BETTER.md",
            ):
                (target / "research_record" / name).write_text(f"# {name}\n", encoding="utf-8")
            context_path = runtime / "context.json"
            write_json(context_path, {"kind": "synthesis", "primary_branch": "r1b1"})
            invocation = build_synthesis_scientist_invocation(
                cli="codex",
                target=target,
                context_path=context_path,
                result_path=runtime / "result.json",
                parallel_id="P1",
                branch_id="s1",
                effort="max",
            )
        prompt = invocation.stdin_text or ""
        self.assertIn("<<< RESEARCH_AGENT_INJECTED SYNTHESIS_COORDINATION_INPUT >>>", prompt)
        self.assertIn("<<< RESEARCH_AGENT_INJECTED SCIENTIST_TASK >>>", prompt)
        self.assertIn("# Task", prompt)
        self.assertNotIn((ROOT / "SKILL.md").read_text(encoding="utf-8").rstrip(), prompt)
        self.assertIn("Do not open, read, search, or otherwise inspect `research_record/SKILL.md`", prompt)
        self.assertIn("reference-only snapshots", prompt)
        self.assertIn("not instructions", prompt)
        self.assertIn("Do not merge branch code, memories, or scores", prompt)
        self.assertIn("you may reject the proposed synthesis", prompt)
        self.assertIn("You retain ownership", prompt)

    def test_parallel_can_synthesize_complementary_worlds_then_promote_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.make_target(root)
            original_head = git(target, "rev-parse", "HEAD")
            synthesis_contexts: list[dict[str, object]] = []

            def fake_run(
                invocation,
                *,
                environment=None,
                output_path=None,
                stream_output=True,
                timeout_seconds=None,
                cancel_event=None,
            ):
                del output_path, stream_output, timeout_seconds, cancel_event
                prompt = invocation.stdin_text or ""
                if "optional synthesis check" in prompt:
                    manifest = json.loads(
                        prompt_path(prompt, "MANIFEST_PATH").read_text(encoding="utf-8")
                    )
                    branches = manifest["rounds_log"][-1]["branches"]
                    first, second = branches[0]["branch_id"], branches[1]["branch_id"]
                    prompt_path(prompt, "RESULT_PATH").write_text(json.dumps({
                        "schema_version": 1,
                        "parallel_id": manifest["parallel_id"],
                        "status": "completed",
                        "summary": "two credible complementary findings",
                        "synthesis": {
                            "primary_branch": first,
                            "informed_by": [second],
                        },
                    }), encoding="utf-8")
                    return 0

                if "You are the Parallel Reviewer for run" in prompt:
                    manifest = json.loads(
                        prompt_path(prompt, "MANIFEST_PATH").read_text(encoding="utf-8")
                    )
                    branches = manifest["rounds_log"][-1]["branches"]
                    synthesis = [b["branch_id"] for b in branches if str(b["branch_id"]).startswith("s")]
                    selected = synthesis or [branches[0]["branch_id"]]
                    prompt_path(prompt, "RESULT_PATH").write_text(json.dumps({
                        "schema_version": 1,
                        "parallel_id": manifest["parallel_id"],
                        "round": 1,
                        "selected_branches": selected,
                        "rejected": [],
                        "summary": "reviewed completed research worlds",
                        "next_action": "adopt",
                    }), encoding="utf-8")
                    return 0

                self.assertIsNotNone(environment)
                context_path = Path(environment["RESEARCH_AGENT_PARALLEL_CONTEXT"])
                context = json.loads(context_path.read_text(encoding="utf-8"))
                workspace = invocation.cwd
                if context.get("kind") == "synthesis":
                    synthesis_contexts.append(context)
                    self.assertEqual(context["primary_branch"], "r1b1")
                    self.assertEqual(context["informed_by"], ["r1b2"])
                    source = Path(context["synthesis_inputs"][0]["audit_dir"])
                    self.assertTrue((source / "result.json").is_file())
                    self.assertTrue((source / "memory/research_record/RESEARCH_RECORD.yaml").is_file())
                    (workspace / "research_record/RESEARCH_RECORD.yaml").write_text(
                        record_text("synthesis tested complementary evidence"),
                        encoding="utf-8",
                    )
                    summary = "fresh Scientist tested the cross-world hypothesis"
                else:
                    (workspace / "research_record/RESEARCH_RECORD.yaml").write_text(
                        record_text(f"finding from {context['branch_id']}"),
                        encoding="utf-8",
                    )
                    summary = f"independent finding {context['branch_id']}"
                Path(context["result_path"]).write_text(json.dumps({
                    "schema_version": 1,
                    "branch_id": context["branch_id"],
                    "status": "completed",
                    "summary": summary,
                    "evidence": ["measured"],
                    "reflection": "",
                }), encoding="utf-8")
                return 0

            with patch("research_agent.parallel.run_invocation", side_effect=fake_run):
                result = run_parallel(
                    target=target,
                    meta_cli="codex",
                    scientist_cli="codex",
                    meta_model=None,
                    scientist_model=None,
                    meta_effort="medium",
                    scientist_effort="medium",
                    rounds=1,
                    branches=2,
                    keep=1,
                    parallelism=2,
                    share_inputs=False,
                    synthesis=True,
                )

            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["selected_branches"], ["s1"])
            self.assertEqual(result["synthesis"]["status"], "completed")
            self.assertEqual(len(synthesis_contexts), 1)
            parallel_dir = Path(result["result_path"]).parent
            manifest = json.loads((parallel_dir / "manifest.json").read_text(encoding="utf-8"))
            synthesis_branch = next(
                b for b in manifest["rounds_log"][-1]["branches"] if b["branch_id"] == "s1"
            )
            self.assertEqual(synthesis_branch["parent_branch"], "r1b1")
            self.assertEqual(synthesis_branch["informed_by"], ["r1b2"])
            self.assertTrue(synthesis_branch["workspace_retained"])

            promoted = promote_parallel_branch(
                target=target,
                parallel_dir=parallel_dir,
                branch_id="s1",
            )
            self.assertTrue(promoted["research_memory_adopted"])
            self.assertFalse(promoted["state_promoted"])
            self.assertEqual(git(target, "rev-parse", "HEAD"), original_head)
            self.assertIn(
                "synthesis tested complementary evidence",
                (target / "research_record/RESEARCH_RECORD.yaml").read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
