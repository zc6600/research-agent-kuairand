from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from research_agent.bootstrap import (
    BootstrapError,
    copy_project_inputs,
    ensure_target_git_root,
    initialize_project,
    prepare_target,
    require_supported_record,
)
from research_agent.brief import read_cycle_brief
from research_agent.cycle import CycleResult, next_cycle_id, read_cycle_result, synthetic_result
from research_agent.launcher import build_inner_invocation, build_meta_invocation, run_invocation
from research_agent.parallel import promote_parallel_branch, run_parallel
from research_agent.runners import supported_runners
from research_agent.runners.base import EFFORT_LEVELS
from research_agent.runtime import create_run_directory, utc_now, write_json
from research_agent.usage import collect, run_delta


def skill_root() -> Path:
    source_root = Path(__file__).resolve().parents[2]
    if (source_root / "SKILL.md").is_file():
        return source_root
    installed_bundle = Path(__file__).resolve().parent / "bundle"
    if (installed_bundle / "SKILL.md").is_file():
        return installed_bundle
    raise BootstrapError("research-agent release bundle is missing SKILL.md")


def _git(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(target), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _commit_selected(target: Path, paths: tuple[str, ...], *, message: str) -> None:
    existing = tuple(path for path in paths if (target / path).exists())
    if not existing:
        return
    status = _git(target, "status", "--porcelain", "--", *existing)
    if status.returncode != 0:
        raise BootstrapError(status.stderr.strip() or "cannot inspect Git status")
    if not status.stdout.strip():
        return
    added = _git(target, "add", "--", *existing)
    if added.returncode != 0:
        raise BootstrapError(added.stderr.strip() or "cannot stage research-agent files")
    has_head = _git(target, "rev-parse", "--verify", "HEAD").returncode == 0
    if has_head:
        committed = _git(target, "commit", "--only", "-m", message, "--", *existing)
    else:
        committed = _git(target, "commit", "-m", message)
    if committed.returncode != 0:
        raise BootstrapError(committed.stderr.strip() or "cannot create research-agent Git checkpoint")


def add_target_arguments(parser: argparse.ArgumentParser, *, allow_new: bool) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--target", type=Path, help="Existing target project")
    if allow_new:
        group.add_argument("--new", dest="new_target", type=Path, help="Create one new target directory")


def add_init_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--target", type=Path, help="Existing target project with task.md and PERSONAL.md")
    group.add_argument("--new", dest="new_target", type=Path, help="Create one new target directory")
    parser.add_argument("--task", type=Path, help="Task input to copy into a new target")
    parser.add_argument("--personal", type=Path, help="Environment facts to copy into a new target")


def add_cycle_arguments(parser: argparse.ArgumentParser) -> None:
    add_target_arguments(parser, allow_new=False)
    runners = supported_runners()
    parser.add_argument(
        "--cli",
        choices=runners,
        help="Default runner for both META and Scientist; role-specific flags may override it",
    )
    parser.add_argument("--meta-cli", choices=runners, help="Runner used by the persistent META process")
    parser.add_argument("--scientist-cli", choices=runners, help="Runner used by fresh Scientist processes")
    parser.add_argument("--model", help="Default model override for both META and Scientist")
    parser.add_argument("--meta-model", help="Model override for META only")
    parser.add_argument("--scientist-model", help="Model override for Scientist only")
    parser.add_argument(
        "--effort",
        choices=EFFORT_LEVELS,
        help="Default reasoning effort for both META and Scientist",
    )
    parser.add_argument("--meta-effort", choices=EFFORT_LEVELS, help="Reasoning effort for META only")
    parser.add_argument("--scientist-effort", choices=EFFORT_LEVELS, help="Reasoning effort for Scientist only")
    parser.add_argument("--allow-edits", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("-v", "--verbose", dest="output_mode", action="store_const", const="verbose")
    output_group.add_argument("-q", "--quiet", dest="output_mode", action="store_const", const="quiet")
    parser.set_defaults(output_mode="normal")


def add_parallel_arguments(parser: argparse.ArgumentParser) -> None:
    add_cycle_arguments(parser)
    parser.add_argument(
        "--rounds",
        type=int,
        default=1,
        help="Number of independent-Scientist/reviewer rounds to run",
    )
    parser.add_argument(
        "--branches",
        type=int,
        default=2,
        help="Number of independent Scientist replicas created per selected parent research world",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=1,
        help="Maximum number of reviewed research worlds carried into the next round",
    )
    parser.add_argument(
        "--parallelism",
        type=int,
        default=2,
        help="Maximum number of Scientist worktrees run concurrently",
    )
    parser.add_argument(
        "--synthesis",
        action="store_true",
        help="Run one optional evidence-synthesis pass after the final Parallel review",
    )
    parser.add_argument(
        "--share-inputs",
        action="store_true",
        help="Reserved; currently rejected until a portable read-only input boundary exists",
    )


def resolved_output_mode(args: argparse.Namespace) -> str:
    return str(getattr(args, "output_mode", "normal"))


def resolved_role_config(
    args: argparse.Namespace,
) -> tuple[str, str, str | None, str | None, str | None, str | None]:
    shared_cli = getattr(args, "cli", None)
    meta_cli = getattr(args, "meta_cli", None) or shared_cli
    scientist_cli = getattr(args, "scientist_cli", None) or shared_cli
    if meta_cli is None or scientist_cli is None:
        raise BootstrapError(
            "select runners with --cli, or provide both --meta-cli and --scientist-cli"
        )

    shared_model = getattr(args, "model", None)
    meta_model = getattr(args, "meta_model", None) or shared_model
    scientist_model = getattr(args, "scientist_model", None) or shared_model
    shared_effort = getattr(args, "effort", None)
    meta_effort = getattr(args, "meta_effort", None) or shared_effort
    scientist_effort = getattr(args, "scientist_effort", None) or shared_effort
    return str(meta_cli), str(scientist_cli), meta_model, scientist_model, meta_effort, scientist_effort


def tail_lines(path: Path, *, count: int = 20, width: int = 240) -> list[str]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-count:]
    return [line if len(line) <= width else f"{line[: width - 1]}…" for line in lines]


def command_init(args: argparse.Namespace) -> int:
    root = skill_root()
    if args.target is not None:
        if args.task is not None or args.personal is not None:
            raise BootstrapError("--task and --personal are only valid with --new")
        new_target = None
        task_source = personal_source = None
    else:
        new_target = args.new_target
        if args.task is None or args.personal is None:
            raise BootstrapError("--new requires both --task and --personal")
        task_source = args.task
        personal_source = args.personal
        assert task_source is not None and personal_source is not None
        for name, source in (("task.md", task_source), ("PERSONAL.md", personal_source)):
            if not source.expanduser().is_file():
                raise BootstrapError(f"required input file does not exist: {name}: {source}")

    target, _ = prepare_target(target=args.target, new_target=new_target)
    if new_target is not None:
        assert task_source is not None and personal_source is not None
        copy_project_inputs(target, task_source=task_source, personal_source=personal_source)
    ensure_target_git_root(target, create_if_missing=new_target is not None)
    result = initialize_project(target, root / "assets" / "project-template")
    _commit_selected(
        target,
        ("task.md", "PERSONAL.md", ".gitignore", "AGENTS.md", "CLAUDE.md", "research_record"),
        message="Initialize research-agent record v5",
    )
    print(json.dumps({
        "target": str(result.target),
        "research_record": "created",
        "AGENTS.md": result.agents_action,
        "CLAUDE.md": result.claude_action,
    }, ensure_ascii=False))
    return 0


def begin_run(
    *,
    kind: str,
    meta_cli: str,
    scientist_cli: str,
    target: Path,
    max_cycles: int,
    output_mode: str,
    meta_model: str | None,
    scientist_model: str | None,
    meta_effort: str | None,
    scientist_effort: str | None,
) -> tuple[Path, dict[str, Any]]:
    run_id, run_dir = create_run_directory(target)
    metadata: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id,
        "kind": kind,
        # Keep the historical fields as the META transport for compatibility.
        "cli": meta_cli,
        "model": meta_model,
        "meta_cli": meta_cli,
        "meta_model": meta_model,
        "meta_effort": meta_effort,
        "scientist_cli": scientist_cli,
        "scientist_model": scientist_model,
        "scientist_effort": scientist_effort,
        "target": str(target),
        "max_cycles": max_cycles,
        "started_at": utc_now(),
        "status": "running",
    }
    write_json(run_dir / "run.json", metadata)
    if output_mode != "quiet":
        print("Research Agent")
        print(f"  Project   {target.name}")
        if meta_cli == scientist_cli and meta_model == scientist_model:
            print(f"  Runner    {meta_cli}")
            if meta_model is not None:
                print(f"  Model     {meta_model}")
        else:
            meta_label = meta_cli if meta_model is None else f"{meta_cli} / {meta_model}"
            scientist_label = scientist_cli if scientist_model is None else f"{scientist_cli} / {scientist_model}"
            print(f"  META      {meta_label}")
            print(f"  Scientist {scientist_label}")
        print(f"  Run       {run_id[:8]}")
        print(f"  Runtime   {run_dir}")
    return run_dir, metadata


