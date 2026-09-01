from __future__ import annotations

import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from research_agent.bootstrap import BootstrapError, ensure_target_git_root, require_supported_record
from research_agent.launcher import run_invocation
from research_agent.parallel_support import (
    SCHEMA,
    BranchRecord,
    add_worktree,
    build_parallel_reviewer_invocation,
    build_parallel_scientist_invocation,
    cleanup_worktrees,
    environment,
    execute_scientist_branch,
    git_output,
    prepare_control,
    promote_selected,
    read_object,
    snapshot_memory,
    state_descriptor,
    system_status,
    usage_report,
)
from research_agent.parallel_synthesis import (
    build_synthesis_reviewer_invocation,
    build_synthesis_scientist_invocation,
    prepare_synthesis_branch,
    read_synthesis_request,
)
from research_agent.runtime import create_run_directory, utc_now, write_json

PARALLEL_SCHEMA_VERSION = SCHEMA
_parallel_usage_report = usage_report


def _branch_specs(
    frontier: list[str],
    *,
    round_number: int,
    branches: int,
    existing: set[str],
) -> list[BranchRecord]:
    result: list[BranchRecord] = []
    counter = 1
    for parent in frontier:
        for replica in range(1, branches + 1):
            while f"r{round_number}b{counter}" in existing:
                counter += 1
            branch_id = f"r{round_number}b{counter}"
            counter += 1
            existing.add(branch_id)
            result.append(BranchRecord(
                branch_id=branch_id,
                parent_branch=parent,
                replica=replica,
            ))
    return result


def _review_result(
    path: Path,
    *,
    parallel_id: str,
    round_number: int,
    available: set[str],
    keep: int,
    exit_code: int,
) -> dict[str, Any]:
    payload = read_object(path)
    if payload is None:
        return {
            "schema_version": SCHEMA,
            "parallel_id": parallel_id,
            "round": round_number,
            "selected_branches": [],
            "rejected": [],
            "summary": "Parallel Reviewer did not write a valid result.",
            "next_action": "Inspect branch artifacts manually.",
            "status": "failed" if exit_code else "needs_human",
        }
    selected = payload.get("selected_branches")
    if not isinstance(selected, list):
        selected = []
    valid = [
        x for x in selected
        if isinstance(x, str) and x in available
    ]
    payload.update({
        "schema_version": SCHEMA,
        "parallel_id": parallel_id,
        "round": round_number,
        "selected_branches": list(dict.fromkeys(valid))[:keep],
        "status": "completed" if exit_code == 0 else "failed",
        "exit_code": exit_code,
        "observed_at": utc_now(),
    })
    return payload


