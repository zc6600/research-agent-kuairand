from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Protocol, cast

from research_agent.bootstrap import BootstrapError, ensure_target_git_root, prepare_target
from research_agent.launcher import run_invocation
from research_agent.runners import get_adapter, supported_runners
from research_agent.runners.base import EFFORT_LEVELS, Invocation
from research_agent.runtime import utc_now, write_json

BASELINE_PROMPT = """You are the blank-control optimization agent for an experiment.

Improve this task's measured performance directly in one autonomous session. Read task.md and PERSONAL.md when present, inspect the current implementation and evaluator, establish the current behavior or score when practical, make changes, run evaluations, and keep the strongest verified implementation you can produce.

This is a long-running single-agent control, not a one-shot patch. Continue through multiple useful inspect/measure/change/verify cycles when the task and budget support them. Do not stop after the first implementation, first passing smoke test, or first plausible improvement. Complete only after you have either reached a meaningful stopping condition or exhausted the available work, and leave a concise final summary of the experiments, strongest verified result, tests, and any blocker.

This is intentionally a control condition. Do not use research_record/** as guidance, do not follow the Research Agent research method, do not adopt META or Scientist roles, do not read Research Intuition or DO_BETTER, do not use a META brief, and do not invoke research-agent. Work directly from the task, environment, code, data, and evaluator. You do not need to maintain a research diary or research-agent State history.

Prefer measured improvements over speculative rewrites. You may investigate failures and discard unsuccessful attempts. Before exiting, leave the target project in the best verified state you found.
"""


class _GoalRunnerAdapter(Protocol):
    def invoke_goal(
        self,
        *,
        target: Path,
        goal: str,
        allow_edits: bool,
        model: str | None,
        sandbox_mode: str | None = None,
        effort: str | None = None,
    ) -> Invocation: ...


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-agent baseline",
        description="Run one blank-control optimizer without META/Scientist research machinery",
    )
    parser.add_argument("--target", type=Path, required=True, help="Existing Git project")
    parser.add_argument("--cli", "--runner", dest="cli", choices=supported_runners(), required=True)
    parser.add_argument("--model", help="Optional runner model override")
    parser.add_argument(
        "--effort",
        choices=EFFORT_LEVELS,
        help="Reasoning effort override for runners that support it",
    )
    parser.add_argument("--allow-edits", action="store_true")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        help="Optional hard wall-time limit for the delegated runner",
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument("-v", "--verbose", dest="output_mode", action="store_const", const="verbose")
    output.add_argument("-q", "--quiet", dest="output_mode", action="store_const", const="quiet")
    parser.set_defaults(output_mode="normal")
    return parser



def _prepare_target(path: Path) -> Path:
    target, _ = prepare_target(target=path, new_target=None)
    return ensure_target_git_root(target, create_if_missing=False)


def _create_run_directory(target: Path) -> tuple[str, Path]:
    run_id = uuid.uuid4().hex
    run_dir = target / ".git" / "research-agent-baseline" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_id, run_dir


def _usage_summary(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    models = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(models, list):
        return None
    labels: list[str] = []
    for item in models:
        if not isinstance(item, dict):
            continue
        model = str(item.get("model") or item.get("runner") or "model")
        total = item.get("total")
        labels.append(f"{model}: {total}" if isinstance(total, int) else f"{model}: unavailable")
    return " · ".join(labels) or None


def baseline_main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.allow_edits:
        raise SystemExit("error: baseline requires explicit --allow-edits")
    if args.timeout_seconds is not None and args.timeout_seconds <= 0:
        raise SystemExit("error: --timeout-seconds must be positive")

    try:
        target = _prepare_target(args.target)
    except BootstrapError as exc:
        raise SystemExit(f"error: {exc}") from exc

    run_id, run_dir = _create_run_directory(target)
    session_dir = run_dir / "baseline"
    session_dir.mkdir(parents=True, exist_ok=False)
    log_path = session_dir / "baseline.log"
    result_path = session_dir / "result.json"
    usage_path = session_dir / "model-usage.json"
    adapter = get_adapter(args.cli)
    goal_adapter = cast(_GoalRunnerAdapter, adapter)
    supports_goal = hasattr(goal_adapter, "invoke_goal")
    mode = "goal" if supports_goal else "single-turn"
    metadata = {
        "schema_version": 1,
        "run_id": run_id,
        "kind": "baseline",
        "control": "blank",
        "mode": mode,
        "cli": args.cli,
        "model": args.model,
        "target": str(target),
        "started_at": utc_now(),
        "status": "running",
    }
    write_json(run_dir / "run.json", metadata)

    if args.output_mode != "quiet":
        print("Research Agent · Blank Control")
        print(f"  Project   {target.name}")
        print(f"  Runner    {args.cli}")
        if args.model:
            print(f"  Model     {args.model}")
        print(f"  Mode      {mode}")
        print(f"  Run       {run_id[:8]}")

    if supports_goal:
        invocation = goal_adapter.invoke_goal(
            target=target,
            goal=BASELINE_PROMPT,
            allow_edits=True,
            model=args.model,
            effort=args.effort,
        )
    else:
        invocation = adapter.invoke(
            target=target,
            prompt=BASELINE_PROMPT,
            allow_edits=True,
            model=args.model,
            effort=args.effort,
        )
    environment = {
        "RESEARCH_AGENT_ROLE": "BASELINE",
        "RESEARCH_AGENT_TARGET": str(target),
        "RESEARCH_AGENT_RUN_DIR": str(run_dir),
    }

    try:
        return_code = run_invocation(
            invocation,
            environment=environment,
            output_path=log_path,
            stream_output=args.output_mode == "verbose",
            timeout_seconds=args.timeout_seconds,
        )
    except KeyboardInterrupt:
        return_code = 130
    except RuntimeError as exc:
        return_code = 127
        log_path.write_text(f"error: {exc}\n", encoding="utf-8")

    terminal_status = "completed" if return_code == 0 else "interrupted" if return_code == 130 else "failed"
    result = {
        "status": terminal_status,
        "summary": f"Blank-control {mode} runner completed direct optimization."
        if return_code == 0
        else f"Blank-control {mode} runner did not complete successfully.",
        "next_action": "Evaluate the resulting implementation with the same benchmark used for the Research Agent condition.",
    }
    write_json(result_path, result)
    metadata.update(
        {
            "status": "closed",
            "terminal_status": terminal_status,
            "exit_code": return_code,
            "ended_at": utc_now(),
        }
    )
    write_json(run_dir / "run.json", metadata)

    usage = _usage_summary(usage_path)
    if args.output_mode == "quiet":
        print(
            json.dumps(
                {
                    "status": terminal_status,
                    "run_id": run_id,
                    "log": str(log_path),
                    "usage": str(usage_path),
                },
                ensure_ascii=False,
            )
        )
    else:
        marker = "✓" if return_code == 0 else "!"
        print(f"{marker} Baseline · {terminal_status}")
        if usage:
            print(f"  Tokens    {usage}")
        print(f"  Log       {log_path}")
        print(f"  Usage     {usage_path}")
    return return_code