def _mixed_runner_usage(meta_cli: str, scientist_cli: str) -> dict[str, Any]:
    return {
        "runner": "mixed",
        "accounting_status": "unavailable",
        "scope": "run_delta",
        "final": False,
        "observed_at": utc_now(),
        "roles": {"meta": meta_cli, "scientist": scientist_cli},
        "reason": "Run usage is not aggregated across different runner telemetry backends",
    }


def execute_meta_session(
    *,
    root: Path,
    run_dir: Path,
    meta_cli: str,
    scientist_cli: str,
    target: Path,
    max_cycles: int,
    output_mode: str,
    meta_model: str | None,
    scientist_model: str | None,
    meta_effort: str | None,
    scientist_effort: str | None,
) -> tuple[CycleResult, int, Path]:
    start_cycle_id = next_cycle_id(target)
    session_dir = run_dir / "meta"
    session_dir.mkdir(parents=True, exist_ok=False)
    log_path = session_dir / "meta.log"
    usage_path = session_dir / "usage.json"
    result_path = session_dir / "result.json"
    usage_before = collect(root, target, runner=meta_cli, final=False) if meta_cli == scientist_cli else None

    environment = {
        "RESEARCH_AGENT_ROLE": "META",
        "RESEARCH_AGENT_META_SESSION": "1",
        "RESEARCH_AGENT_START_CYCLE": str(start_cycle_id),
        "RESEARCH_AGENT_MAX_CYCLES": str(max_cycles),
        # Historical generic variables continue to describe the delegated
        # Scientist launch, which is what nested launch-inner consumes.
        "RESEARCH_AGENT_CLI": scientist_cli,
        "RESEARCH_AGENT_META_CLI": meta_cli,
        "RESEARCH_AGENT_SCIENTIST_CLI": scientist_cli,
        "RESEARCH_AGENT_TARGET": str(target),
        "RESEARCH_AGENT_CYCLE_RESULT_FILE": str(result_path),
    }
    if meta_model is not None:
        environment["RESEARCH_AGENT_META_MODEL"] = meta_model
    if scientist_model is not None:
        environment["RESEARCH_AGENT_MODEL"] = scientist_model
        environment["RESEARCH_AGENT_SCIENTIST_MODEL"] = scientist_model
    if meta_effort is not None:
        environment["RESEARCH_AGENT_META_EFFORT"] = meta_effort
    if scientist_effort is not None:
        environment["RESEARCH_AGENT_SCIENTIST_EFFORT"] = scientist_effort
    if output_mode != "quiet":
        end_cycle_id = start_cycle_id + max_cycles - 1
        print(f"→ META · cycle budget {start_cycle_id}-{end_cycle_id}", flush=True)

    try:
        invocation = build_meta_invocation(
            cli=meta_cli,
            target=target,
            cycle_result=result_path,
            start_cycle_id=start_cycle_id,
            max_cycles=max_cycles,
            allow_edits=True,
            model=meta_model,
            effort=meta_effort,
            scientist_cli=scientist_cli,
            scientist_model=scientist_model,
            scientist_effort=scientist_effort,
        )
        return_code = run_invocation(
            invocation,
            environment=environment,
            output_path=log_path,
            stream_output=output_mode == "verbose",
        )
    except (OSError, RuntimeError, ValueError) as exc:
        return_code = 127
        log_path.write_text(f"error: {exc}\n", encoding="utf-8")
        result = synthetic_result("failed", str(exc), "Install or select an available CLI.")
    else:
        if return_code != 0:
            result = synthetic_result(
                "failed",
                f"META CLI exited with code {return_code}.",
                "Inspect the META output and project state before retrying.",
            )
        else:
            result = read_cycle_result(result_path)

    if usage_before is None:
        usage_report = _mixed_runner_usage(meta_cli, scientist_cli)
    else:
        usage_after = collect(root, target, runner=meta_cli, final=True)
        usage_report = run_delta(usage_after, usage_before)
    write_json(usage_path, usage_report)
    if not result_path.exists():
        write_json(result_path, result.to_dict())

    if output_mode != "quiet":
        marker = "✓" if result.status in {"continue", "converged", "budget_exhausted"} and return_code == 0 else "!"
        print(f"{marker} META · {result.status}")
        print(f"  Summary   {result.summary}")
        print(f"  Next      {result.next_action}")
        print(f"  Log       {log_path}")
        if output_mode == "normal" and (return_code != 0 or result.status == "failed"):
            recent_output = tail_lines(log_path)
            if recent_output:
                print("  Last output")
                for line in recent_output:
                    print(f"    {line}")
    return result, return_code, log_path


