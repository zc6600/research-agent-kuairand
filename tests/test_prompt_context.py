from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from research_agent.bootstrap import BootstrapError
from research_agent.prompt_context import injected_file


class PromptContextTests(unittest.TestCase):
    def test_injected_file_contains_source_and_exact_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "skill.md"
            content = "# Instructions\nkeep this exact text\n"
            path.write_text(content, encoding="utf-8")

            result = injected_file("test skill", path)

        self.assertIn("<<< RESEARCH_AGENT_INJECTED TEST_SKILL >>>", result)
        self.assertIn(f"Source: {path.resolve()}", result)
        self.assertIn(content.rstrip(), result)
        self.assertIn("<<< END RESEARCH_AGENT_INJECTED TEST_SKILL >>>", result)

    def test_injected_file_fails_for_missing_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(BootstrapError, "cannot inject missing"):
                injected_file("missing", Path(temporary) / "missing.md")

    def test_injected_file_fails_for_empty_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "empty.md"
            path.write_text("\n", encoding="utf-8")
            with self.assertRaisesRegex(BootstrapError, "cannot inject empty"):
                injected_file("empty source", path)


if __name__ == "__main__":
    unittest.main()
