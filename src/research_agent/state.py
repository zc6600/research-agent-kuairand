from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

STATE_FILE = "research_record/STATE.yaml"
SYSTEM_ROOT = "system"
REPORT_ROOT = PurePosixPath("research_record/reports")
_STATE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class MaterializeResult:
    state_id: str
    git_tag: str
    source_commit: str
    scientist_report: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class CreateStateResult:
    state_id: str
    git_tag: str
    commit: str


def _git(target: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(target), *args], input=input_bytes,
        capture_output=True, check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"git {' '.join(args)} failed: {detail or result.returncode}")
    return result.stdout


def _root(target: Path) -> Path:
    target = target.expanduser().resolve()
    if not target.is_dir():
        raise ValueError(f"target project does not exist: {target}")
    root = Path(_git(target, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if root != target:
        raise ValueError(f"State operations require the target to be its own Git root: target={target}, git_root={root}")
    return target


def _paths(payload: bytes) -> tuple[str, ...]:
    return tuple(x.decode("utf-8", errors="surrogateescape") for x in payload.split(b"\0") if x)


def _state_id(value: str) -> str:
    value = value.removeprefix("state/")
    if not _STATE_ID.fullmatch(value):
        raise ValueError(f"invalid State id: {value!r}")
    return value


def _scientist_report(text: str) -> str:
    found = re.search(r"(?m)^scientist_report:\s*([^\s#]+)\s*$", text)
    if found is None:
        raise ValueError("STATE.yaml must contain scientist_report")
    value = found.group(1)
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"invalid scientist_report path: {value!r}")
    if path.parent != REPORT_ROOT or path.suffix.lower() != ".md" or not path.name:
        raise ValueError(
            "scientist_report must be a project-relative Markdown path directly under research_record/reports/"
        )
    return path.as_posix()


def _require_scientist_report(target: Path, report: str, *, state_label: str) -> None:
    if not (target / report).is_file():
        raise ValueError(
            f"{state_label} provenance is incomplete: Scientist report is missing: {report}"
        )


def _validate_descriptor(text: str, state_id: str, tag: str) -> str:
    found_id = re.search(r"(?m)^id:\s*([^\s#]+)\s*$", text)
    found_tag = re.search(r"(?m)^git_tag:\s*([^\s#]+)\s*$", text)
    if found_id is None or found_id.group(1) != state_id:
        raise ValueError(f"expected STATE.yaml id {state_id!r}")
    if found_tag is None or found_tag.group(1) != tag:
        raise ValueError(f"expected STATE.yaml git_tag {tag!r}")
    return _scientist_report(text)


def _tag_descriptor(target: Path, state_id: str, tag: str) -> tuple[str, str]:
    text = _git(target, "show", f"{tag}:{STATE_FILE}").decode("utf-8", errors="replace")
    report = _validate_descriptor(text, state_id, tag)
    return text, report


def _current_state(target: Path) -> tuple[str, str]:
    try:
        text = (target / STATE_FILE).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"current State descriptor is unreadable: {exc}") from exc
    found_id = re.search(r"(?m)^id:\s*([^\s#]+)\s*$", text)
    found_tag = re.search(r"(?m)^git_tag:\s*([^\s#]+)\s*$", text)
    if found_id is None or found_tag is None:
        raise ValueError("current STATE.yaml must contain id and git_tag")
    state_id = _state_id(found_id.group(1))
    tag = found_tag.group(1)
    if tag != f"state/{state_id}":
        raise ValueError(f"current STATE.yaml id/tag mismatch: {state_id!r} vs {tag!r}")
    tagged, _ = _tag_descriptor(target, state_id, tag)
    if text != tagged:
        raise ValueError(f"current STATE.yaml differs from immutable {tag}; historical State metadata cannot be edited in place")
    return state_id, tag


def _system_paths(target: Path, ref: str) -> set[str]:
    return set(_paths(_git(target, "ls-tree", "-r", "--name-only", "-z", ref, "--", SYSTEM_ROOT)))