def finish_run(
    run_dir: Path,
    metadata: dict[str, Any],
    *,
    result: CycleResult,
    exit_code: int,
    output_mode: str,
    log_path: Path | None,
) -> int:
    metadata.update({
        "ended_at": utc_now(),
        "terminal_status": result.status,
        "status": "closed",
        "exit_code": exit_code,
    })
    write_json(run_dir / "run.json", metadata)
    if output_mode == "quiet":
        suffix = f"; log={log_path}" if exit_code != 0 and log_path is not None else ""
        print(f"research-agent: {result.status}{suffix}")
    else:
        marker = "✓" if exit_code == 0 else "!"
        print(f"{marker} Finished · {result.status}")
    return exit_code


def status_exit_code(result: CycleResult, runner_code: int) -> int:
    if runner_code != 0 or result.status == "failed":
        return runner_code if runner_code != 0 else 1
    if result.status == "needs_human":
        return 4
    return 0


def reject_nested_meta_cycle(command: str) -> None:
    if os.environ.get("RESEARCH_AGENT_META_SESSION") == "1":
        raise BootstrapError(
            f"cannot launch research-agent {command} from an active META session; "
            "META should launch Scientist with research-agent launch-inner"
        )
    role = os.environ.get("RESEARCH_AGENT_ROLE")
    if role in {"SCIENTIST", "PARALLEL_REVIEWER"}:
        raise BootstrapError(
            f"cannot launch research-agent {command} from an active {role} session; "
            "return control to META"
        )