def _aggregate(parallel_dir: Path, manifest: dict[str, Any]) -> None:
    branches = [
        {
            key: branch.get(key)
            for key in (
                "kind", "round", "branch_id", "parent_branch", "primary_branch",
                "informed_by", "replica", "status", "summary", "candidate_commit",
                "candidate_state_id", "memory_snapshot", "result_path", "workspace_retained",
            )
        }
        for rr in manifest.get("rounds_log", [])
        for branch in rr.get("branches", [])
        if isinstance(branch, dict)
    ]
    write_json(parallel_dir / "aggregate.json", {
        "schema_version": SCHEMA,
        "parallel_id": manifest["parallel_id"],
        "target": manifest["target"],
        "synthesis_enabled": bool(manifest.get("synthesis_enabled")),
        "selected_branches": [
            branch_id
            for rr in manifest.get("rounds_log", [])
            for branch_id in rr.get("selected_branches", [])
            if isinstance(branch_id, str)
        ],
        "branches": branches,
        "note": (
            "Each branch is an independent research world. A synthesis branch has one primary "
            "State parent and may be informed by reference-only evidence from other worlds. "
            "Final selected worktrees are retained until explicit parallel-promote adoption."
        ),
        "observed_at": utc_now(),
    })
    lines = [
        f"# Parallel {manifest['parallel_id']} aggregate", "",
        "| Round | Branch | Kind | Parent | Status | Candidate State | Retained |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for branch in branches:
        lines.append(
            f"| {branch['round']} | {branch['branch_id']} | {branch.get('kind') or 'replica'} | "
            f"{branch['parent_branch']} | {branch['status']} | "
            f"{branch['candidate_state_id'] or '-'} | "
            f"{'yes' if branch['workspace_retained'] else 'no'} |"
        )
    (parallel_dir / "aggregate.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _finish(
    run_dir: Path,
    parallel_dir: Path,
    manifest: dict[str, Any],
    result: dict[str, Any],
    *,
    retain_worktrees: bool = True,
) -> dict[str, Any]:
    manifest["status"] = result["status"]
    manifest["ended_at"] = utc_now()
    write_json(parallel_dir / "result.json", result)
    write_json(parallel_dir / "manifest.json", manifest)
    _aggregate(parallel_dir, manifest)

    meta = run_dir / "meta"
    meta.mkdir(parents=True, exist_ok=True)
    write_json(meta / "model-usage.json", usage_report(parallel_dir))

    selected = result.get("selected_branches")
    if not retain_worktrees:
        keep: set[str] = set()
    elif result["status"] == "completed" and isinstance(selected, list):
        keep = set(selected)
    else:
        keep = {
            str(branch["branch_id"])
            for rr in manifest.get("rounds_log", [])
            for branch in rr.get("branches", [])
            if isinstance(branch, dict) and branch.get("branch_id")
        }
    cleanup_worktrees(manifest, keep)
    write_json(parallel_dir / "manifest.json", manifest)
    _aggregate(parallel_dir, manifest)
    write_json(run_dir / "run.json", {
        "schema_version": 1,
        "run_id": run_dir.name,
        "kind": "parallel",
        "target": manifest["target"],
        "parallel_id": manifest["parallel_id"],
        "started_at": manifest["started_at"],
        "ended_at": manifest["ended_at"],
        "status": "closed",
        "terminal_status": result["status"],
        "exit_code": 0 if result["status"] == "completed" else 4,
    })
    return result


def _failure(
    run_dir: Path,
    parallel_dir: Path,
    manifest: dict[str, Any],
    summary: str,
) -> dict[str, Any]:
    return _finish(run_dir, parallel_dir, manifest, {
        "schema_version": SCHEMA,
        "parallel_id": manifest["parallel_id"],
        "status": "needs_human",
        "summary": summary,
        "next_action": "Inspect retained Parallel artifacts before retrying.",
        "selected_branches": [],
        "result_path": str(parallel_dir / "result.json"),
        "observed_at": utc_now(),
    })


def _abort(
    run_dir: Path,
    parallel_dir: Path,
    manifest: dict[str, Any],
    summary: str,
) -> dict[str, Any]:
    """Close a run after a bootstrap failure and remove disposable worktrees."""

    result = _finish(
        run_dir,
        parallel_dir,
        manifest,
        {
            "schema_version": SCHEMA,
            "parallel_id": manifest["parallel_id"],
            "status": "failed",
            "summary": summary,
            "next_action": "Fix the runtime bootstrap error before retrying.",
            "selected_branches": [],
            "result_path": str(parallel_dir / "result.json"),
            "observed_at": utc_now(),
        },
        retain_worktrees=False,
    )
    worktree_root = Path(str(manifest.get("worktree_root") or ""))
    if worktree_root.is_dir():
        try:
            worktree_root.rmdir()
        except OSError:
            pass
    return result


def _eligible_branches(all_branches: dict[str, BranchRecord]) -> set[str]:
    return {
        branch_id for branch_id, branch in all_branches.items()
        if branch.get("status") == "completed" and not branch.get("system_state_dirty")
    }


def _optional_synthesis(
    *,
    target: Path,
    run_dir: Path,
    parallel_dir: Path,
    worktrees: Path,
    control: Path,
    manifest: dict[str, Any],
    all_branches: dict[str, BranchRecord],
    selected: list[str],
    meta_cli: str,
    scientist_cli: str,
    meta_model: str | None,
    scientist_model: str | None,
    meta_effort: str | None,
    scientist_effort: str | None,
    keep: int,
) -> tuple[list[str], dict[str, Any]]:
    rr = manifest["rounds_log"][-1]
    eligible = _eligible_branches(all_branches)
    record: dict[str, Any]
    if not selected or len(eligible) < 2:
        record = {
            "status": "not_applicable",
            "summary": "Synthesis needs a selected primary and at least one other completed research world.",
        }
        rr["synthesis"] = record
        return selected, record

    control_dir = prepare_control(target, target, control, parallel_dir, manifest, manifest["base_commit"])
    check_path = control_dir / "synthesis-check.json"
    check_run = parallel_dir / "meta" / "synthesis-check"
    check_run.mkdir(parents=True, exist_ok=True)
    try:
        invocation = build_synthesis_reviewer_invocation(
            cli=meta_cli,
            target=control,
            manifest_path=control_dir / "manifest.json",
            result_path=check_path,
            parallel_id=manifest["parallel_id"],
            selected_branches=selected,
            candidate_branches=sorted(eligible),
            model=meta_model,
            effort=meta_effort,
        )
        code = run_invocation(
            invocation,
            environment=environment(
                run_dir=check_run,
                role="PARALLEL_REVIEWER",
                parallel_id=manifest["parallel_id"],
            ),
            output_path=check_run / "reviewer.log",
            stream_output=False,
        )
    except KeyboardInterrupt:
        raise
    except (RuntimeError, OSError, ValueError) as exc:
        record = {"status": "failed", "summary": f"Synthesis check failed: {exc}"}
        rr["synthesis"] = record
        write_json(parallel_dir / "synthesis-check.normalized.json", record)
        return selected, record

    request, record = read_synthesis_request(
        check_path,
        eligible=eligible,
        selected=set(selected),
        exit_code=code,
    )
    rr["synthesis"] = record
    write_json(parallel_dir / "synthesis-check.normalized.json", record)
    if request is None:
        return selected, record

    primary = all_branches[request["primary_branch"]]
    try:
        synthesis_branch = prepare_synthesis_branch(
            repository=target,
            worktree_root=worktrees,
            parallel_dir=parallel_dir,
            parallel_id=manifest["parallel_id"],
            round_number=int(rr["round"]),
            primary=primary,
            informed_by=list(request["informed_by"]),
            branches=all_branches,
        )
    except (BootstrapError, OSError, ValueError) as exc:
        record.update(status="failed", summary=f"Could not prepare synthesis world: {exc}")
        rr["synthesis"] = record
        write_json(parallel_dir / "synthesis-check.normalized.json", record)
        return selected, record

    rr["branches"].append(synthesis_branch)
    all_branches[synthesis_branch["branch_id"]] = synthesis_branch
    write_json(parallel_dir / "manifest.json", manifest)
    try:
        synthesis_invocation = build_synthesis_scientist_invocation(
            cli=scientist_cli,
            target=Path(str(synthesis_branch["workspace"])),
            context_path=Path(str(synthesis_branch["context_path"])),
            result_path=Path(str(synthesis_branch["scientist_result_path"])),
            parallel_id=manifest["parallel_id"],
            branch_id=str(synthesis_branch["branch_id"]),
            model=scientist_model,
            effort=scientist_effort,
        )
        execute_scientist_branch(
            invocation=synthesis_invocation,
            branch=synthesis_branch,
            parallel_id=manifest["parallel_id"],
            usage_dir=parallel_dir / "usage" / f"synthesis-{synthesis_branch['branch_id']}",
            runner=run_invocation,
        )
    except KeyboardInterrupt:
        raise
    except (RuntimeError, OSError, BootstrapError) as exc:
        synthesis_branch["status"] = "failed"
        synthesis_branch["summary"] = f"Synthesis Scientist failed: {exc}"

    record["branch_id"] = synthesis_branch["branch_id"]
    record["branch_status"] = synthesis_branch.get("status")
    if synthesis_branch.get("status") != "completed" or synthesis_branch.get("system_state_dirty"):
        record["status"] = "completed_without_candidate"
        record["summary"] = (
            "Synthesis was attempted but did not produce a clean completed research world: "
            f"{synthesis_branch.get('summary', '')}"
        )
        rr["synthesis"] = record
        write_json(parallel_dir / "synthesis-check.normalized.json", record)
        return selected, record

    final_available = set(selected)
    final_available.add(str(synthesis_branch["branch_id"]))
    control_dir = prepare_control(target, target, control, parallel_dir, manifest, manifest["base_commit"])
    final_review_path = control_dir / "synthesis-final-review.json"
    final_review_run = parallel_dir / "meta" / "synthesis-final-review"
    final_review_run.mkdir(parents=True, exist_ok=True)
    try:
        final_invocation = build_parallel_reviewer_invocation(
            cli=meta_cli,
            target=control,
            manifest_path=control_dir / "manifest.json",
            result_path=final_review_path,
            parallel_id=manifest["parallel_id"],
            round_number=int(rr["round"]),
            keep=keep,
            candidate_branches=sorted(final_available),
            model=meta_model,
            effort=meta_effort,
        )
        final_code = run_invocation(
            final_invocation,
            environment=environment(
                run_dir=final_review_run,
                role="PARALLEL_REVIEWER",
                parallel_id=manifest["parallel_id"],
            ),
            output_path=final_review_run / "reviewer.log",
            stream_output=False,
        )
        final_review = _review_result(
            final_review_path,
            parallel_id=manifest["parallel_id"],
            round_number=int(rr["round"]),
            available=final_available,
            keep=keep,
            exit_code=final_code,
        )
    except KeyboardInterrupt:
        raise
    except (RuntimeError, OSError, ValueError) as exc:
        final_review = {
            "schema_version": SCHEMA,
            "parallel_id": manifest["parallel_id"],
            "round": rr["round"],
            "selected_branches": selected,
            "summary": f"Final synthesis review failed; preserving pre-synthesis selection: {exc}",
            "next_action": "Inspect synthesis artifacts.",
            "status": "failed",
        }

    normalized = parallel_dir / "synthesis-final-review.normalized.json"
    write_json(normalized, final_review)
    record.update({
        "status": "completed",
        "final_review_path": str(normalized),
        "final_review": final_review,
    })
    raw_selected = final_review.get("selected_branches")
    if final_review.get("status") == "completed" and isinstance(raw_selected, list):
        selected = list(raw_selected)
    rr["selected_branches"] = selected
    rr["synthesis"] = record
    write_json(parallel_dir / "manifest.json", manifest)
    _aggregate(parallel_dir, manifest)
    return selected, record


def run_parallel(
    *,
    target: Path,
    meta_cli: str,
    scientist_cli: str,
    meta_model: str | None,
    scientist_model: str | None,
    meta_effort: str | None,
    scientist_effort: str | None,
    rounds: int,
    branches: int,
    keep: int,
    parallelism: int,
    share_inputs: bool,
    synthesis: bool = False,
) -> dict[str, Any]:
    for value, name in (
        (rounds, "--rounds"),
        (branches, "--branches"),
        (keep, "--keep"),
        (parallelism, "--parallelism"),
    ):
        if value < 1:
            raise BootstrapError(f"{name} must be a positive integer")
    if share_inputs:
        raise BootstrapError(
            "--share-inputs is disabled because Parallel cannot enforce a portable read-only mount"
        )

    target = target.expanduser().resolve()
    ensure_target_git_root(target, create_if_missing=False)
    require_supported_record(target)
    if system_status(target):
        raise BootstrapError("Parallel requires a clean system/** and STATE.yaml boundary")

    base_commit = git_output(target, "rev-parse", "HEAD")
    run_id, run_dir = create_run_directory(target)
    parallel_dir = run_dir / "parallel"
    branch_dir = parallel_dir / "branches"
    branch_dir.mkdir(parents=True, exist_ok=False)
    base_memory = parallel_dir / "base-memory"
    snapshot_memory(target, base_memory, include_meta=False)

    parallel_id = f"P{run_id[:8]}"
    worktrees = Path(tempfile.mkdtemp(prefix=f"research-agent-{parallel_id}-"))
    control = worktrees / "control"
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA,
        "parallel_id": parallel_id,
        "kind": "parallel",
        "target": str(target),
        "base_commit": base_commit,
        "base_state": state_descriptor(target / "research_record/STATE.yaml"),
        "base_memory_snapshot": str(base_memory),
        "worktree_root": str(worktrees),
        "control_workspace": str(control),
        "rounds": rounds,
        "branches": branches,
        "keep": keep,
        "parallelism": parallelism,
        "synthesis_enabled": synthesis,
        "started_at": utc_now(),
        "status": "running",
        "rounds_log": [],
    }
    write_json(parallel_dir / "manifest.json", manifest)
    write_json(run_dir / "run.json", {
        "schema_version": 1, "run_id": run_id, "kind": "parallel",
        "parallel_id": parallel_id, "target": str(target),
        "started_at": manifest["started_at"], "status": "running",
    })

    frontier = ["root"]
    all_branches: dict[str, BranchRecord] = {}
    selected: list[str] = []

    for round_number in range(1, rounds + 1):
        rr: dict[str, Any] = {"round": round_number, "branches": [], "selected_branches": []}
        manifest["rounds_log"].append(rr)
        ready: list[BranchRecord] = []

        for spec in _branch_specs(
            frontier, round_number=round_number, branches=branches, existing=set(all_branches)
        ):
            branch_id, parent_id = spec["branch_id"], spec["parent_branch"]
            if round_number == 1:
                source, commit = target, base_commit
                parent_state = manifest["base_state"]
            else:
                parent = all_branches[parent_id]
                source = Path(str(parent["workspace"]))
                commit = str(parent.get("candidate_commit") or "")
                parent_state = state_descriptor(source / "research_record/STATE.yaml")
                if not commit or system_status(source):
                    failed = BranchRecord(
                        **spec,
                        round=round_number,
                        status="failed",
                        summary="Parent research world has no clean usable commit.",
                    )
                    rr["branches"].append(failed)
                    continue

            workspace = worktrees / f"r{round_number}-{branch_id}"
            runtime = workspace / "research_record/runtime/parallel-branch"
            context = runtime / "parallel-branch.json"
            scientist_result = runtime / "parallel-result.json"
            branch = BranchRecord(
                **spec,
                kind="replica",
                round=round_number,
                base_commit=commit,
                base_state=parent_state,
                workspace=str(workspace),
                context_path=str(context),
                scientist_result_path=str(scientist_result),
                result_path=str(branch_dir / f"r{round_number}-{branch_id}.json"),
                log_path=str(branch_dir / f"r{round_number}-{branch_id}.log"),
                memory_snapshot=str(branch_dir / f"r{round_number}-{branch_id}-memory"),
                candidate_state_id=f"{parallel_id}-{branch_id}",
                status="prepared",
            )
            try:
                add_worktree(target, source, workspace, commit)
                runtime.mkdir(parents=True, exist_ok=True)
                write_json(context, {
                    "schema_version": SCHEMA,
                    "parallel_id": parallel_id,
                    "branch_id": branch_id,
                    "round": round_number,
                    "replica": spec["replica"],
                    "parent_branch": parent_id,
                    "base_commit": commit,
                    "base_state": parent_state,
                    "candidate_state_id": branch["candidate_state_id"],
                    "candidate_git_tag": f"state/{branch['candidate_state_id']}",
                    "constraints": [],
                    "budget": {},
                    "result_path": str(scientist_result),
                })
                branch["status"] = "running"
                ready.append(branch)
            except (BootstrapError, OSError, ValueError) as exc:
                branch["status"] = "failed"
                branch["summary"] = f"Could not prepare isolated worktree: {exc}"
            rr["branches"].append(branch)
            all_branches[branch_id] = branch

        write_json(parallel_dir / "manifest.json", manifest)
        if ready:
            cancel = threading.Event()
            executor = ThreadPoolExecutor(max_workers=min(parallelism, len(ready)))
            try:
                futures = {}
                for branch in ready:
                    invocation = build_parallel_scientist_invocation(
                        cli=scientist_cli,
                        target=Path(str(branch["workspace"])),
                        context_path=Path(str(branch["context_path"])),
                        result_path=Path(str(branch["scientist_result_path"])),
                        parallel_id=parallel_id,
                        branch_id=str(branch["branch_id"]),
                        round_number=round_number,
                        model=scientist_model,
                        effort=scientist_effort,
                    )
                    future = executor.submit(
                        execute_scientist_branch,
                        invocation=invocation,
                        branch=branch,
                        parallel_id=parallel_id,
                        usage_dir=parallel_dir / "usage" / f"r{round_number}-{branch['branch_id']}",
                        cancel_event=cancel,
                        runner=run_invocation,
                    )
                    futures[future] = branch
                for future in as_completed(futures):
                    branch = futures[future]
                    try:
                        branch.update(future.result())
                    except Exception as exc:  # pragma: no cover
                        branch["status"] = "failed"
                        branch["summary"] = f"Coordinator error: {exc}"
            except KeyboardInterrupt:
                cancel.set()
                executor.shutdown(wait=True, cancel_futures=True)
                return _failure(run_dir, parallel_dir, manifest, "Parallel Scientist round interrupted.")
            except (OSError, RuntimeError, ValueError) as exc:
                cancel.set()
                for branch in ready:
                    if branch.get("status") == "running":
                        branch["status"] = "failed"
                        branch["summary"] = f"Could not bootstrap Scientist invocation: {exc}"
                executor.shutdown(wait=True, cancel_futures=True)
                return _abort(
                    run_dir,
                    parallel_dir,
                    manifest,
                    f"Parallel Scientist bootstrap failed: {exc}",
                )
            else:
                executor.shutdown(wait=True)

        write_json(parallel_dir / "manifest.json", manifest)
        _aggregate(parallel_dir, manifest)
        available = {
            str(b["branch_id"]) for b in rr["branches"]
            if b.get("status") == "completed" and not b.get("system_state_dirty")
        }
        if round_number > 1:
            available.update(
                x for x in frontier
                if x in all_branches
                and all_branches[x].get("status") == "completed"
                and not all_branches[x].get("system_state_dirty")
            )

        try:
            control_dir = prepare_control(target, target, control, parallel_dir, manifest, base_commit)
        except (BootstrapError, OSError, RuntimeError, ValueError) as exc:
            return _abort(
                run_dir,
                parallel_dir,
                manifest,
                f"Parallel Reviewer bootstrap failed: {exc}",
            )
        review_path = control_dir / f"review-r{round_number}.json"
        reviewer_run = parallel_dir / "meta" / f"reviewer-r{round_number}"
        reviewer_run.mkdir(parents=True, exist_ok=True)
        try:
            invocation = build_parallel_reviewer_invocation(
                cli=meta_cli,
                target=control,
                manifest_path=control_dir / "manifest.json",
                result_path=review_path,
                parallel_id=parallel_id,
                round_number=round_number,
                keep=keep,
                candidate_branches=sorted(available),
                model=meta_model,
                effort=meta_effort,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            return _abort(
                run_dir,
                parallel_dir,
                manifest,
                f"Parallel Reviewer bootstrap failed: {exc}",
            )
        try:
            code = run_invocation(
                invocation,
                environment=environment(
                    run_dir=reviewer_run,
                    role="PARALLEL_REVIEWER",
                    parallel_id=parallel_id,
                ),
                output_path=reviewer_run / "reviewer.log",
                stream_output=False,
            )
            review = _review_result(
                review_path, parallel_id=parallel_id, round_number=round_number,
                available=available, keep=keep, exit_code=code,
            )
        except KeyboardInterrupt:
            return _failure(run_dir, parallel_dir, manifest, "Parallel Reviewer interrupted.")
        except (RuntimeError, OSError) as exc:
            code = 127
            review = {
                "schema_version": SCHEMA, "parallel_id": parallel_id, "round": round_number,
                "selected_branches": [], "summary": f"Parallel Reviewer failed: {exc}",
                "next_action": "Inspect branch artifacts.", "status": "failed",
            }

        normalized = parallel_dir / f"review-r{round_number}.normalized.json"
        write_json(normalized, review)
        rr["review_path"], rr["review"] = str(normalized), review
        raw = review.get("selected_branches")
        selected = list(raw) if isinstance(raw, list) else []
        rr["selected_branches"] = selected
        write_json(parallel_dir / "manifest.json", manifest)
        _aggregate(parallel_dir, manifest)

        if not selected:
            status = "completed" if code == 0 and review.get("status") == "completed" else "needs_human"
            return _finish(run_dir, parallel_dir, manifest, {
                "schema_version": SCHEMA,
                "parallel_id": parallel_id,
                "status": status,
                "summary": review.get("summary", "No research world was selected."),
                "next_action": review.get("next_action", "Inspect branch artifacts."),
                "selected_branches": [],
                "rounds_completed": round_number,
                "aggregate_path": str(parallel_dir / "aggregate.json"),
                "result_path": str(parallel_dir / "result.json"),
                "observed_at": utc_now(),
            })

        cleanup_worktrees(manifest, set(selected))
        write_json(parallel_dir / "manifest.json", manifest)
        _aggregate(parallel_dir, manifest)
        frontier = selected

    synthesis_record: dict[str, Any]
    if synthesis:
        try:
            selected, synthesis_record = _optional_synthesis(
                target=target,
                run_dir=run_dir,
                parallel_dir=parallel_dir,
                worktrees=worktrees,
                control=control,
                manifest=manifest,
                all_branches=all_branches,
                selected=selected,
                meta_cli=meta_cli,
                scientist_cli=scientist_cli,
                meta_model=meta_model,
                scientist_model=scientist_model,
                meta_effort=meta_effort,
                scientist_effort=scientist_effort,
                keep=keep,
            )
        except KeyboardInterrupt:
            return _failure(run_dir, parallel_dir, manifest, "Parallel synthesis interrupted.")
        except (BootstrapError, OSError, RuntimeError, ValueError) as exc:
            return _abort(
                run_dir,
                parallel_dir,
                manifest,
                f"Parallel synthesis bootstrap failed: {exc}",
            )
    else:
        synthesis_record = {
            "status": "disabled",
            "summary": "Research synthesis was not requested for this Parallel run.",
        }
        manifest["rounds_log"][-1]["synthesis"] = synthesis_record
        write_json(parallel_dir / "manifest.json", manifest)

    if synthesis_record.get("status") == "completed":
        summary = (
            f"Parallel research completed through {len(manifest['rounds_log'])} round(s), "
            "including one evidence-driven synthesis attempt and final review."
        )
    else:
        summary = f"Parallel research completed through {len(manifest['rounds_log'])} round(s)."
    next_action = (
        "Run parallel-promote on a selected branch to adopt its research world."
        if selected else "Inspect the completed branch and synthesis artifacts."
    )
    return _finish(run_dir, parallel_dir, manifest, {
        "schema_version": SCHEMA,
        "parallel_id": parallel_id,
        "status": "completed",
        "summary": summary,
        "next_action": next_action,
        "selected_branches": selected,
        "synthesis": synthesis_record,
        "rounds_completed": len(manifest["rounds_log"]),
        "aggregate_path": str(parallel_dir / "aggregate.json"),
        "result_path": str(parallel_dir / "result.json"),
        "observed_at": utc_now(),
    })


def promote_parallel_branch(
    *,
    target: Path,
    parallel_dir: Path,
    branch_id: str,
) -> dict[str, Any]:
    target = target.expanduser().resolve()
    parallel_dir = parallel_dir.expanduser().resolve()
    ensure_target_git_root(target, create_if_missing=False)
    require_supported_record(target)
    return promote_selected(target, parallel_dir, branch_id)