def _require_system_state(target: Path, tag: str) -> set[str]:
    paths = _system_paths(target, tag)
    if not paths:
        raise ValueError(f"State {tag} has no tracked system/ object and cannot be materialized")
    return paths


def _dirty_system(target: Path, current_tag: str) -> tuple[str, ...]:
    dirty = set(_paths(_git(target, "diff", "--name-only", "-z", "--no-renames", current_tag, "--", SYSTEM_ROOT)))
    dirty.update(_paths(_git(target, "diff", "--cached", "--name-only", "-z", "--", SYSTEM_ROOT)))
    dirty.update(_paths(_git(target, "ls-files", "--others", "--exclude-standard", "-z", "--", SYSTEM_ROOT)))
    return tuple(sorted(dirty))


def _system_matches_state(target: Path, tag: str) -> bool:
    """Return whether the worktree system/ exactly matches one immutable State."""
    with tempfile.TemporaryDirectory(prefix="research-agent-state-index-") as temporary:
        environment = os.environ.copy()
        environment["GIT_INDEX_FILE"] = str(Path(temporary) / "index")

        read_tree = subprocess.run(
            ["git", "-C", str(target), "read-tree", tag],
            env=environment, capture_output=True, check=False,
        )
        if read_tree.returncode:
            detail = read_tree.stderr.decode("utf-8", errors="replace").strip()
            raise ValueError(f"cannot compare materialized State {tag}: {detail or read_tree.returncode}")

        subprocess.run(
            ["git", "-C", str(target), "update-index", "--refresh"],
            env=environment, capture_output=True, check=False,
        )
        changed = subprocess.run(
            ["git", "-C", str(target), "diff-files", "--name-only", "-z", "--", SYSTEM_ROOT],
            env=environment, capture_output=True, check=False,
        )
        if changed.returncode:
            detail = changed.stderr.decode("utf-8", errors="replace").strip()
            raise ValueError(f"cannot compare materialized State {tag}: {detail or changed.returncode}")
        untracked = subprocess.run(
            ["git", "-C", str(target), "ls-files", "--others", "--exclude-standard", "-z", "--", SYSTEM_ROOT],
            env=environment, capture_output=True, check=False,
        )
        if untracked.returncode:
            detail = untracked.stderr.decode("utf-8", errors="replace").strip()
            raise ValueError(f"cannot inspect materialized State {tag}: {detail or untracked.returncode}")
        return not changed.stdout and not untracked.stdout


