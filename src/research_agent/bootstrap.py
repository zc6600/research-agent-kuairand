from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class BootstrapError(RuntimeError):
    """Raised when a target cannot be initialized safely."""


@dataclass(frozen=True)
class BootstrapResult:
    target: Path
    created_record: bool
    agents_action: str
    claude_action: str


RECORD_VERSION = "research-agent-record-v5"
REQUIRED_RECORD_FILES = (
    "SYSTEM_CONTRACT.md",
    "RESEARCH_METHOD.md",
    "SKILL.md",
    "VERSION",
    "RESEARCH_BRIEF.md",
    "RESEARCH_RECORD.yaml",
    "EXPLORE.md",
    "OPTIMIZE.md",
    "ENGINEERING.md",
    "KNOWLEDGE.md",
    "RESEARCH_INTUITION.md",
    "DO_BETTER.md",
)


def _run_git(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(target), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def ensure_target_git_root(target: Path, *, create_if_missing: bool = False) -> Path:
    target = target.expanduser().resolve()
    if not target.is_dir():
        raise BootstrapError(f"target project does not exist: {target}")
    resolved = _run_git(target, "rev-parse", "--show-toplevel")
    if resolved.returncode == 0:
        git_root = Path(resolved.stdout.strip()).resolve()
        if git_root == target:
            return target
        if not create_if_missing:
            raise BootstrapError(f"target must be its own Git root: target={target}, enclosing_git_root={git_root}")
        ignored = subprocess.run(
            ["git", "-C", str(git_root), "check-ignore", "--quiet", "--", str(target)],
            check=False,
        )
        if ignored.returncode != 0:
            raise BootstrapError(f"refusing to create a nested Git repository in a tracked enclosing repository: {git_root}")
    elif not create_if_missing:
        raise BootstrapError(f"target is not a Git repository; initialize an independent target Git root before research: {target}")

    initialized = _run_git(target, "init", "-b", "main")
    if initialized.returncode != 0:
        initialized = _run_git(target, "init")
    if initialized.returncode != 0:
        raise BootstrapError(f"failed to initialize target Git repository: {initialized.stderr.strip() or target}")
    return target


def _reject_unrelated_staged_files_on_unborn_repo(target: Path) -> None:
    if _run_git(target, "rev-parse", "--git-dir").returncode != 0:
        return
    if _run_git(target, "rev-parse", "--verify", "HEAD").returncode == 0:
        return
    staged = _run_git(target, "diff", "--cached", "--name-only")
    if staged.returncode != 0:
        raise BootstrapError(staged.stderr.strip() or "cannot inspect staged files in target Git repository")
    allowed = {"task.md", "PERSONAL.md", ".gitignore", "AGENTS.md", "CLAUDE.md"}
    unrelated = [
        path for path in staged.stdout.splitlines()
        if path not in allowed and not path.startswith("research_record/")
    ]
    if unrelated:
        detail = ", ".join(unrelated[:8]) + (" ..." if len(unrelated) > 8 else "")
        raise BootstrapError(
            "refusing to create the initial research-agent commit while unrelated files are staged: " + detail
        )


def copy_project_inputs(target: Path, *, task_source: Path, personal_source: Path) -> None:
    sources = {"task.md": task_source, "PERSONAL.md": personal_source}
    missing = [name for name, source in sources.items() if not source.expanduser().is_file()]
    if missing:
        raise BootstrapError(f"required input file does not exist: {', '.join(missing)}")
    target = target.expanduser().resolve()
    for name, source in sources.items():
        destination = target / name
        if destination.exists():
            raise BootstrapError(f"target already contains {name}; refusing to overwrite: {destination}")
        shutil.copyfile(source.expanduser().resolve(), destination)


def require_supported_record(target: Path) -> None:
    record = target / "research_record"
    if not record.is_dir():
        raise BootstrapError(
            f"target is not initialized for research-agent: missing {record}. "
            "Run research-agent init first."
        )
    version_path = record / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else "unversioned"
    if version != RECORD_VERSION:
        raise BootstrapError(
            f"target research record is {version!r}; expected {RECORD_VERSION!r}. "
            "Initialize a clean project with the current research-agent release."
        )
    required = tuple(record / name for name in REQUIRED_RECORD_FILES)
    missing = [str(path.relative_to(target)) for path in required if not path.is_file()]
    if missing:
        raise BootstrapError(
            f"target research record is an incomplete {RECORD_VERSION!r}; missing: {', '.join(missing)}. "
            "Initialize a clean project with the current research-agent release."
        )


def prepare_target(*, target: Path | None, new_target: Path | None) -> tuple[Path, bool]:
    if (target is None) == (new_target is None):
        raise BootstrapError("provide exactly one of --target or --new")
    if target is not None:
        resolved = target.expanduser().resolve()
        if not resolved.is_dir():
            raise BootstrapError(f"target project does not exist: {resolved}")
        return resolved, False
    assert new_target is not None
    requested = new_target.expanduser().resolve()
    if requested.exists():
        if not requested.is_dir():
            raise BootstrapError(f"new target exists and is not a directory: {requested}")
        if any(requested.iterdir()):
            raise BootstrapError(f"new target directory is not empty: {requested}")
        return requested, False
    requested.mkdir(parents=True)
    return requested, True


def initialize_project(target: Path, template_root: Path) -> BootstrapResult:
    target = target.expanduser().resolve()
    template_root = template_root.resolve()
    if not target.is_dir():
        raise BootstrapError(f"target project does not exist: {target}")
    missing = [name for name in ("task.md", "PERSONAL.md") if not (target / name).is_file()]
    if missing:
        raise BootstrapError(
            f"write and verify {', '.join(missing)} before initialization; the initializer does not invent task or machine facts"
        )
    _reject_unrelated_staged_files_on_unborn_repo(target)

    record_source = template_root / "research_record"
    ignore_source = template_root / ".gitignore"
    record_target = target / "research_record"
    if not record_source.is_dir():
        raise BootstrapError(f"research-record template is missing: {record_source}")
    missing_record_files = [name for name in REQUIRED_RECORD_FILES if not (record_source / name).is_file()]
    if missing_record_files:
        raise BootstrapError(f"record template is incomplete; missing: {', '.join(missing_record_files)}")
    template_version = (record_source / "VERSION").read_text(encoding="utf-8").strip()
    if template_version != RECORD_VERSION:
        raise BootstrapError(f"record template version is {template_version!r}; expected {RECORD_VERSION!r}")
    if (record_source / "SYSTEM_SCOPE.json").exists():
        raise BootstrapError("current record template must not contain SYSTEM_SCOPE.json")
    if not ignore_source.is_file():
        raise BootstrapError(f"gitignore template is missing: {ignore_source}")
    if record_target.exists():
        raise BootstrapError(f"target already contains research_record; initialize a clean project instead: {record_target}")
    shutil.copytree(record_source, record_target)

    ignore_path = target / ".gitignore"
    ignore_block = ignore_source.read_text(encoding="utf-8").rstrip()
    ignore_marker = "# BEGIN research-agent generated files"
    if ignore_path.exists():
        current = ignore_path.read_text(encoding="utf-8")
        if ignore_marker not in current:
            separator = "" if current.endswith("\n\n") else "\n" if current.endswith("\n") else "\n\n"
            ignore_path.write_text(current + separator + ignore_block + "\n", encoding="utf-8")
    else:
        ignore_path.write_text(ignore_block + "\n", encoding="utf-8")

    agents_path = target / "AGENTS.md"
    block = (template_root / "AGENTS.block.md").read_text(encoding="utf-8").rstrip()
    begin_marker = "<!-- BEGIN research-agent project contract -->"
    if agents_path.exists():
        current = agents_path.read_text(encoding="utf-8")
        if begin_marker in current:
            agents_action = "unchanged"
        else:
            separator = "" if current.endswith("\n\n") else "\n" if current.endswith("\n") else "\n\n"
            agents_path.write_text(current + separator + block + "\n", encoding="utf-8")
            agents_action = "appended"
    else:
        agents_path.write_text("# Repository Guidelines\n\n" + block + "\n", encoding="utf-8")
        agents_action = "created"

    claude_path = target / "CLAUDE.md"
    if claude_path.exists():
        claude_action = "unchanged"
    else:
        shutil.copyfile(template_root / "CLAUDE.md", claude_path)
        claude_action = "created"
    return BootstrapResult(target, True, agents_action, claude_action)
