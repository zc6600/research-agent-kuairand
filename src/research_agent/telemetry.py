from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any

COUNTERS = ("input", "output", "reasoning", "cache_read", "cache_write", "total")


def _under(path: str, roots: tuple[Path, ...]) -> bool:
    if not path:
        return False
    try:
        candidate = Path(path).expanduser().resolve()
    except OSError:
        return False
    return any(candidate == root or root in candidate.parents for root in roots)


def _unavailable(runner: str, reason: str) -> dict[str, Any]:
    return {
        "runner": runner,
        "accounting_status": "unavailable",
        "scope": "runner_sessions",
        "reason": reason,
    }


def _measured(runner: str, sessions: set[str], counters: dict[str, int], **extra: Any) -> dict[str, Any]:
    report: dict[str, Any] = {
        "runner": runner,
        "accounting_status": "measured",
        "scope": "runner_sessions",
        "sessions": len(sessions),
        **{name: int(counters.get(name, 0)) for name in COUNTERS},
    }
    report.update(extra)
    return report


def _json_objects(path: Path) -> Iterable[dict[str, Any]]:
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    yield value
    except OSError:
        return


def _codex_usage(path: Path) -> dict[str, int] | None:
    latest: dict[str, Any] | None = None
    for value in _json_objects(path):
        payload = value.get("payload")
        if not isinstance(payload, dict):
            continue
        info = payload.get("info")
        if isinstance(info, dict) and isinstance(info.get("total_token_usage"), dict):
            latest = info["total_token_usage"]
            continue
        usage = payload.get("usage")
        if isinstance(usage, dict) and "input_tokens" in usage:
            latest = usage
    if latest is None:
        return None
    return {
        "input": int(latest.get("input_tokens", 0) or 0),
        "output": int(latest.get("output_tokens", 0) or 0),
        "reasoning": int(latest.get("reasoning_output_tokens", 0) or 0),
        "cache_read": int(latest.get("cached_input_tokens", 0) or 0),
        "cache_write": 0,
        "total": int(latest.get("total_tokens", 0) or 0),
    }