def validate_state_commit(target: Path, state: str, commit: str) -> CreateStateResult:
    """Validate one committed reusable State without creating its immutable tag."""
    target = _root(target)
    state_id = _state_id(state)
    tag = f"state/{state_id}"
    resolved = _git(target, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    descriptor = _git(target, "show", f"{resolved}:{STATE_FILE}").decode(
        "utf-8", errors="replace"
    )
    _validate_descriptor(descriptor, state_id, tag)
    if not _system_paths(target, resolved):
        raise ValueError("State commit must contain at least one tracked system/ object")
    return CreateStateResult(state_id, tag, resolved)


def create_state_at_commit(target: Path, state: str, commit: str) -> CreateStateResult:
    """Create the canonical immutable State tag for an already-validated commit."""
    target = _root(target)
    validated = validate_state_commit(target, state, commit)
    if subprocess.run(
        ["git", "-C", str(target), "show-ref", "--verify", "--quiet", f"refs/tags/{validated.git_tag}"],
        check=False,
    ).returncode == 0:
        raise ValueError(f"State tag already exists and is immutable: {validated.git_tag}")
    _git(
        target,
        "tag",
        "--annotate",
        validated.git_tag,
        "--message",
        f"Research Agent State {validated.state_id}",
        validated.commit,
    )
    return validated


def materialize_state(target: Path, state: str) -> MaterializeResult:
    target = _root(target)
    _, current_tag = _current_state(target)
    current_paths = _require_system_state(target, current_tag)

    state_id = _state_id(state)
    tag = f"state/{state_id}"
    commit = _git(target, "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}").decode().strip()
    _, scientist_report = _tag_descriptor(target, state_id, tag)
    _require_scientist_report(target, scientist_report, state_label=f"State {tag}")
    target_paths = _require_system_state(target, tag)

    dirty = _dirty_system(target, current_tag)
    if dirty and not _system_matches_state(target, current_tag):
        joined = ", ".join(dirty[:8]) + (" ..." if len(dirty) > 8 else "")
        raise ValueError(f"refusing to materialize over uncommitted system changes: {joined}")

    restore = tuple(sorted(target_paths))
    remove = tuple(sorted(current_paths - target_paths))
    if restore:
        payload = b"\0".join(x.encode("utf-8", errors="surrogateescape") for x in restore) + b"\0"
        _git(target, "--literal-pathspecs", "restore", "--source", tag, "--worktree",
             "--pathspec-from-file=-", "--pathspec-file-nul", input_bytes=payload)
    for path in remove:
        candidate = target / path
        if candidate.is_file() or candidate.is_symlink():
            candidate.unlink()
    _git(target, "restore", "--source", tag, "--worktree", "--", STATE_FILE)
    touched = tuple(sorted(set(restore) | set(remove) | {STATE_FILE}))
    return MaterializeResult(state_id, tag, commit, scientist_report, touched)


def create_state(target: Path, state: str) -> CreateStateResult:
    target = _root(target)
    state_id = _state_id(state)
    tag = f"state/{state_id}"
    try:
        descriptor = (target / STATE_FILE).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"State descriptor is unreadable: {exc}") from exc
    scientist_report = _validate_descriptor(descriptor, state_id, tag)
    _require_scientist_report(target, scientist_report, state_label=f"State {tag}")
    if subprocess.run(
        ["git", "-C", str(target), "show-ref", "--verify", "--quiet", f"refs/tags/{tag}"],
        check=False,
    ).returncode == 0:
        raise ValueError(f"State tag already exists and is immutable: {tag}")

    dirty = _git(target, "status", "--porcelain", "--", SYSTEM_ROOT, STATE_FILE).decode(
        "utf-8", errors="replace"
    ).strip()
    if dirty:
        raise ValueError(f"system object and META-authored State descriptor must be fully committed before creating a State tag: {dirty}")
    commit = _git(target, "rev-parse", "HEAD").decode().strip()
    return create_state_at_commit(target, state_id, commit)


def push_state(target: Path, state: str, *, remote: str) -> str:
    target = _root(target)
    state_id = _state_id(state)
    tag = f"state/{state_id}"
    _, scientist_report = _tag_descriptor(target, state_id, tag)
    _require_scientist_report(target, scientist_report, state_label=f"State {tag}")
    _require_system_state(target, tag)
    _git(target, "push", remote, f"refs/tags/{tag}:refs/tags/{tag}")
    return tag


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="research-agent state")
    subs = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("materialize", "Reuse a historical State without rewinding research memory"),
        ("create", "Create the immutable tag for the current committed META-described State"),
        ("push", "Push exactly one State tag to a configured Git remote"),
    ):
        command = subs.add_parser(name, help=help_text)
        command.add_argument("state", help="State id such as S006 or tag state/S006")
        command.add_argument("--target", type=Path, required=True)
        if name == "push":
            command.add_argument("--remote", default="origin")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "materialize":
            result = materialize_state(args.target, args.state)
            print(json.dumps({
                "state_id": result.state_id,
                "git_tag": result.git_tag,
                "source_commit": result.source_commit,
                "scientist_report": result.scientist_report,
                "materialized_paths": list(result.paths),
            }, ensure_ascii=False))
        elif args.command == "create":
            created = create_state(args.target, args.state)
            print(json.dumps({"state_id": created.state_id, "git_tag": created.git_tag, "commit": created.commit}, ensure_ascii=False))
        else:
            print(json.dumps({"git_tag": push_state(args.target, args.state, remote=args.remote), "remote": args.remote}, ensure_ascii=False))
        return 0
    except ValueError as exc:
        raise SystemExit(f"error: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