def _prepare_existing_cycle_target(args: argparse.Namespace) -> Path:
    target, _ = prepare_target(target=args.target, new_target=None)
    ensure_target_git_root(target, create_if_missing=False)
    require_supported_record(target)
    return target


def command_step(args: argparse.Namespace) -> int:
    reject_nested_meta_cycle("step")
    if not args.allow_edits:
        raise BootstrapError("step requires explicit --allow-edits")
    root = skill_root()
    target = _prepare_existing_cycle_target(args)
    output_mode = resolved_output_mode(args)
    (
        meta_cli,
        scientist_cli,
        meta_model,
        scientist_model,
        meta_effort,
        scientist_effort,
    ) = resolved_role_config(args)
    run_dir, metadata = begin_run(
        kind="step",
        meta_cli=meta_cli,
        scientist_cli=scientist_cli,
        target=target,
        max_cycles=1,
        output_mode=output_mode,
        meta_model=meta_model,
        scientist_model=scientist_model,
        meta_effort=meta_effort,
        scientist_effort=scientist_effort,
    )
    result = synthetic_result("needs_human", "META did not complete.")
    runner_code = 0
    log_path: Path | None = None
    try:
        result, runner_code, log_path = execute_meta_session(
            root=root,
            run_dir=run_dir,
            meta_cli=meta_cli,
            scientist_cli=scientist_cli,
            target=target,
            max_cycles=1,
            output_mode=output_mode,
            meta_model=meta_model,
            scientist_model=scientist_model,
            meta_effort=meta_effort,
            scientist_effort=scientist_effort,
        )
    except KeyboardInterrupt:
        result = synthetic_result(
            "needs_human",
            "Research step was interrupted by the operator.",
            "Inspect the current project before resuming.",
        )
        runner_code = 130
    return finish_run(
        run_dir, metadata, result=result,
        exit_code=status_exit_code(result, runner_code), output_mode=output_mode, log_path=log_path,
    )


