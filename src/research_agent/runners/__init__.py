from research_agent.runners.agy import AgyAdapter
from research_agent.runners.base import RunnerAdapter
from research_agent.runners.claude import ClaudeAdapter
from research_agent.runners.codex import CodexAdapter
from research_agent.runners.gemini import GeminiAdapter
from research_agent.runners.opencode import OpenCodeAdapter

_ADAPTERS: dict[str, RunnerAdapter] = {
    "codex": CodexAdapter(),
    "claude": ClaudeAdapter(),
    "gemini": GeminiAdapter(),
    "opencode": OpenCodeAdapter(),
    "agy": AgyAdapter(),
}


def get_adapter(name: str) -> RunnerAdapter:
    try:
        return _ADAPTERS[name]
    except KeyError as exc:
        supported = ", ".join(sorted(_ADAPTERS))
        raise ValueError(f"unsupported CLI {name!r}; choose one of: {supported}") from exc


def supported_runners() -> tuple[str, ...]:
    return tuple(sorted(_ADAPTERS))
