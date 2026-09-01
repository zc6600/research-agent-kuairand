from pathlib import Path

from research_agent.runners.base import EFFORT_LEVELS, Invocation, RunnerAdapter


class CodexAdapter(RunnerAdapter):
    name = "codex"

    @staticmethod
    def _permissions(allow_edits: bool, sandbox_mode: str | None = None) -> list[str]:
        if not allow_edits:
            return ["--sandbox", "read-only"]
        if sandbox_mode == "danger-full-access":
            # META may need to start a nested Codex app-server through
            # launch-inner. The explicit approval policy keeps this mode
            # independent of the operator's local Codex configuration.
            return [
                "--sandbox",
                "danger-full-access",
                "--config",
                'approval_policy="never"',
            ]
        return ["--approve-for-me"]

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
        command = ["codex", "exec"]
        if model is not None:
            command.extend(["--model", model])
        if effort is not None:
            if effort not in EFFORT_LEVELS:
                raise ValueError(f"unsupported effort {effort!r}")
            command.extend(["--config", f'model_reasoning_effort="{effort}"'])
        command.extend(["-C", str(target)])
        command.extend(self._permissions(allow_edits, sandbox_mode))
        command.append("-")
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
        """Build a real interactive Codex Goal-mode invocation.

        Goal mode is a slash command handled by the interactive CLI, so it
        cannot be represented faithfully by ``codex exec``.  The launcher
        uses ``input_text`` to submit this command through a PTY after the
        interactive session is ready.
        """

        objective = goal.strip()
        if not objective:
            raise ValueError("Codex Goal objective must not be empty")

        command = ["codex", "--no-alt-screen"]
        if model is not None:
            command.extend(["--model", model])
        if effort is not None:
            if effort not in EFFORT_LEVELS:
                raise ValueError(f"unsupported effort {effort!r}")
            command.extend(["--config", f'model_reasoning_effort="{effort}"'])
        command.extend(["-C", str(target)])
        command.extend(self._permissions(allow_edits, sandbox_mode))
        return Invocation(
            tuple(command),
            target,
            interactive=True,
            input_text=f"/goal {objective}\r",
        )