def command_run(args: argparse.Namespace) -> int:
    reject_nested_meta_cycle(getattr(args, "command", "run"))
    if not args.allow_edits:
        raise BootstrapError("run requires explicit --allow-edits")
    if args.max_cycles < 1:
        raise BootstrapError("--max-cycles must be a positive integer")
    root = skill_root()
    target = _prepare_existing_cycle_target(args)
    kind = getattr(args, "command", "run")
    output_mode = resolved_output_mode(args)
    (
        meta_cli,
        scientist_cli,
        meta_model,
        scientist_model,
        meta_effort,
        scientist_effort,
    ) = resolved_role_config(args)
    run_dir, metadata = begin_run(
        kind=kind,
        meta_cli=meta_cli,
        scientist_cli=scientist_cli,
        target=target,
        max_cycles=args.max_cycles,
        output_mode=output_mode,
        meta_model=meta_model,
        scientist_model=scientist_model,
        meta_effort=meta_effort,
        scientist_effort=scientist_effort,
    )
    result = synthetic_result("needs_human", "META did not complete.")
    runner_code = 0
    log_path: Path | None = None
    try:
        result, runner_code, log_path = execute_meta_session(
            root=root,
            run_dir=run_dir,
            meta_cli=meta_cli,
            scientist_cli=scientist_cli,
            target=target,
            max_cycles=args.max_cycles,
            output_mode=output_mode,
            meta_model=meta_model,
            scientist_model=scientist_model,
            meta_effort=meta_effort,
            scientist_effort=scientist_effort,
        )
    except KeyboardInterrupt:
        result = synthetic_result(
            "needs_human",
            "Autonomous run was interrupted by the operator.",
            "Inspect the current project before resuming.",
        )
        runner_code = 130
    return finish_run(
        run_dir, metadata, result=result,
        exit_code=status_exit_code(result, runner_code), output_mode=output_mode, log_path=log_path,
    )


def command_parallel(args: argparse.Namespace) -> int:
    reject_nested_meta_cycle("parallel")
    if not args.allow_edits:
        raise BootstrapError("parallel requires explicit --allow-edits")
    target = _prepare_existing_cycle_target(args)
    output_mode = resolved_output_mode(args)
    (
        meta_cli,
        scientist_cli,
        meta_model,
        scientist_model,
        meta_effort,
        scientist_effort,
    ) = resolved_role_config(args)
    try:
        result = run_parallel(
            target=target,
            meta_cli=meta_cli,
            scientist_cli=scientist_cli,
            meta_model=meta_model,
            scientist_model=scientist_model,
            meta_effort=meta_effort or "medium",
            scientist_effort=scientist_effort or "medium",
            rounds=args.rounds,
            branches=args.branches,
            keep=args.keep,
            parallelism=args.parallelism,
            share_inputs=args.share_inputs,
            synthesis=args.synthesis,
        )
    except KeyboardInterrupt:
        print(
            "research-agent: parallel interrupted; inspect retained branch worktrees",
            file=sys.stderr,
        )
        return 130
    if output_mode == "quiet":
        print(f"research-agent: parallel {result['status']}; result={result['result_path']}")
    else:
        print(f"Parallel {result['parallel_id']} · {result['status']}")
        print(f"  Summary   {result['summary']}")
        print(f"  Next      {result['next_action']}")
        print(f"  Result    {result['result_path']}")
    return 0 if result["status"] == "completed" else 4


