from pathlib import Path

from research_agent.runners.base import Invocation, RunnerAdapter


class ClaudeAdapter(RunnerAdapter):
    name = "claude"

    @staticmethod
    def _permission(allow_edits: bool) -> str:
        return "acceptEdits" if allow_edits else "plan"

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
        command = ["claude"]
        if model is not None:
            command.extend(["--model", model])
        command.extend(["--print", "--permission-mode", self._permission(allow_edits)])
        return Invocation(tuple(command), target, stdin_text=prompt)

    def invoke_goal(
        self,
        *,
        target: Path,
        goal: str,
        allow_edits: bool,
        model: str | None,
        sandbox_mode: str | None = None,
        effort: str | None = None,
    ) -> Invocation:
        objective = goal.strip()
        if not objective:
            raise ValueError("Claude Goal objective must not be empty")
        return self.invoke(
            target=target,
            prompt=f"/goal {objective}",
            allow_edits=allow_edits,
            model=model,
            sandbox_mode=sandbox_mode,
            effort=effort,
        )
