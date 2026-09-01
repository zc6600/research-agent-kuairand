from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

EFFORT_LEVELS = ("low", "medium", "high", "max")


@dataclass(frozen=True)
class Invocation:
    argv: tuple[str, ...]
    cwd: Path
    interactive: bool = False
    input_text: str | None = None
    stdin_text: str | None = None



class RunnerAdapter:
    name: str

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
        raise NotImplementedError
