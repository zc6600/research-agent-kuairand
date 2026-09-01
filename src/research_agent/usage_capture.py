from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_agent.runtime import utc_now, write_json
from research_agent.telemetry import COUNTERS, collect_runner, subtract_reports

ROLE_ORDER = {"meta": 0, "scientist": 1, "baseline": 2}
STRUCTURED_USAGE_RUNNERS = frozenset({"agy", "gemini"})


def _integer(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _counter_sum(entries: list[dict[str, Any]], counter: str) -> int | None:
    values: list[int] = []
    for entry in entries:
        value = _integer(entry.get(counter))
        if value is not None:
            values.append(value)
    return sum(values) if values else None


def _arg_value(argv: tuple[str, ...], name: str) -> str | None:
    for index, value in enumerate(argv):
        if value == name and index + 1 < len(argv):
            return argv[index + 1]
        if value.startswith(name + "="):
            return value.split("=", 1)[1]
    return None


def _role(environment: dict[str, str]) -> str | None:
    assigned = environment.get("RESEARCH_AGENT_ROLE")
    if assigned == "SCIENTIST":
        return "scientist"
    if assigned == "BASELINE":
        return "baseline"
    if environment.get("RESEARCH_AGENT_META_SESSION") == "1":
        return "meta"
    return None


def _configured_model(role: str, argv: tuple[str, ...], environment: dict[str, str]) -> str | None:
    if role == "meta":
        return environment.get("RESEARCH_AGENT_META_MODEL") or _arg_value(argv, "--model")
    if role == "scientist":
        return (
            environment.get("RESEARCH_AGENT_SCIENTIST_MODEL")
            or environment.get("RESEARCH_AGENT_MODEL")
            or _arg_value(argv, "--model")
        )
    return _arg_value(argv, "--model")


def _active_run_dir(target: Path, environment: dict[str, str]) -> Path | None:
    explicit = environment.get("RESEARCH_AGENT_RUN_DIR")
    if explicit:
        path = Path(explicit).expanduser().resolve()
        return path if path.is_dir() else None

    root = target / "research_record" / "runtime" / "tmp"
    if not root.is_dir():
        return None
    candidates: list[tuple[float, Path]] = []
    for run_dir in root.iterdir():
        descriptor = run_dir / "run.json"
        if not descriptor.is_file():
            continue
        try:
            payload = json.loads(descriptor.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and payload.get("status") == "running":
            try:
                stamp = descriptor.stat().st_mtime
            except OSError:
                stamp = 0.0
            candidates.append((stamp, run_dir))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]


def _empty_baseline(report: dict[str, Any]) -> bool:
    if report.get("accounting_status") != "unavailable":
        return False
    reason = str(report.get("reason") or "")
    return reason.startswith("No matching ") and reason.endswith(" sessions were found")


def _delta(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    if after.get("accounting_status") == "measured" and _empty_baseline(before):
        result = dict(after)
        result["scope"] = "run_delta"
        result["baseline_status"] = "empty"
        return result
    return subtract_reports(after, before)


def _entry_from_report(
    report: dict[str, Any],
    *,
    role: str,
    runner: str,
    model: str | None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "role": role,
        "runner": runner,
        "model": model or "default",
        "accounting_status": str(report.get("accounting_status") or "unavailable"),
    }
    for key in (*COUNTERS, "breakdown_status", "reason"):
        if key in report:
            entry[key] = report[key]
    return entry


def _json_object(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        return {}
    try:
        value = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _gemini_entries(
    path: Path,
    *,
    role: str,
    configured_model: str | None,
) -> list[dict[str, Any]]:
    payload = _json_object(path)
    stats = payload.get("stats")
    models = stats.get("models") if isinstance(stats, dict) else None
    if not isinstance(models, dict) or not models:
        return []

    entries: list[dict[str, Any]] = []
    for model_name, raw in models.items():
        if not isinstance(raw, dict):
            continue
        tokens = raw.get("tokens")
        if not isinstance(tokens, dict):
            continue
        total = _integer(tokens.get("total"))
        if total is None:
            continue
        entry: dict[str, Any] = {
            "role": role,
            "runner": "gemini",
            "model": str(model_name or configured_model or "default"),
            "configured_model": configured_model,
            "accounting_status": "measured",
            "breakdown_status": "gemini_session_metrics",
            "total": total,
        }
        mapping = {
            "input": "prompt",
            "output": "candidates",
            "reasoning": "thoughts",
            "cache_read": "cached",
        }
        for destination, source in mapping.items():
            value = _integer(tokens.get(source))
            if value is not None:
                entry[destination] = value
        entry["cache_write"] = 0
        entries.append(entry)
    return entries


def _agy_entries(
    path: Path,
    *,
    role: str,
    configured_model: str | None,
) -> list[dict[str, Any]]:
    payload = _json_object(path)
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        return []
    total = _integer(usage.get("total_tokens"))
    if total is None:
        return []

    entry: dict[str, Any] = {
        "role": role,
        "runner": "agy",
        "model": configured_model or "default",
        "accounting_status": "measured",
        "breakdown_status": "agy_session_metrics",
        "total": total,
    }
    mapping = {
        "input": "input_tokens",
        "output": "output_tokens",
        "reasoning": "thinking_tokens",
        "cache_read": "cache_read_tokens",
    }
    for destination, source in mapping.items():
        value = _integer(usage.get(source))
        if value is not None:
            entry[destination] = value
    return [entry]


def _aggregate(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for entry in entries:
        key = (
            str(entry.get("role") or "unknown"),
            str(entry.get("runner") or "unknown"),
            str(entry.get("model") or "default"),
        )
        groups.setdefault(key, []).append(entry)

    merged: list[dict[str, Any]] = []
    for (role, runner, model), items in groups.items():
        measured = [item for item in items if item.get("accounting_status") == "measured"]
        if len(measured) == len(items):
            status = "measured"
        elif measured:
            status = "partial"
        else:
            status = "unavailable"
        result: dict[str, Any] = {
            "role": role,
            "runner": runner,
            "model": model,
            "accounting_status": status,
        }
        configured = next((item.get("configured_model") for item in items if item.get("configured_model")), None)
        if configured:
            result["configured_model"] = configured
        for counter in COUNTERS:
            value = _counter_sum(measured, counter)
            if value is not None:
                result[counter] = value
        if not measured:
            reasons = [str(item.get("reason")) for item in items if item.get("reason")]
            if reasons:
                result["reason"] = reasons[0]
        merged.append(result)
    merged.sort(
        key=lambda item: (
            ROLE_ORDER.get(str(item.get("role")), 9),
            str(item.get("runner")),
            str(item.get("model")),
        )
    )
    return merged


def model_usage_report(entries: list[dict[str, Any]]) -> dict[str, Any]:
    models = _aggregate(entries)
    measured = [item for item in models if item.get("accounting_status") in {"measured", "partial"}]
    if models and all(item.get("accounting_status") == "measured" for item in models):
        status = "measured"
    elif measured:
        status = "partial"
    else:
        status = "unavailable"
    total = _counter_sum(measured, "total") or 0
    return {
        "schema_version": 2,
        "scope": "run_models",
        "accounting_status": status,
        "total": total,
        "models": models,
        "observed_at": utc_now(),
    }


def _scientist_entries(run_dir: Path) -> list[dict[str, Any]]:
    directory = run_dir / "scientist"
    if not directory.is_dir():
        return []
    entries: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.usage.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        models = payload.get("models") if isinstance(payload, dict) else None
        if isinstance(models, list):
            entries.extend(item for item in models if isinstance(item, dict))
    return entries


def _subtract_scientists(total: dict[str, Any], scientists: list[dict[str, Any]]) -> dict[str, Any]:
    if total.get("accounting_status") != "measured":
        return total
    if any(item.get("accounting_status") != "measured" for item in scientists):
        return {
            **{key: total[key] for key in ("role", "runner", "model") if key in total},
            "accounting_status": "unavailable",
            "reason": "META usage cannot be isolated because Scientist usage on the same runner is unavailable",
        }

    result = dict(total)
    for counter in COUNTERS:
        value = _integer(result.get(counter))
        if value is None:
            continue
        used = _counter_sum(scientists, counter) or 0
        if used > value:
            return {
                **{key: total[key] for key in ("role", "runner", "model") if key in total},
                "accounting_status": "unavailable",
                "reason": f"META/Scientist token accounting is inconsistent for {counter}",
            }
        result[counter] = value - used
    return result


@dataclass
class UsageCapture:
    target: Path
    runner: str
    role: str
    model: str | None
    run_dir: Path
    before: dict[str, Any]
    cycle: str | None = None

    @classmethod
    def begin(
        cls,
        argv: tuple[str, ...],
        target: Path,
        environment: dict[str, str],
    ) -> UsageCapture | None:
        role = _role(environment)
        run_dir = _active_run_dir(target, environment)
        if role is None or run_dir is None:
            return None
        runner = argv[0]
        model = _configured_model(role, argv, environment)
        before = collect_runner(runner, (target,))
        return cls(
            target.resolve(),
            runner,
            role,
            model,
            run_dir,
            before,
            environment.get("RESEARCH_AGENT_CYCLE"),
        )

    def prepare_output(
        self,
        output_path: Path | None,
        stream_output: bool,
    ) -> tuple[Path | None, bool]:
        if self.runner not in STRUCTURED_USAGE_RUNNERS or output_path is not None:
            return output_path, stream_output
        if self.role == "scientist":
            path = self.run_dir / "scientist" / f"cycle-{self.cycle or 'unknown'}-{os.getpid()}.log"
        elif self.role == "baseline":
            path = self.run_dir / "baseline" / "baseline.log"
        else:
            path = self.run_dir / "meta" / "meta.log"
        return path, False

    def finish(self, output_path: Path | None) -> None:
        after = collect_runner(self.runner, (self.target,))
        entries: list[dict[str, Any]] = []
        if output_path is not None:
            if self.runner == "gemini":
                entries = _gemini_entries(output_path, role=self.role, configured_model=self.model)
            elif self.runner == "agy":
                entries = _agy_entries(output_path, role=self.role, configured_model=self.model)
        if not entries:
            entries = [
                _entry_from_report(
                    _delta(after, self.before),
                    role=self.role,
                    runner=self.runner,
                    model=self.model,
                )
            ]

        if self.role == "scientist":
            directory = self.run_dir / "scientist"
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / f"cycle-{self.cycle or 'unknown'}-{os.getpid()}.usage.json"
            write_json(path, model_usage_report(entries))
            return

        if self.role == "baseline":
            write_json(self.run_dir / "baseline" / "model-usage.json", model_usage_report(entries))
            return

        scientists = _scientist_entries(self.run_dir)
        if self.runner not in STRUCTURED_USAGE_RUNNERS:
            same_runner = [item for item in scientists if item.get("runner") == self.runner]
            entries = [_subtract_scientists(entry, same_runner) for entry in entries]
        write_json(self.run_dir / "meta" / "model-usage.json", model_usage_report(entries + scientists))
