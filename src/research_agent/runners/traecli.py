from pathlib import Path

from research_agent.runners.base import Invocation, RunnerAdapter


class TraeCliAdapter(RunnerAdapter):
    """Adapter for ByteDance's TraeCode CLI (``traecli``)."""

    name = "traecli"

    @staticmethod
    def _sandbox_mode(allow_edits: bool, sandbox_mode: str | None) -> str:
        if sandbox_mode is not None:
            if sandbox_mode not in {"read-only", "workspace-write", "danger-full-access"}:
                raise ValueError(f"unsupported Trae sandbox mode {sandbox_mode!r}")
            return sandbox_mode
        return "workspace-write" if allow_edits else "read-only"

    @staticmethod
    def _permission_mode(allow_edits: bool) -> str:
        return "bypass_permissions" if allow_edits else "plan"

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
        # TraeCode CLI's ``exec`` command accepts ``-`` as a prompt-from-stdin
        # marker. Keep the injected runtime context out of argv and process
        # listings, consistent with the other non-interactive adapters.
        del effort
        command = [
            "traecli",
            "exec",
            "--sandbox",
            self._sandbox_mode(allow_edits, sandbox_mode),
            "--permission-mode",
            self._permission_mode(allow_edits),
        ]
        if model is not None:
            command.extend(["--model", model])
        command.append("-")
        return Invocation(tuple(command), target, stdin_text=prompt)
