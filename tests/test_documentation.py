from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "assets" / "project-template" / "research_record"
MAINTAINED_DOCS = (
    ROOT / "README.md",
    ROOT / "SKILL.md",
    ROOT / "assets" / "project-template" / "AGENTS.block.md",
    RECORD / "SKILL.md",
    RECORD / "SYSTEM_CONTRACT.md",
    RECORD / "RESEARCH_METHOD.md",
    RECORD / "RESEARCH_BRIEF.md",
    RECORD / "EXPLORE.md",
    RECORD / "OPTIMIZE.md",
    RECORD / "ENGINEERING.md",
    RECORD / "KNOWLEDGE.md",
    RECORD / "RESEARCH_INTUITION.md",
    RECORD / "DO_BETTER.md",
    RECORD / "runtime" / "README.md",
    *(ROOT / "references").glob("*.md"),
)


class DocumentationTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self) -> None:
        link_pattern = re.compile(r"\[[^]]+\]\(([^)]+)\)")
        for document in MAINTAINED_DOCS:
            content = document.read_text(encoding="utf-8")
            for raw_target in link_pattern.findall(content):
                target = raw_target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (document.parent / target).resolve()
                with self.subTest(document=document.relative_to(ROOT), target=target):
                    self.assertTrue(resolved.exists(), f"broken local link: {resolved}")

    def test_generic_package_does_not_own_competition_inputs(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertTrue((ROOT / "competitions" / "kuairand" / "task.md").is_file())
        self.assertFalse((ROOT / "task.md").exists())
        self.assertNotIn('"task.md" = "research_agent/bundle/task.md"', pyproject)

    def test_record_v5_template_contains_complete_research_environment(self) -> None:
        self.assertEqual((RECORD / "VERSION").read_text(encoding="utf-8").strip(), "research-agent-record-v5")
        for name in (
            "RESEARCH_BRIEF.md",
            "RESEARCH_RECORD.yaml",
            "EXPLORE.md",
            "OPTIMIZE.md",
            "ENGINEERING.md",
            "KNOWLEDGE.md",
            "RESEARCH_INTUITION.md",
            "DO_BETTER.md",
        ):
            with self.subTest(name=name):
                self.assertTrue((RECORD / name).is_file())

    def test_state_boundary_remains_system_only_and_meta_described(self) -> None:
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (RECORD / "SYSTEM_CONTRACT.md").read_text(encoding="utf-8")
        scientist = (RECORD / "SKILL.md").read_text(encoding="utf-8")
        method = (RECORD / "RESEARCH_METHOD.md").read_text(encoding="utf-8")
        schema = (RECORD / "schema" / "STATE.yaml").read_text(encoding="utf-8")

        for text in (root_skill, contract, scientist, method, schema):
            self.assertIn("system/**", text)
        self.assertIn("not the research diary", contract)
        self.assertIn("State creation happens after a Scientist session", contract)
        self.assertIn("`research_record/STATE.yaml` | META", contract)
        self.assertIn("`system/**` | Scientist only", contract)
        self.assertIn("Do **not** edit, create, or rewrite `research_record/STATE.yaml`", scientist)
        self.assertIn("META decides whether the retained `system/**` should be crystallized", scientist)
        self.assertIn("META-authored descriptive/provenance metadata", method)
        self.assertIn("由 META 在 Scientist session 结束后写入", schema)

    def test_state_points_to_existing_scientist_report(self) -> None:
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (RECORD / "SYSTEM_CONTRACT.md").read_text(encoding="utf-8")
        method = (RECORD / "RESEARCH_METHOD.md").read_text(encoding="utf-8")
        schema = (RECORD / "schema" / "STATE.yaml").read_text(encoding="utf-8")

        for text in (root_skill, contract, method, schema):
            self.assertIn("scientist_report", text)
        self.assertIn("verify that its report exists", root_skill)
        self.assertIn("completed free-form Scientist report", contract)
        self.assertIn("already existing", method)

    def test_scientist_is_not_bottleneck_bound(self) -> None:
        scientist = (RECORD / "SKILL.md").read_text(encoding="utf-8")
        method = (RECORD / "RESEARCH_METHOD.md").read_text(encoding="utf-8")
        contract = (RECORD / "SYSTEM_CONTRACT.md").read_text(encoding="utf-8")
        runtime_doc = (RECORD / "runtime" / "README.md").read_text(encoding="utf-8")

        self.assertIn("no required bottleneck state machine", scientist)
        self.assertIn("no requirement to stay inside one named bottleneck", scientist)
        self.assertIn("no required bottleneck lifecycle", method)
        self.assertIn("not constrained by a bottleneck lifecycle", contract)

        for text in (scientist, method, runtime_doc):
            self.assertNotIn("status: <forming | active | closed>", text)
            self.assertNotIn("that bottleneck defines the iteration boundary", text)
            self.assertNotIn("do not switch bottlenecks", text.lower())
            self.assertNotIn("bottleneck-bounded", text.lower())

    def test_hypotheses_and_exploration_are_both_supported(self) -> None:
        scientist = (RECORD / "SKILL.md").read_text(encoding="utf-8")
        method = (RECORD / "RESEARCH_METHOD.md").read_text(encoding="utf-8")

        self.assertIn("make the working hypothesis explicit", scientist)
        self.assertIn("Exploratory experiments are also allowed", scientist)
        self.assertIn("Hypotheses are valuable", method)
        self.assertIn("record it as exploratory", method)

    def test_shared_environment_memory_has_shared_write_ownership(self) -> None:
        contract = (RECORD / "SYSTEM_CONTRACT.md").read_text(encoding="utf-8")
        scientist = (RECORD / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("`EXPLORE.md`, `OPTIMIZE.md`, `ENGINEERING.md`, `KNOWLEDGE.md` | META and Scientist", contract)
        self.assertIn("not read-only during a Scientist session", scientist)
        for name in ("EXPLORE.md", "OPTIMIZE.md", "ENGINEERING.md", "KNOWLEDGE.md"):
            content = (RECORD / name).read_text(encoding="utf-8")
            with self.subTest(name=name):
                self.assertIn("shared research-environment memory", content)
                self.assertIn("META may initialize or curate", content)
                self.assertIn("Scientist", content)

    def test_explore_and_knowledge_are_memory_not_workflow_gates(self) -> None:
        explore = (RECORD / "EXPLORE.md").read_text(encoding="utf-8")
        knowledge = (RECORD / "KNOWLEDGE.md").read_text(encoding="utf-8")
        self.assertIn("Unknown facts may remain unknown until they matter", explore)
        self.assertNotIn("pending` / `complete` / `blocked", explore)
        self.assertNotIn("第一次形成 bottleneck", explore)
        self.assertIn("Do not search literature merely to populate this file", knowledge)
        self.assertNotIn("打开新的 bottleneck", knowledge)

    def test_optimize_separates_task_tricks_from_research_method(self) -> None:
        optimize = (RECORD / "OPTIMIZE.md").read_text(encoding="utf-8")
        scientist = (RECORD / "SKILL.md").read_text(encoding="utf-8")
        method = (RECORD / "RESEARCH_METHOD.md").read_text(encoding="utf-8")

        self.assertIn("task-specific strategy", optimize)
        self.assertIn("Full evaluations as scarce decision points", optimize)
        self.assertIn("Skip the gate when reduced fidelity would distort", optimize)
        self.assertIn("research_record/OPTIMIZE.md", scientist)
        self.assertIn("Task-specific benchmark tactics belong in `OPTIMIZE.md`", method)

    def test_meta_owns_cumulative_memory_and_state_without_owning_science(self) -> None:
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (RECORD / "SYSTEM_CONTRACT.md").read_text(encoding="utf-8")
        scientist = (RECORD / "SKILL.md").read_text(encoding="utf-8")

        for text in (root_skill, contract):
            for name in (
                "RESEARCH_RECORD.yaml", "RESEARCH_BRIEF.md", "RESEARCH_INTUITION.md",
                "DO_BETTER.md", "STATE.yaml",
            ):
                self.assertIn(name, text)
        self.assertIn("append complete experiment entries", contract)
        self.assertIn("must **not** choose or prescribe", contract)
        self.assertIn("must **not edit the contents of `system/**`**", contract)
        self.assertIn("Describe what is known; do not prescribe", root_skill)
        self.assertIn("Do not edit `RESEARCH_RECORD.yaml`, `RESEARCH_BRIEF.md`, `RESEARCH_INTUITION.md`, `DO_BETTER.md`, or `STATE.yaml`", scientist)

    def test_fresh_scientist_inherits_intuition_and_process_progress(self) -> None:
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (RECORD / "SYSTEM_CONTRACT.md").read_text(encoding="utf-8")
        scientist = (RECORD / "SKILL.md").read_text(encoding="utf-8")
        intuition = (RECORD / "RESEARCH_INTUITION.md").read_text(encoding="utf-8")
        do_better = (RECORD / "DO_BETTER.md").read_text(encoding="utf-8")

        self.assertIn("cognitively fresh, not scientifically blank", root_skill)
        self.assertIn("RESEARCH_INTUITION.md` and `research_record/DO_BETTER.md", scientist)
        self.assertIn("launcher-injected shared-memory stack", contract)
        self.assertIn("every fresh Scientist reads it during cold start", intuition)
        self.assertIn("every fresh Scientist reads it during cold start", do_better)
        self.assertIn("not as an instruction or authority", intuition)
        self.assertIn("not as a mandatory workflow", do_better)

    def test_scientist_report_is_persisted_but_unstructured(self) -> None:
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        scientist = (RECORD / "SKILL.md").read_text(encoding="utf-8")
        contract = (RECORD / "SYSTEM_CONTRACT.md").read_text(encoding="utf-8")

        self.assertIn("free-form Scientist reports", root_skill)
        self.assertIn("cycle-$RESEARCH_AGENT_CYCLE.md", scientist)
        self.assertIn("branch-$RESEARCH_AGENT_BRANCH_ID.md", scientist)
        self.assertIn("no required report template", scientist.lower())
        self.assertIn("has no required schema, section list, fields, or style", contract)
        self.assertIn("`research_record/reports/*` | Scientist", contract)
        self.assertNotIn("RESEARCH_AGENT_REPORT", scientist)
        self.assertNotIn("RESEARCH_AGENT_REPORT", contract)

    def test_research_record_is_a_simple_experiment_ledger(self) -> None:
        schema = (RECORD / "schema" / "RESEARCH_RECORD.yaml").read_text(encoding="utf-8")
        example = (RECORD / "example" / "RESEARCH_RECORD.md").read_text(encoding="utf-8")

        self.assertIn("experiments:", schema)
        self.assertIn("record: >", schema)
        self.assertIn("primary_metric:", schema)
        self.assertIn("official_score:", schema)
        self.assertIn("evidence:", schema)
        self.assertNotIn("bottlenecks:", schema)
        self.assertNotIn("formation:", schema)
        self.assertNotIn("competing_explanations:", schema)

        self.assertIn("Hypothesis-driven experiment", example)
        self.assertIn("Exploratory experiment", example)

    def test_brief_is_default_handoff_and_deep_history_is_on_demand(self) -> None:
        brief = (RECORD / "RESEARCH_BRIEF.md").read_text(encoding="utf-8")
        scientist = (RECORD / "SKILL.md").read_text(encoding="utf-8")
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Runtime-launched Scientists do not", brief)
        self.assertIn("deeper provenance", brief)
        self.assertIn("when the available memory or evidence is insufficient", scientist)
        self.assertIn("lossy", root_skill)
        self.assertIn("raw evidence", root_skill)

    def test_mutable_memory_is_not_part_of_state_git_history(self) -> None:
        ignore_lines = {
            line.strip()
            for line in (ROOT / "assets" / "project-template" / ".gitignore").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        for path in (
            "research_record/RESEARCH_RECORD.yaml",
            "research_record/RESEARCH_BRIEF.md",
            "research_record/EXPLORE.md",
            "research_record/OPTIMIZE.md",
            "research_record/ENGINEERING.md",
            "research_record/KNOWLEDGE.md",
            "research_record/RESEARCH_INTUITION.md",
            "research_record/DO_BETTER.md",
            "research_record/reports/",
        ):
            self.assertIn(path, ignore_lines)
        self.assertNotIn("research_record/STATE.yaml", ignore_lines)

    def test_coordination_brief_still_has_no_scientific_objective(self) -> None:
        brief_schema = json.loads(
            (RECORD / "schema" / "CYCLE_BRIEF.schema.json").read_text(encoding="utf-8")
        )
        self.assertIn("concerns", brief_schema["properties"])
        self.assertNotIn("objective", brief_schema["properties"])

    def test_entry_prompts_inject_runtime_context(self) -> None:
        launcher = (ROOT / "src" / "research_agent" / "launcher.py").read_text(encoding="utf-8")
        prompt_context = (ROOT / "src" / "research_agent" / "prompt_context.py").read_text(encoding="utf-8")
        self.assertIn("target files required for META startup", launcher)
        self.assertIn("target files required for Scientist startup", launcher)
        self.assertIn("meta_startup_context", launcher)
        self.assertIn("scientist_startup_context", launcher)
        self.assertIn("RESEARCH_AGENT_INJECTED", prompt_context)
        self.assertIn("NO_SKILL_FILE_READ", prompt_context)
        self.assertNotIn("injected_file('META_SKILL'", launcher)
        self.assertNotIn("injected_file('SCIENTIST_SKILL'", launcher)
        self.assertNotIn("One Scientist iteration is a bottleneck boundary", launcher)
        self.assertNotIn("cheapest experiment or diagnostic", launcher)


if __name__ == "__main__":
    unittest.main()