def collect_codex(roots: tuple[Path, ...], session: str | None) -> dict[str, Any]:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    candidates = sorted(codex_home.glob("state_*.sqlite"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        return _unavailable("codex", "Codex state database was not found")
    database = candidates[0]
    try:
        connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
        rows = connection.execute("select id, tokens_used, rollout_path, cwd from threads").fetchall()
    except sqlite3.Error as exc:
        return _unavailable("codex", f"Codex state database could not be read: {exc}")
    finally:
        if "connection" in locals():
            connection.close()

    sessions: set[str] = set()
    counters = {name: 0 for name in COUNTERS}
    breakdown = "complete"
    for thread_id, tokens_used, rollout_path, cwd in rows:
        if session:
            matches = thread_id == session
        else:
            matches = _under(str(cwd or ""), roots)
        if not matches:
            continue
        sessions.add(str(thread_id))
        usage = _codex_usage(Path(rollout_path)) if rollout_path else None
        if usage is None:
            usage = {name: 0 for name in COUNTERS}
            usage["total"] = int(tokens_used or 0)
            breakdown = "total_only"
        for name in COUNTERS:
            counters[name] += usage[name]
    if not sessions:
        return _unavailable("codex", "No matching Codex sessions were found")
    return _measured("codex", sessions, counters, breakdown_status=breakdown)


def collect_claude(roots: tuple[Path, ...], session: str | None) -> dict[str, Any]:
    projects = Path.home() / ".claude" / "projects"
    if not projects.is_dir():
        return _unavailable("claude", "Claude project telemetry directory was not found")
    sessions: set[str] = set()
    counters = {name: 0 for name in COUNTERS}
    seen_messages: set[str] = set()
    for path in projects.glob("**/*.jsonl"):
        for value in _json_objects(path):
            if value.get("type") != "assistant":
                continue
            session_id = str(value.get("sessionId") or path.stem)
            if session:
                if session_id != session:
                    continue
            elif not _under(str(value.get("cwd") or ""), roots):
                continue
            message_id = str(value.get("uuid") or "")
            if message_id and message_id in seen_messages:
                continue
            if message_id:
                seen_messages.add(message_id)
            message = value.get("message")
            usage = message.get("usage") if isinstance(message, dict) else None
            if not isinstance(usage, dict):
                continue
            sessions.add(session_id)
            counters["input"] += int(usage.get("input_tokens", 0) or 0)
            counters["output"] += int(usage.get("output_tokens", 0) or 0)
            counters["cache_read"] += int(usage.get("cache_read_input_tokens", 0) or 0)
            counters["cache_write"] += int(usage.get("cache_creation_input_tokens", 0) or 0)
    if not sessions:
        return _unavailable("claude", "No matching Claude sessions were found")
    counters["total"] = counters["input"] + counters["output"] + counters["cache_read"] + counters["cache_write"]
    return _measured("claude", sessions, counters)


def collect_opencode(roots: tuple[Path, ...], session: str | None) -> dict[str, Any]:
    database = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
    if not database.is_file():
        return _unavailable("opencode", "OpenCode state database was not found")
    try:
        connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
        rows = connection.execute(
            "select id, directory, tokens_input, tokens_output, tokens_reasoning, "
            "tokens_cache_read, tokens_cache_write from session"
        ).fetchall()
    except sqlite3.Error as exc:
        return _unavailable("opencode", f"OpenCode state database could not be read: {exc}")
    finally:
        if "connection" in locals():
            connection.close()
    sessions: set[str] = set()
    counters = {name: 0 for name in COUNTERS}
    for row in rows:
        session_id, directory, input_tokens, output_tokens, reasoning, cache_read, cache_write = row
        if session:
            if session_id != session:
                continue
        elif not _under(str(directory or ""), roots):
            continue
        sessions.add(str(session_id))
        counters["input"] += int(input_tokens or 0)
        counters["output"] += int(output_tokens or 0)
        counters["reasoning"] += int(reasoning or 0)
        counters["cache_read"] += int(cache_read or 0)
        counters["cache_write"] += int(cache_write or 0)
    if not sessions:
        return _unavailable("opencode", "No matching OpenCode sessions were found")
    counters["total"] = sum(counters[name] for name in COUNTERS if name != "total")
    return _measured("opencode", sessions, counters)


def collect_runner(runner: str, roots: Iterable[Path], session: str | None = None) -> dict[str, Any]:
    normalized_roots = tuple(path.expanduser().resolve() for path in roots)
    if runner == "codex":
        return collect_codex(normalized_roots, session)
    if runner == "claude":
        return collect_claude(normalized_roots, session)
    if runner == "opencode":
        return collect_opencode(normalized_roots, session)
    if runner == "agy":
        return _unavailable("agy", "agy does not expose a verified local token telemetry backend")
    return _unavailable(runner, f"Unsupported telemetry runner: {runner}")


def _unavailable_delta(after: dict[str, Any], before: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "runner": str(after.get("runner") or before.get("runner") or "unknown"),
        "accounting_status": "unavailable",
        "scope": "run_delta",
        "baseline_status": str(before.get("accounting_status") or "unavailable"),
        "reason": reason,
    }


def subtract_reports(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    if after.get("accounting_status") != "measured":
        result = dict(after)
        result["scope"] = "run_delta"
        result["baseline_status"] = str(before.get("accounting_status") or "unavailable")
        return result
    if before.get("accounting_status") != "measured" or before.get("runner") != after.get("runner"):
        return _unavailable_delta(
            after,
            before,
            "Run usage delta requires comparable measured before/after telemetry from the same runner",
        )

    total_only = before.get("breakdown_status") == "total_only" or after.get("breakdown_status") == "total_only"
    reliable_counters = ("total",) if total_only else COUNTERS
    result = {
        key: value
        for key, value in after.items()
        if key not in COUNTERS and key != "sessions"
    }
    result["scope"] = "run_delta"
    result["breakdown_status"] = "total_only" if total_only else str(after.get("breakdown_status") or "complete")
    for name in reliable_counters:
        after_value = int(after.get(name, 0))
        before_value = int(before.get(name, 0))
        if after_value < before_value:
            return _unavailable_delta(
                after,
                before,
                f"Runner telemetry counter moved backwards during the run: {name}",
            )
        result[name] = after_value - before_value
    result["baseline_status"] = "measured"
    return result
