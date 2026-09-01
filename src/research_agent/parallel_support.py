from __future__ import annotations

import json
import re
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Any, TypedDict

from research_agent.bootstrap import BootstrapError
from research_agent.launcher import run_invocation
from research_agent.prompt_context import (
    NO_SKILL_FILE_READ,
    REVIEWER_RUNTIME_RULES,
    RUNTIME_CONTEXT_PRECEDENCE,
    SCIENTIST_RUNTIME_RULES,
    injected_file,
    meta_startup_context,
    scientist_startup_context,
)
from research_agent.runners import get_adapter
from research_agent.runners.base import Invocation
from research_agent.runtime import utc_now, write_json
from research_agent.state import CreateStateResult, create_state_at_commit, validate_state_commit
from research_agent.usage_capture import model_usage_report

SCHEMA = 1
STATE_ID = re.compile(r"(?m)^id:\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*$")
STATE_TAG = re.compile(r"(?m)^git_tag:\s*(state/[A-Za-z0-9][A-Za-z0-9._-]*)\s*$")
DERIVED = re.compile(r"(?m)^derived_from:\s*([^\s#]+)\s*$")
MEMORY_FILES = (
    "research_record/RESEARCH_RECORD.yaml",
    "research_record/EXPLORE.md",
    "research_record/KNOWLEDGE.md",
    "research_record/ENGINEERING.md",
    "research_record/OPTIMIZE.md",
    "research_record/RESEARCH_INTUITION.md",
    "research_record/DO_BETTER.md",
)
ADOPT_FILES = MEMORY_FILES[:5]
ADOPT_DIRS = ("research_record/reports", "research_record/logs", "research_record/archive")


class StateDescriptor(TypedDict, total=False):
    id: str | None
    git_tag: str | None


class BranchRecord(TypedDict, total=False):
    kind: str
    branch_id: str
    parent_branch: str
    primary_branch: str
    informed_by: list[str]
    replica: int | None
    round: int
    base_commit: str
    base_state: StateDescriptor
    workspace: str
    context_path: str
    scientist_result_path: str
    result_path: str
    log_path: str
    memory_snapshot: str
    candidate_state_id: str
    candidate_commit: str
    system_state_dirty: bool
    status: str
    summary: str
    exit_code: int
    workspace_retained: bool


def git(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(target), *args],
        check=False, capture_output=True, text=True,
    )


def git_output(target: Path, *args: str) -> str:
    completed = git(target, *args)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise BootstrapError(f"git {' '.join(args)} failed in {target}: {detail}")
    return completed.stdout.strip()


def read_object(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def state_descriptor(path: Path) -> StateDescriptor:
    if not path.is_file():
        return {"id": None, "git_tag": None}
    text = path.read_text(encoding="utf-8", errors="replace")
    sid, tag = STATE_ID.search(text), STATE_TAG.search(text)
    return {
        "id": sid.group(1) if sid else None,
        "git_tag": tag.group(1) if tag else None,
    }


def system_status(target: Path) -> str:
    completed = git(
        target, "status", "--porcelain=v1", "--",
        "system", "research_record/STATE.yaml",
    )
    if completed.returncode:
        raise BootstrapError(completed.stderr.strip() or f"cannot inspect State files in {target}")
    return completed.stdout.strip()


def copy_project(source: Path, destination: Path) -> None:
    source, destination = source.resolve(), destination.resolve()

    def ignored(directory: str, names: list[str]) -> set[str]:
        relative = Path(directory).resolve().relative_to(source)
        if relative == Path("."):
            return {".git"}
        if relative == Path("research_record"):
            return {"runtime"}
        if relative.parts[:2] == ("research_record", "runtime"):
            return set(names)
        return set()

    shutil.copytree(source, destination, dirs_exist_ok=True, ignore=ignored)


def snapshot_memory(source: Path, destination: Path, *, include_meta: bool = True) -> None:
    for relative in MEMORY_FILES if include_meta else ADOPT_FILES:
        src = source / relative
        if src.is_file():
            dst = destination / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
    for relative in ADOPT_DIRS:
        src, dst = source / relative, destination / relative
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)