def command_parallel_promote(args: argparse.Namespace) -> int:
    reject_nested_meta_cycle("parallel-promote")
    if not args.allow_edits:
        raise BootstrapError("parallel-promote requires explicit --allow-edits")
    target = _prepare_existing_cycle_target(args)
    result = promote_parallel_branch(
        target=target,
        parallel_dir=args.parallel_dir,
        branch_id=args.branch,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


def command_launch_inner(args: argparse.Namespace) -> int:
    target, _ = prepare_target(target=args.target, new_target=None)
    ensure_target_git_root(target, create_if_missing=False)
    require_supported_record(target)
    if not args.allow_edits:
        raise BootstrapError("Scientist launch requires explicit --allow-edits")

    record = target / "research_record"
    brief_path = record / "runtime" / "current-brief.json"
    brief = read_cycle_brief(brief_path)

    model = (
        getattr(args, "model", None)
        or os.environ.get("RESEARCH_AGENT_SCIENTIST_MODEL")
        or os.environ.get("RESEARCH_AGENT_MODEL")
    )
    effort = (
        getattr(args, "effort", None)
        or os.environ.get("RESEARCH_AGENT_SCIENTIST_EFFORT")
        or os.environ.get("RESEARCH_AGENT_EFFORT")
    )
    invocation = build_inner_invocation(
        cli=args.cli,
        target=target,
        allow_edits=True,
        prompt=args.prompt,
        brief_path=brief_path,
        model=model,
        effort=effort,
    )
    environment = {
        "RESEARCH_AGENT_ROLE": "SCIENTIST",
        "RESEARCH_AGENT_TARGET": str(target),
        "RESEARCH_AGENT_CYCLE": str(brief.cycle_id),
        "RESEARCH_AGENT_BRIEF": str(brief_path),
    }
    try:
        # Scientist wall time is advisory coordination data. Do not terminate a
        # valid research iteration merely because META wrote a time estimate in
        # an older or third-party brief; operator interruption remains supported
        # by run_invocation/process-group cleanup.
        return run_invocation(invocation, environment=environment)
    except KeyboardInterrupt:
        return 130
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 124 if "wall-time budget" in str(exc) else 127


def command_usage(args: argparse.Namespace) -> int:
    root = skill_root()
    target, _ = prepare_target(target=args.target, new_target=None)
    include_paths = tuple(path.expanduser().resolve() for path in args.include_path)
    report = collect(root, target, runner=args.cli, final=args.final, session=args.session, include_paths=include_paths)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report.get("accounting_status") != "unavailable" else 1


def command_doctor(args: argparse.Namespace) -> int:
    names = (args.cli,) if args.cli else supported_runners()
    failed = False
    for name in names:
        executable = shutil.which(name)
        if executable is None:
            print(json.dumps({"cli": name, "status": "unavailable"}))
            failed = True
            continue
        completed = subprocess.run([name, "--version"], check=False, capture_output=True, text=True, timeout=10)
        output = completed.stdout or completed.stderr
        version = output.strip().splitlines()[-1] if output else ""
        print(json.dumps({"cli": name, "status": "available", "path": executable, "version": version}))
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Install the Scientist research scaffold")
    add_init_arguments(init_parser)
    init_parser.set_defaults(handler=command_init)

    step_parser = subparsers.add_parser("step", help="Run one META/Scientist cycle and stop")
    add_cycle_arguments(step_parser)
    step_parser.set_defaults(handler=command_step)

    run_parser = subparsers.add_parser("run", help="Run one persistent META session with bounded Scientist iterations")
    add_cycle_arguments(run_parser)
    run_parser.add_argument("--max-cycles", type=int, required=True)
    run_parser.set_defaults(handler=command_run)

    resume_parser = subparsers.add_parser("resume", help="Start another persistent META session from durable project state")
    add_cycle_arguments(resume_parser)
    resume_parser.add_argument("--max-cycles", type=int, required=True)
    resume_parser.set_defaults(handler=command_run)

    parallel_parser = subparsers.add_parser(
        "parallel",
        help="Run independent Scientist replicas and post-hoc review in isolated worktrees",
    )
    add_parallel_arguments(parallel_parser)
    parallel_parser.set_defaults(handler=command_parallel)

    promote_parser = subparsers.add_parser(
        "parallel-promote",
        help="Adopt one reviewed Parallel research world into the target",
    )
    add_target_arguments(promote_parser, allow_new=False)
    promote_parser.add_argument("--parallel-dir", type=Path, required=True)
    promote_parser.add_argument("--branch", required=True)
    promote_parser.add_argument("--allow-edits", action="store_true")
    promote_parser.set_defaults(handler=command_parallel_promote)

    inner_parser = subparsers.add_parser("launch-inner", help="Launch one project-local Scientist")
    add_target_arguments(inner_parser, allow_new=False)
    inner_parser.add_argument("--cli", "--runner", dest="cli", choices=supported_runners(), required=True)
    inner_parser.add_argument("--model")
    inner_parser.add_argument("--effort", choices=EFFORT_LEVELS)
    inner_parser.add_argument("--allow-edits", action="store_true")
    inner_parser.add_argument("--prompt")
    inner_parser.set_defaults(handler=command_launch_inner)

    usage_parser = subparsers.add_parser("usage", help="Collect best-effort target telemetry")
    add_target_arguments(usage_parser, allow_new=False)
    usage_parser.add_argument("--cli", "--runner", dest="cli", choices=supported_runners(), required=True)
    usage_parser.add_argument("--session")
    usage_parser.add_argument("--include-path", action="append", type=Path, default=[])
    usage_parser.add_argument("--final", action="store_true")
    usage_parser.set_defaults(handler=command_usage)

    doctor_parser = subparsers.add_parser("doctor", help="Inspect available runner CLIs")
    doctor_parser.add_argument("--cli", choices=supported_runners())
    doctor_parser.set_defaults(handler=command_doctor)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (BootstrapError, ValueError) as exc:
        parser.error(str(exc))
    return 2
