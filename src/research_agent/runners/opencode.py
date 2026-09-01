from pathlib import Path

from research_agent.runners.base import Invocation, RunnerAdapter


class OpenCodeAdapter(RunnerAdapter):
    name = "opencode"

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
        command = ["opencode", "run", "--dir", str(target)]
        if model is not None:
            command.extend(["--model", model])
        if allow_edits:
            command.append("--auto")
        return Invocation(tuple(command), target, stdin_text=prompt)
