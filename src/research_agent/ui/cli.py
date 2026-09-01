from __future__ import annotations

import argparse
import time
from pathlib import Path

from research_agent.bootstrap import BootstrapError, ensure_target_git_root, require_supported_record
from research_agent.ui.lifecycle import latest_run, read_run
from research_agent.ui.progress import SemanticProgress
from research_agent.ui.render import render_status
from research_agent.ui.status import inspect_status
from research_agent.ui.web import serve_dashboard


def _target(parser: argparse.ArgumentParser, value: Path) -> Path:
    try:
        target = ensure_target_git_root(value, create_if_missing=False)
        require_supported_record(target)
        return target
    except BootstrapError as exc:
        parser.error(str(exc))
    raise AssertionError("argparse.error must exit")


def status_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-agent status", description="Show the current semantic research state")
    parser.add_argument("--target", type=Path, required=True, help="Existing target project")
    args = parser.parse_args(argv)
    target = _target(parser, args.target)
    print(render_status(inspect_status(target)))
    return 0


def gui_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-agent gui", description="Serve the local research dashboard")
    parser.add_argument("--target", type=Path, required=True, help="Existing target project")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (default: 8000)")
    parser.add_argument("--no-open", action="store_true", help="Do not open the dashboard in a browser")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    target = _target(parser, args.target)
    return serve_dashboard(target, host=args.host, port=args.port, open_browser=not args.no_open)


def _run_label(run_id: str, kind: str | None = None) -> str:
    suffix = f" · {kind}" if kind else ""
    return f"{run_id[:8]}{suffix}"


def _print_completed_run(target: Path, run_id: str, terminal_status: str | None) -> None:
    print(f"✓ Run {_run_label(run_id)} · {terminal_status or 'closed'}")
    print("\n" + render_status(inspect_status(target)))


def watch_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-agent watch", description="Watch semantic research progress")
    parser.add_argument("--target", type=Path, required=True, help="Existing target project")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    args = parser.parse_args(argv)
    if args.interval <= 0:
        parser.error("--interval must be positive")
    target = _target(parser, args.target)
    progress = SemanticProgress(target)
    assert progress.previous is not None
    print(render_status(progress.previous))

    initial_run = latest_run(target)
    seen_run_id = initial_run.run_id if initial_run is not None else None
    if initial_run is not None and initial_run.status == "running":
        tracked_run_id = initial_run.run_id
        print(f"\nWatching run {_run_label(tracked_run_id, initial_run.kind)}. Press Ctrl-C to stop.")
    else:
        tracked_run_id = None
        print("\nNo active run. Waiting for the next run. Press Ctrl-C to stop.")

    try:
        while True:
            time.sleep(args.interval)
            progress.poll()

            if tracked_run_id is not None:
                run = read_run(target, tracked_run_id)
                if run is not None and run.status == "closed":
                    _print_completed_run(target, run.run_id, run.terminal_status)
                    return 0
                continue

            run = latest_run(target)
            if run is None or run.run_id == seen_run_id:
                continue
            seen_run_id = run.run_id
            if run.status == "running":
                tracked_run_id = run.run_id
                print(f"→ Run {_run_label(run.run_id, run.kind)} started", flush=True)
            elif run.status == "closed":
                _print_completed_run(target, run.run_id, run.terminal_status)
                return 0
    except KeyboardInterrupt:
        return 0
