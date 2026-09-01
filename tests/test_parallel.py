from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent.bootstrap import BootstrapError
from research_agent.cli import build_parser
from research_agent.parallel import (
    _branch_specs,
    _parallel_usage_report,
    build_parallel_reviewer_invocation,
    build_parallel_scientist_invocation,
    promote_parallel_branch,
    run_parallel,
)
from research_agent.parallel_support import snapshot_memory
from research_agent.runners.base import Invocation
from research_agent.runtime import write_json

ROOT = Path(__file__).resolve().parents[1]


def prompt_text(invocation: Invocation) -> str:
    return invocation.stdin_text or invocation.argv[-1]


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


class ParallelTests(unittest.TestCase):
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
        reports = record / "reports"
        reports.mkdir(exist_ok=True)
        (reports / "init.md").write_text("# Init\n", encoding="utf-8")
        (record / "STATE.yaml").write_text(
            "id: S001\ngit_tag: state/S001\nderived_from: null\nscientist_report: research_record/reports/init.md\n",
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

    def test_parallel_parser_is_opt_in_and_tree_is_gone(self) -> None:
        args = build_parser().parse_args([
            "parallel", "--target", "/tmp/project", "--cli", "codex",
            "--allow-edits", "--rounds", "2", "--branches", "3", "--keep", "2",
        ])
        self.assertEqual(args.command, "parallel")
        self.assertEqual((args.rounds, args.branches, args.keep), (2, 3, 2))
        with self.assertRaises(SystemExit):
            build_parser().parse_args([
                "tree", "--target", "/tmp/project", "--cli", "codex", "--allow-edits",
            ])

    def test_parallel_has_no_scientific_planner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "branch"
            record = target / "research_record"
            runtime = record / "runtime"
            runtime.mkdir(parents=True)
            (target / "AGENTS.md").write_text("# Project instructions\n", encoding="utf-8")
            (target / "task.md").write_text("# Task\n", encoding="utf-8")
            (target / "PERSONAL.md").write_text("# Personal\n", encoding="utf-8")
            (record / "SKILL.md").write_text("# Scientist\n", encoding="utf-8")
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
                (record / name).write_text(f"# {name}\n", encoding="utf-8")
            context_path = runtime / "context.json"
            write_json(context_path, {"branch_id": "r1b1", "constraints": [], "budget": {}})
            control = root / "control"
            control.mkdir()
            control_record = control / "research_record"
            control_record.mkdir()
            (control / "AGENTS.md").write_text("# Project instructions\n", encoding="utf-8")
            (control / "task.md").write_text("# Task\n", encoding="utf-8")
            (control / "PERSONAL.md").write_text("# Personal\n", encoding="utf-8")
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
                (control_record / name).write_text(f"# {name}\n", encoding="utf-8")
            manifest_path = control / "manifest.json"
            write_json(manifest_path, {"parallel_id": "P1", "rounds_log": []})
            scientist = build_parallel_scientist_invocation(
                cli="codex",
                target=target,
                context_path=context_path,
                result_path=runtime / "result.json",
                parallel_id="P1",
                branch_id="r1b1",
                round_number=1,
                effort="max",
            )
            reviewer = build_parallel_reviewer_invocation(
                cli="codex",
                target=control,
                manifest_path=manifest_path,
                result_path=control / "review.json",
                parallel_id="P1",
                round_number=1,
                keep=1,
                candidate_branches=["r1b1", "r1b2"],
                effort="max",
            )
        scientist_prompt = prompt_text(scientist)
        reviewer_prompt = prompt_text(reviewer)
        self.assertIn("formal coordination input instead of RESEARCH_AGENT_BRIEF", scientist_prompt)
        self.assertIn("does not assign a scientific question", scientist_prompt)
        self.assertIn("Independently reconstruct", scientist_prompt)
        self.assertIn("<<< RESEARCH_AGENT_INJECTED PARALLEL_COORDINATION_INPUT >>>", scientist_prompt)
        self.assertIn("<<< RESEARCH_AGENT_INJECTED SCIENTIST_TASK >>>", scientist_prompt)
        self.assertIn("# Task", scientist_prompt)
        self.assertNotIn((ROOT / "SKILL.md").read_text(encoding="utf-8").rstrip(), scientist_prompt)
        self.assertIn("Do not open, read, search, or otherwise inspect `research_record/SKILL.md`", scientist_prompt)
        self.assertNotIn("planner", scientist_prompt.lower())
        self.assertIn("Review only completed research", reviewer_prompt)
        self.assertIn("do not prescribe", reviewer_prompt)
        self.assertIn("next_action process-level only", reviewer_prompt)
        self.assertIn("<<< RESEARCH_AGENT_INJECTED PARALLEL_MANIFEST >>>", reviewer_prompt)
        self.assertIn("<<< RESEARCH_AGENT_INJECTED META_TASK >>>", reviewer_prompt)
        self.assertIn("# Task", reviewer_prompt)
        self.assertNotIn((ROOT / "SKILL.md").read_text(encoding="utf-8").rstrip(), reviewer_prompt)
        self.assertNotIn("bottleneck understanding", reviewer_prompt.lower())
        self.assertNotIn("Tree", reviewer_prompt)

    def test_branch_generation_is_mechanical(self) -> None:
        specs = _branch_specs(
            ["root"], round_number=1, branches=3, existing=set()
        )
        self.assertEqual(
            specs,
            [
                {"branch_id": "r1b1", "parent_branch": "root", "replica": 1},
                {"branch_id": "r1b2", "parent_branch": "root", "replica": 2},
                {"branch_id": "r1b3", "parent_branch": "root", "replica": 3},
            ],
        )
        self.assertNotIn("question", specs[0])
        self.assertNotIn("instructions", specs[0])

    def test_share_inputs_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_target(Path(temporary))
            with self.assertRaisesRegex(BootstrapError, "share-inputs is disabled"):
                run_parallel(
                    target=target,
                    meta_cli="codex",
                    scientist_cli="codex",
                    meta_model=None,
                    scientist_model=None,
                    meta_effort="medium",
                    scientist_effort="medium",
                    rounds=1,
                    branches=1,
                    keep=1,
                    parallelism=1,
                    share_inputs=True,
                )

    def test_missing_injected_scientist_file_closes_and_cleans_bootstrap_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.make_target(root)
            git(target, "rm", "-q", "AGENTS.md")
            git(target, "commit", "-qm", "remove optional project instructions")

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
            )

            self.assertEqual(result["status"], "failed")
            parallel_dir = Path(result["result_path"]).parent
            run_metadata = json.loads((parallel_dir.parent / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_metadata["status"], "closed")
            self.assertEqual(run_metadata["terminal_status"], "failed")
            manifest = json.loads((parallel_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(all(not Path(branch["workspace"]).exists() for branch in manifest["rounds_log"][0]["branches"]))
            self.assertFalse(Path(manifest["worktree_root"]).exists())

    def test_parallel_scientists_choose_independently_and_context_is_formal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_target(Path(temporary))
            seen_contexts: list[dict[str, object]] = []

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
                prompt = prompt_text(invocation)
                if "You are the Parallel Reviewer for run" in prompt:
                    manifest = json.loads(
                        prompt_path(prompt, "MANIFEST_PATH").read_text(encoding="utf-8")
                    )
                    branches = manifest["rounds_log"][-1]["branches"]
                    prompt_path(prompt, "RESULT_PATH").write_text(json.dumps({
                        "schema_version": 1,
                        "parallel_id": manifest["parallel_id"],
                        "round": 1,
                        "selected_branches": [branches[0]["branch_id"]],
                        "rejected": [],
                        "summary": "best research world",
                        "next_action": "adopt",
                    }), encoding="utf-8")
                    return 0

                self.assertIsNotNone(environment)
                context_path = Path(environment["RESEARCH_AGENT_PARALLEL_CONTEXT"])
                context = json.loads(context_path.read_text(encoding="utf-8"))
                seen_contexts.append(context)
                self.assertNotIn("RESEARCH_AGENT_BRIEF", environment)
                self.assertNotIn("question", context)
                self.assertNotIn("instructions", context)
                self.assertIn("base_state", context)
                self.assertIn("constraints", context)
                self.assertIn("budget", context)
                workspace = invocation.cwd
                (workspace / "research_record/RESEARCH_RECORD.yaml").write_text(
                    f"branch: {context['branch_id']}\n", encoding="utf-8"
                )
                Path(context["result_path"]).write_text(json.dumps({
                    "schema_version": 1,
                    "branch_id": context["branch_id"],
                    "status": "completed",
                    "summary": "independent diagnostic",
                    "evidence": ["diagnostic"],
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
                )

            self.assertEqual(result["status"], "completed")
            self.assertEqual(len(seen_contexts), 2)
            self.assertEqual({x["replica"] for x in seen_contexts}, {1, 2})
            self.assertEqual(
                (target / "research_record/RESEARCH_RECORD.yaml").read_text(encoding="utf-8"),
                "experiments: []\nmanual_interventions: []\n",
            )

    def test_parallel_keeps_incumbent_without_planner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_target(Path(temporary))

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
                prompt = prompt_text(invocation)
                if "You are the Parallel Reviewer for run" in prompt:
                    manifest = json.loads(
                        prompt_path(prompt, "MANIFEST_PATH").read_text(encoding="utf-8")
                    )
                    round_number = len(manifest["rounds_log"])
                    if round_number == 1:
                        selected = [
                            branch["branch_id"]
                            for branch in manifest["rounds_log"][-1]["branches"]
                        ]
                    else:
                        selected = [manifest["rounds_log"][0]["selected_branches"][0]]
                    prompt_path(prompt, "RESULT_PATH").write_text(json.dumps({
                        "schema_version": 1,
                        "parallel_id": manifest["parallel_id"],
                        "round": round_number,
                        "selected_branches": selected,
                        "rejected": [],
                        "summary": "incumbent remains strongest",
                        "next_action": "keep incumbent",
                    }), encoding="utf-8")
                    return 0

                context = json.loads(
                    Path(environment["RESEARCH_AGENT_PARALLEL_CONTEXT"])
                    .read_text(encoding="utf-8")
                )
                Path(context["result_path"]).write_text(json.dumps({
                    "schema_version": 1,
                    "branch_id": context["branch_id"],
                    "status": "completed",
                    "summary": "diagnostic",
                    "evidence": ["marker"],
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
                    rounds=2,
                    branches=2,
                    keep=2,
                    parallelism=2,
                    share_inputs=False,
                )

            first = json.loads(
                (Path(result["result_path"]).parent / "manifest.json").read_text(encoding="utf-8")
            )["rounds_log"][0]["selected_branches"][0]
            self.assertEqual(result["selected_branches"], [first])

    def test_usage_aggregates_reviewer_and_scientist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parallel_dir = Path(temporary)
            write_json(parallel_dir / "meta/reviewer-r1/meta/model-usage.json", {
                "models": [{
                    "role": "meta", "runner": "codex", "model": "m",
                    "accounting_status": "measured", "total": 10,
                }]
            })
            write_json(parallel_dir / "usage/r1b1/scientist/x.usage.json", {
                "models": [{
                    "role": "scientist", "runner": "codex", "model": "m",
                    "accounting_status": "measured", "total": 20,
                }]
            })
            self.assertEqual(_parallel_usage_report(parallel_dir)["total"], 30)

    def _manual_runtime(
        self,
        target: Path,
        temporary: Path,
        *,
        with_state: bool,
        derived_from: str = "S001",
    ) -> tuple[Path, Path, str]:
        base_commit = git(target, "rev-parse", "HEAD")
        workspace = temporary / "candidate"
        subprocess.run(
            ["git", "-C", str(target), "worktree", "add", "--detach", str(workspace), base_commit],
            check=True, capture_output=True, text=True,
        )
        for name in ("EXPLORE.md", "OPTIMIZE.md", "ENGINEERING.md", "KNOWLEDGE.md"):
            src = target / "research_record" / name
            if src.is_file():
                (workspace / "research_record" / name).write_bytes(src.read_bytes())
        (workspace / "research_record/RESEARCH_RECORD.yaml").write_text(
            "experiments:\n  - id: EFAIL\n    record: failed experiment preserved\n"
            "    primary_metric: {name: null, value: null}\n"
            "    official_score: false\n"
            "    resulting_state: null\n"
            "    evidence: []\nmanual_interventions: []\n",
            encoding="utf-8",
        )
        if with_state:
            (workspace / "system/model.py").write_text("MODEL = 'candidate'\n", encoding="utf-8")
            reports = workspace / "research_record" / "reports"
            reports.mkdir(parents=True, exist_ok=True)
            (reports / "branch-b1.md").write_text("# Branch b1\n", encoding="utf-8")
            (workspace / "research_record/STATE.yaml").write_text(
                f"id: S002\ngit_tag: state/S002\nderived_from: {derived_from}\n"
                "scientist_report: research_record/reports/branch-b1.md\n",
                encoding="utf-8",
            )
            git(workspace, "add", "system", "research_record/STATE.yaml")
            git(workspace, "commit", "-qm", "candidate S002")
        candidate_commit = git(workspace, "rev-parse", "HEAD")

        parallel_dir = target / "research_record/runtime/parallel-test"
        base_memory = parallel_dir / "base-memory"
        branch_memory = parallel_dir / "branches/r1b1-memory"
        snapshot_memory(target, base_memory, include_meta=False)
        snapshot_memory(workspace, branch_memory, include_meta=False)

        write_json(parallel_dir / "manifest.json", {
            "schema_version": 1,
            "kind": "parallel",
            "parallel_id": "P1",
            "target": str(target.resolve()),
            "base_commit": base_commit,
            "base_memory_snapshot": str(base_memory),
            "rounds_log": [{
                "round": 1,
                "branches": [{
                    "branch_id": "b1",
                    "parent_branch": "root",
                    "base_commit": base_commit,
                    "base_state": {"id": "S001", "git_tag": "state/S001"},
                    "workspace": str(workspace),
                    "candidate_commit": candidate_commit,
                    "candidate_state_id": "S002",
                    "memory_snapshot": str(branch_memory),
                    "system_state_dirty": False,
                }],
            }],
        })
        write_json(parallel_dir / "result.json", {
            "schema_version": 1,
            "parallel_id": "P1",
            "status": "completed",
            "selected_branches": ["b1"],
        })
        return parallel_dir, workspace, candidate_commit

    def test_promote_adopts_research_memory_and_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.make_target(root)
            parallel_dir, workspace, candidate_commit = self._manual_runtime(
                target, root, with_state=True
            )
            result = promote_parallel_branch(
                target=target, parallel_dir=parallel_dir, branch_id="b1"
            )
            self.assertTrue(result["research_memory_adopted"])
            self.assertTrue(result["state_promoted"])
            self.assertEqual(result["state_id"], "S002")
            self.assertEqual(git(target, "rev-parse", "HEAD"), candidate_commit)
            self.assertIn(
                "failed experiment preserved",
                (target / "research_record/RESEARCH_RECORD.yaml").read_text(encoding="utf-8"),
            )
            self.assertFalse(workspace.exists())

    def test_diagnostic_only_branch_can_be_promoted_as_research_world(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.make_target(root)
            original_head = git(target, "rev-parse", "HEAD")
            parallel_dir, workspace, _ = self._manual_runtime(
                target, root, with_state=False
            )
            result = promote_parallel_branch(
                target=target, parallel_dir=parallel_dir, branch_id="b1"
            )
            self.assertTrue(result["research_memory_adopted"])
            self.assertFalse(result["state_promoted"])
            self.assertEqual(git(target, "rev-parse", "HEAD"), original_head)
            self.assertIn(
                "failed experiment preserved",
                (target / "research_record/RESEARCH_RECORD.yaml").read_text(encoding="utf-8"),
            )
            self.assertFalse(workspace.exists())

    def test_promote_refuses_to_overwrite_newer_research_memory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.make_target(root)
            parallel_dir, _, _ = self._manual_runtime(target, root, with_state=False)
            (target / "research_record/RESEARCH_RECORD.yaml").write_text(
                "experiments:\n  - id: ENEW\n    record: newer serial research\n"
                "    primary_metric: {name: null, value: null}\n"
                "    official_score: false\n"
                "    resulting_state: null\n"
                "    evidence: []\nmanual_interventions: []\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(BootstrapError, "research memory changed"):
                promote_parallel_branch(
                    target=target, parallel_dir=parallel_dir, branch_id="b1"
                )

    def test_promote_validates_state_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = self.make_target(root)
            parallel_dir, _, _ = self._manual_runtime(
                target, root, with_state=True, derived_from="WRONG"
            )
            with self.assertRaisesRegex(BootstrapError, "derived_from"):
                promote_parallel_branch(
                    target=target, parallel_dir=parallel_dir, branch_id="b1"
                )


if __name__ == "__main__":
    unittest.main()