def memory_bytes(root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for relative in ADOPT_FILES:
        path = root / relative
        if path.is_file():
            result[relative] = path.read_bytes()
    for relative in ADOPT_DIRS:
        directory = root / relative
        if directory.is_dir():
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def adopt_memory(snapshot: Path, target: Path) -> None:
    for relative in ADOPT_FILES:
        src, dst = snapshot / relative, target / relative
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        elif dst.exists() or dst.is_symlink():
            dst.unlink()
    for relative in ADOPT_DIRS:
        src, dst = snapshot / relative, target / relative
        if dst.exists():
            shutil.rmtree(dst)
        if src.is_dir():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)


def add_worktree(repository: Path, source: Path, destination: Path, commit: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    completed = git(repository, "worktree", "add", "--detach", str(destination), commit)
    if completed.returncode:
        raise BootstrapError(
            completed.stderr.strip() or completed.stdout.strip()
            or f"cannot create Parallel worktree {destination}"
        )
    copy_project(source, destination)


def remove_worktree(repository: Path, workspace: Path) -> bool:
    return workspace.exists() and git(
        repository, "worktree", "remove", "--force", str(workspace)
    ).returncode == 0


def cleanup_worktrees(manifest: dict[str, Any], keep: set[str]) -> None:
    repository = Path(str(manifest["target"]))
    control_value = str(manifest.get("control_workspace") or "")
    if control_value:
        control = Path(control_value)
        if control.is_dir():
            remove_worktree(repository, control)
    for round_record in manifest.get("rounds_log", []):
        if not isinstance(round_record, dict):
            continue
        for branch in round_record.get("branches", []):
            if not isinstance(branch, dict) or not branch.get("workspace"):
                continue
            workspace = Path(str(branch["workspace"]))
            retained = branch.get("branch_id") in keep and workspace.is_dir()
            if workspace.is_dir() and not retained:
                remove_worktree(repository, workspace)
            branch["workspace_retained"] = bool(retained)
    git(repository, "worktree", "prune")


def environment(
    *,
    run_dir: Path,
    role: str,
    parallel_id: str,
    branch_id: str | None = None,
    context: Path | None = None,
) -> dict[str, str]:
    values = {
        "RESEARCH_AGENT_ROLE": role,
        "RESEARCH_AGENT_PARALLEL_MODE": "1",
        "RESEARCH_AGENT_PARALLEL_ID": parallel_id,
        "RESEARCH_AGENT_RUN_DIR": str(run_dir),
    }
    if branch_id:
        values["RESEARCH_AGENT_BRANCH_ID"] = branch_id
    if context:
        values["RESEARCH_AGENT_PARALLEL_CONTEXT"] = str(context)
    if role == "PARALLEL_REVIEWER":
        values["RESEARCH_AGENT_META_SESSION"] = "1"
    return values


def _normal_status(value: Any, exit_code: int) -> str:
    if exit_code:
        return "failed"
    if not isinstance(value, str):
        return "needs_human"
    value = value.strip().lower()
    if value in {"complete", "completed", "converged", "continue"}:
        return "completed"
    if value in {"failed", "error"}:
        return "failed"
    return "needs_human"


def execute_scientist_branch(
    *,
    invocation: Invocation,
    branch: BranchRecord,
    parallel_id: str,
    usage_dir: Path,
    cancel_event: threading.Event | None = None,
    runner: Any = run_invocation,
) -> BranchRecord:
    """Run one Parallel Scientist branch through the shared branch lifecycle."""
    usage_dir.mkdir(parents=True, exist_ok=True)
    log = Path(str(branch["log_path"]))
    try:
        code = runner(
            invocation,
            environment=environment(
                run_dir=usage_dir,
                role="SCIENTIST",
                parallel_id=parallel_id,
                branch_id=str(branch["branch_id"]),
                context=Path(str(branch["context_path"])),
            ),
            output_path=log,
            stream_output=False,
            cancel_event=cancel_event,
        )
    except (RuntimeError, OSError) as exc:
        code = 130 if cancel_event is not None and cancel_event.is_set() else 127
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as handle:
            handle.write(f"error: {exc}\n")

    workspace = Path(str(branch["workspace"]))
    result_path = Path(str(branch["scientist_result_path"]))
    payload = read_object(result_path) or {
        "schema_version": SCHEMA,
        "branch_id": branch["branch_id"],
        "status": "failed" if code else "needs_human",
        "summary": (
            f"Scientist exited with code {code} without a branch result."
            if code else "Scientist did not write the required branch result."
        ),
        "evidence": [],
    }
    if "kind" in branch:
        payload["kind"] = branch["kind"]
    if "primary_branch" in branch:
        payload["primary_branch"] = branch["primary_branch"]
    if "informed_by" in branch:
        payload["informed_by"] = branch["informed_by"]
    payload.update({
        "schema_version": SCHEMA,
        "branch_id": branch["branch_id"],
        "status": _normal_status(payload.get("status"), code),
        "exit_code": code,
        "candidate_commit": git_output(workspace, "rev-parse", "HEAD"),
        "system_state_dirty": bool(system_status(workspace)),
        "observed_at": utc_now(),
    })
    if payload.get("candidate_state") is None:
        payload["candidate_state"] = state_descriptor(workspace / "research_record/STATE.yaml")
    write_json(Path(str(branch["result_path"])), payload)
    snapshot_memory(workspace, Path(str(branch["memory_snapshot"])))
    branch["status"] = str(payload["status"])
    branch["exit_code"] = code
    branch["candidate_commit"] = str(payload["candidate_commit"])
    branch["system_state_dirty"] = bool(payload["system_state_dirty"])
    branch["summary"] = str(payload.get("summary", ""))
    return branch


def build_parallel_scientist_invocation(
    *,
    cli: str,
    target: Path,
    context_path: Path,
    result_path: Path,
    parallel_id: str,
    branch_id: str,
    round_number: int,
    model: str | None = None,
    effort: str | None = None,
) -> Invocation:
    startup_context = scientist_startup_context(
        target,
        coordination_label="PARALLEL_COORDINATION_INPUT",
        coordination_path=context_path,
    )
    prompt = (
        f"{NO_SKILL_FILE_READ} The launcher-provided Scientist runtime contract below defines this invocation; external Skill documentation is not runtime input.\n\n"
        "The launcher has injected the target files required for Scientist startup and the formal Parallel "
        "coordination input below. Treat these blocks as already loaded; do not open their source files merely "
        "to retrieve them.\n\n"
        f"{startup_context}\n\n"
        f"{RUNTIME_CONTEXT_PRECEDENCE}\n\n"
        f"{SCIENTIST_RUNTIME_RULES}\n"
        f"You are an independent Scientist replica for Parallel run {parallel_id}, "
        f"branch {branch_id}, round {round_number}, in isolated project {target}. "
        f"RESEARCH_AGENT_PARALLEL_CONTEXT={context_path} remains available as the "
        "on-disk coordination reference. Use the formal coordination input instead of "
        "RESEARCH_AGENT_BRIEF; it assigns only "
        "identity, ancestry, constraints, budget, and output paths. It does not assign "
        "a scientific question, hypothesis, experiment, or research direction. "
        "Independently reconstruct the research world and choose the most valuable scientific work yourself. "
        "Do not access sibling, parent, or original-target paths. "
        "Follow the project State ownership boundary: you may modify system/** but must not edit "
        "research_record/STATE.yaml or create state/* tags. If retained system/** changes survive evidence, "
        "commit only those system/** changes so the post-hoc Reviewer can inspect a stable implementation "
        "candidate; post-session META-style supervision owns any later State descriptor/tag creation. "
        "A diagnostic-only branch may leave the implementation unchanged. Preserve evidence and write the "
        "free-form branch report required by the runtime contract. "
        f"Write the required branch result to RESULT_PATH={result_path}. Do not launch another agent."
    )
    return get_adapter(cli).invoke(
        target=target, prompt=prompt, allow_edits=True, model=model, effort=effort
    )


def build_parallel_reviewer_invocation(
    *,
    cli: str,
    target: Path,
    manifest_path: Path,
    result_path: Path,
    parallel_id: str,
    round_number: int,
    keep: int,
    candidate_branches: list[str] | None = None,
    model: str | None = None,
    effort: str | None = None,
) -> Invocation:
    candidates = ", ".join(candidate_branches or []) or "none"
    startup_context = meta_startup_context(target)
    prompt = (
        f"{NO_SKILL_FILE_READ} The launcher-provided Parallel Reviewer runtime contract below defines this invocation; external Skill documentation is not runtime input.\n\n"
        "The launcher has injected the target files required for META-style review and the current Parallel "
        "manifest below. Treat these blocks as already loaded; do not open their source files merely to retrieve "
        "them.\n\n"
        f"{startup_context}\n\n"
        f"{injected_file('PARALLEL_MANIFEST', manifest_path)}\n\n"
        f"{RUNTIME_CONTEXT_PRECEDENCE}\n\n"
        f"{REVIEWER_RUNTIME_RULES}\n"
        f"You are the Parallel Reviewer for run {parallel_id}, round {round_number}, "
        "inside a disposable control worktree. Review only completed research; do not prescribe "
        "future scientific questions, hypotheses, experiments, model choices, or research directions. "
        "Do not launch another agent. "
        f"MANIFEST_PATH={manifest_path} remains the on-disk audit reference. Inspect each audit_dir and "
        "relevant pinned source/evaluator when validating the injected manifest. "
        "Audit candidate commits with git show/diff and branch result/log/memory from audit_dir. "
        "Count uncertainty reduction, falsified hypotheses, reusable knowledge, useful negative results, "
        "and improved or otherwise valuable implementations as research progress. Reject unsupported gains, "
        "leakage, unresolved dirty implementation boundaries, and weak evidence. Existing incumbents remain "
        "eligible beside new replicas. "
        f"Eligible branches: {candidates}. Select at most {keep}; empty is valid. "
        "Do not merge, promote, synthesize, edit branch research memory, edit branch system/**, or author "
        "STATE.yaml. Keep next_action process-level only: continue, stop, adopt, inspect, or request human "
        "input; do not use it to assign future scientific work. "
        f"Write schema_version 1 JSON with parallel_id, round, selected_branches, rejected, "
        f"summary, next_action to RESULT_PATH={result_path}."
    )
    return get_adapter(cli).invoke(
        target=target, prompt=prompt, allow_edits=True, model=model, effort=effort
    )


def refresh_control(repository: Path, source: Path, workspace: Path, commit: str) -> None:
    if not workspace.exists():
        add_worktree(repository, source, workspace, commit)
        return
    if git(workspace, "reset", "--hard", commit).returncode:
        raise BootstrapError("cannot reset Parallel control worktree")
    if git(workspace, "clean", "-fd").returncode:
        raise BootstrapError("cannot clean Parallel control worktree")
    runtime = workspace / "research_record/runtime"
    if runtime.exists():
        shutil.rmtree(runtime)
    for relative in MEMORY_FILES:
        path = workspace / relative
        if path.exists() or path.is_symlink():
            path.unlink()
    for relative in ADOPT_DIRS:
        path = workspace / relative
        if path.is_dir():
            shutil.rmtree(path)
    copy_project(source, workspace)


def prepare_control(
    repository: Path,
    source: Path,
    workspace: Path,
    parallel_dir: Path,
    manifest: dict[str, Any],
    commit: str,
) -> Path:
    refresh_control(repository, source, workspace, commit)
    control = workspace / "research_record/runtime/parallel-control"
    control.mkdir(parents=True, exist_ok=True)
    rounds: list[dict[str, Any]] = []
    for rr in manifest.get("rounds_log", []):
        branches = []
        for branch in rr.get("branches", []):
            local = control / "branches" / f"r{rr.get('round')}-{branch.get('branch_id')}"
            local.mkdir(parents=True, exist_ok=True)
            for key, name in (("result_path", "result.json"), ("log_path", "scientist.log")):
                src = Path(str(branch.get(key) or ""))
                if src.is_file():
                    shutil.copyfile(src, local / name)
            memory = Path(str(branch.get("memory_snapshot") or ""))
            if memory.is_dir():
                dst = local / "memory"
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(memory, dst)
            branches.append({
                key: branch.get(key) for key in (
                    "kind", "branch_id", "parent_branch", "primary_branch", "informed_by",
                    "round", "replica", "status", "summary", "base_commit", "base_state",
                    "candidate_commit", "candidate_state_id", "system_state_dirty",
                )
            } | {"audit_dir": str(local)})
        rounds.append({
            "round": rr.get("round"),
            "branches": branches,
            "selected_branches": rr.get("selected_branches", []),
            "review": rr.get("review"),
        })
    write_json(control / "manifest.json", {
        "schema_version": SCHEMA,
        "parallel_id": manifest["parallel_id"],
        "kind": "parallel-control",
        "base_commit": manifest["base_commit"],
        "base_state": manifest.get("base_state"),
        "rounds": manifest["rounds"],
        "branches": manifest["branches"],
        "keep": manifest["keep"],
        "synthesis_enabled": bool(manifest.get("synthesis_enabled")),
        "rounds_log": rounds,
    })
    for name in ("aggregate.json", "aggregate.md"):
        src = parallel_dir / name
        if src.is_file():
            shutil.copyfile(src, control / name)
    return control


def usage_report(parallel_dir: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for path in sorted(
        set(parallel_dir.rglob("model-usage.json")) | set(parallel_dir.rglob("*.usage.json"))
    ):
        payload = read_object(path)
        models = payload.get("models") if payload else None
        if isinstance(models, list):
            entries.extend(x for x in models if isinstance(x, dict))
    return model_usage_report(entries)


def validate_state_candidate(
    target: Path,
    manifest: dict[str, Any],
    branch: BranchRecord,
    candidate_commit: str,
) -> CreateStateResult:
    root = str(manifest["base_commit"])
    if git(target, "merge-base", "--is-ancestor", root, candidate_commit).returncode:
        raise BootstrapError("Parallel candidate is not a descendant of the recorded base")
    changed = git_output(target, "diff", "--name-only", f"{root}..{candidate_commit}").splitlines()
    invalid = [
        p for p in changed
        if p and p != "research_record/STATE.yaml" and not p.startswith("system/")
    ]
    if invalid:
        raise BootstrapError(
            "Parallel branch contains changes outside State: " + ", ".join(invalid[:8])
        )
    if "research_record/STATE.yaml" not in changed or not any(p.startswith("system/") for p in changed):
        raise BootstrapError(
            "Legacy parallel-promote cannot crystallize a Scientist-authored implementation into a State. "
            "Post-session META supervision must write STATE.yaml first."
        )

    expected = str(branch.get("candidate_state_id") or "")
    try:
        validated = validate_state_commit(target, expected, candidate_commit)
        descriptor = git_output(target, "show", f"{candidate_commit}:research_record/STATE.yaml")
        parent = str((branch.get("base_state") or {}).get("id") or "")
        match = DERIVED.search(descriptor)
        derived = match.group(1) if match else None
        if parent and derived != parent:
            raise ValueError(f"derived_from must be {parent!r}, got {derived!r}")
    except ValueError as exc:
        raise BootstrapError(f"invalid Parallel State candidate: {exc}") from exc
    if not git(target, "show-ref", "--verify", "--quiet", f"refs/tags/{validated.git_tag}").returncode:
        raise BootstrapError(
            f"candidate State tag already exists before promotion: {validated.git_tag}"
        )
    return validated


def _branch_index(manifest: dict[str, Any]) -> dict[str, BranchRecord]:
    result: dict[str, BranchRecord] = {}
    for rr in manifest.get("rounds_log", []):
        if not isinstance(rr, dict):
            continue
        for raw in rr.get("branches", []):
            if not isinstance(raw, dict) or not isinstance(raw.get("branch_id"), str):
                continue
            result[str(raw["branch_id"])] = raw  # type: ignore[assignment]
    return result


def _accepted_chain(manifest: dict[str, Any], branch_id: str) -> list[BranchRecord]:
    branches = _branch_index(manifest)
    chain: list[BranchRecord] = []
    seen: set[str] = set()
    current = branch_id
    while current != "root":
        if current in seen:
            raise BootstrapError("Parallel branch ancestry contains a cycle")
        seen.add(current)
        branch = branches.get(current)
        if branch is None:
            raise BootstrapError(f"Parallel branch ancestry is missing {current!r}")
        chain.append(branch)
        parent = branch.get("parent_branch")
        if not isinstance(parent, str) or not parent:
            raise BootstrapError(f"Parallel branch {current!r} has no parent ancestry")
        current = parent
    chain.reverse()
    return chain


def _promotion_states(
    target: Path,
    manifest: dict[str, Any],
    branch_id: str,
) -> tuple[list[CreateStateResult], str]:
    root = str(manifest["base_commit"])
    previous_commit = root
    states: list[CreateStateResult] = []
    for branch in _accepted_chain(manifest, branch_id):
        base_commit = str(branch.get("base_commit") or "")
        candidate_commit = str(branch.get("candidate_commit") or "")
        if not base_commit or not candidate_commit:
            raise BootstrapError("accepted Parallel ancestry is missing commit metadata")
        if base_commit != previous_commit:
            raise BootstrapError(
                f"Parallel ancestry commit mismatch: expected base {previous_commit}, got {base_commit}"
            )
        if candidate_commit != base_commit:
            states.append(validate_state_candidate(target, manifest, branch, candidate_commit))
        previous_commit = candidate_commit
    return states, previous_commit


def _rollback_promotion(
    *,
    target: Path,
    root: str,
    final_commit: str,
    base_memory: Path,
    created_tags: list[str],
    manifest_path: Path,
    manifest_before: bytes,
) -> list[str]:
    errors: list[str] = []
    for tag in reversed(created_tags):
        deleted = git(target, "tag", "-d", tag)
        if deleted.returncode:
            errors.append(deleted.stderr.strip() or f"could not remove rollback tag {tag}")
    current = git_output(target, "rev-parse", "HEAD")
    if current != root:
        moved = git(target, "update-ref", "HEAD", root, final_commit)
        if moved.returncode:
            errors.append(moved.stderr.strip() or "could not restore target HEAD")
        restored = git(
            target,
            "restore",
            "--source",
            root,
            "--staged",
            "--worktree",
            "--",
            "system",
            "research_record/STATE.yaml",
        )
        if restored.returncode:
            errors.append(restored.stderr.strip() or "could not restore State-controlled files")
    try:
        adopt_memory(base_memory, target)
    except OSError as exc:
        errors.append(f"could not restore research memory: {exc}")
    try:
        manifest_path.write_bytes(manifest_before)
    except OSError as exc:
        errors.append(f"could not restore Parallel manifest: {exc}")
    return errors


def promote_selected(target: Path, parallel_dir: Path, branch_id: str) -> dict[str, Any]:
    manifest_path = parallel_dir / "manifest.json"
    manifest = read_object(manifest_path)
    if manifest is None or manifest.get("kind") != "parallel":
        raise BootstrapError(f"not a Parallel runtime directory: {parallel_dir}")
    if manifest.get("target") != str(target):
        raise BootstrapError("Parallel runtime belongs to a different target")
    if system_status(target):
        raise BootstrapError("target State boundary must be clean before promotion")
    root = str(manifest.get("base_commit") or "")
    if git_output(target, "rev-parse", "HEAD") != root:
        raise BootstrapError("target HEAD moved since Parallel started")

    base_memory = Path(str(manifest.get("base_memory_snapshot") or ""))
    if not base_memory.is_dir() or memory_bytes(target) != memory_bytes(base_memory):
        raise BootstrapError(
            "target research memory changed since Parallel started; "
            "start a new Parallel run rather than overwriting newer research"
        )
    result = read_object(parallel_dir / "result.json")
    selected = result.get("selected_branches", []) if result else []
    if not isinstance(selected, list) or branch_id not in selected:
        raise BootstrapError(f"branch {branch_id!r} was not selected by the Parallel Reviewer")

    branches = _branch_index(manifest)
    branch = branches.get(branch_id)
    if branch is None:
        raise BootstrapError(f"Parallel branch does not exist: {branch_id}")
    workspace = Path(str(branch.get("workspace") or ""))
    memory = Path(str(branch.get("memory_snapshot") or ""))
    if not workspace.is_dir() or not memory.is_dir():
        raise BootstrapError("selected Parallel branch artifacts are missing")
    if branch.get("system_state_dirty"):
        raise BootstrapError("selected Parallel branch has an uncommitted implementation/State boundary")

    commit = git_output(workspace, "rev-parse", "HEAD")
    if branch.get("candidate_commit") and commit != branch["candidate_commit"]:
        raise BootstrapError("Parallel branch changed after review")
    states, final_commit = _promotion_states(target, manifest, branch_id)
    if commit != final_commit:
        raise BootstrapError("selected Parallel workspace does not match recorded accepted ancestry")

    manifest_before = manifest_path.read_bytes()
    created_tags: list[str] = []
    try:
        if final_commit != root:
            merged = git(target, "merge", "--ff-only", final_commit)
            if merged.returncode:
                raise BootstrapError(
                    merged.stderr.strip() or "cannot fast-forward accepted Parallel State ancestry"
                )
        created: list[CreateStateResult] = []
        for state in states:
            try:
                tagged = create_state_at_commit(target, state.state_id, state.commit)
            except ValueError as exc:
                raise BootstrapError(f"canonical State creation failed: {exc}") from exc
            created.append(tagged)
            created_tags.append(tagged.git_tag)

        adopt_memory(memory, target)
        final_state = created[-1] if created else None
        manifest.update({
            "promoted_branch": branch_id,
            "promoted_commit": final_commit if final_commit != root else None,
            "promoted_state": final_state.state_id if final_state else None,
            "promoted_states": [state.state_id for state in created],
            "research_memory_adopted": True,
            "status": "promoted",
        })
        write_json(manifest_path, manifest)
    except KeyboardInterrupt as exc:
        rollback = _rollback_promotion(
            target=target,
            root=root,
            final_commit=final_commit,
            base_memory=base_memory,
            created_tags=created_tags,
            manifest_path=manifest_path,
            manifest_before=manifest_before,
        )
        if rollback:
            raise BootstrapError(
                "Parallel promotion interrupted and rollback was incomplete: " + "; ".join(rollback)
            ) from exc
        raise
    except (BootstrapError, OSError, ValueError) as exc:
        rollback = _rollback_promotion(
            target=target,
            root=root,
            final_commit=final_commit,
            base_memory=base_memory,
            created_tags=created_tags,
            manifest_path=manifest_path,
            manifest_before=manifest_before,
        )
        detail = f"; rollback issues: {'; '.join(rollback)}" if rollback else ""
        if isinstance(exc, BootstrapError):
            raise BootstrapError(f"{exc}{detail}") from exc
        raise BootstrapError(f"Parallel promotion failed: {exc}{detail}") from exc

    cleanup_worktrees(manifest, set())
    try:
        write_json(manifest_path, manifest)
    except OSError:
        pass

    final_state = states[-1] if states else None
    response: dict[str, Any] = {
        "parallel_id": manifest["parallel_id"],
        "branch_id": branch_id,
        "status": "promoted",
        "research_memory_adopted": True,
        "state_promoted": bool(states),
        "states_promoted": [state.state_id for state in states],
        "target": str(target),
    }
    if final_state:
        response.update(
            commit=final_commit,
            state_id=final_state.state_id,
            git_tag=final_state.git_tag,
        )
    return response
