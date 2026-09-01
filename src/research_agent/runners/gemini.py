from pathlib import Path

from research_agent.runners.base import Invocation, RunnerAdapter


class GeminiAdapter(RunnerAdapter):
    name = "gemini"

    @staticmethod
    def _approval_mode(allow_edits: bool) -> str:
        return "yolo" if allow_edits else "plan"

    def invoke(
        self,
        *,
        target: Path,
        prompt: str,
        allow_edits: bool,
        model: str | None,
        sandbox_mode: str | None = None,
        effort: str | None = None,
    ) -> Invocation:
        del sandbox_mode, effort
        command = [
            "gemini",
            "--skip-trust",
            f"--approval-mode={self._approval_mode(allow_edits)}",
            "--output-format",
            "json",
        ]
        if model is not None:
            command.extend(["--model", model])
        return Invocation(tuple(command), target, stdin_text=prompt)
