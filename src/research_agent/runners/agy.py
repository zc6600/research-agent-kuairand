import os
from pathlib import Path

from research_agent.runners.base import EFFORT_LEVELS, Invocation, RunnerAdapter


class AgyAdapter(RunnerAdapter):
    name = "agy"
    default_effort = "medium"

    @staticmethod
    def _mode(allow_edits: bool) -> str:
        return "accept-edits" if allow_edits else "plan"

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
        # AGY otherwise falls back to its global CLI scratch project when the
        # current directory has no registered AGY project.  Explicitly create
        # the session project from the invocation cwd so edits and artifacts
        # stay inside the research target.
        command = ["agy", "--new-project", "--mode", self._mode(allow_edits)]
        if model is not None:
            command.extend(["--model", model])
            # AGY's Gemini Flash model family requires an explicit reasoning
            # effort when the model is selected by its base name (for example,
            # ``gemini-3.7-flash``). Keep the runner contract usable with a
            # plain model override by selecting the balanced default.
        selected_effort = effort
        if selected_effort is None and model is not None:
            selected_effort = self.default_effort
        if selected_effort is not None:
            if selected_effort not in EFFORT_LEVELS:
                raise ValueError(f"unsupported effort {selected_effort!r}")
            # AGY currently exposes low/medium/high; max means its highest
            # available level rather than silently falling back to medium.
            command.extend(["--effort", "high" if selected_effort == "max" else selected_effort])
        if allow_edits:
            command.append("--dangerously-skip-permissions")
        log_file = os.environ.get("RESEARCH_AGENT_AGY_LOG_FILE")
        if log_file:
            command.extend(["--log-file", log_file])
        # AGY's print-mode flag is a string option rather than a bare switch:
        # ``--print`` must be followed by the prompt. Unlike the other
        # non-interactive adapters, AGY 1.1.x does not consume this prompt from
        # stdin in print mode.
        command.extend(
            [
                "--print-timeout",
                os.environ.get("RESEARCH_AGENT_AGY_PRINT_TIMEOUT", "24h"),
                "--input-format",
                "text",
                "--output-format",
                "json",
                "--print",
                prompt,
            ]
        )
        return Invocation(tuple(command), target)

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
            raise ValueError("AGY Goal objective must not be empty")
        return self.invoke(
            target=target,
            prompt=f"/goal {objective}",
            allow_edits=allow_edits,
            model=model,
            sandbox_mode=sandbox_mode,
            effort=effort,
        )
