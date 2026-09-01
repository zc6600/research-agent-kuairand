from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


WORKSPACE_DIR = Path(__file__).resolve().parents[2]
RESEARCH_AGENT = WORKSPACE_DIR / "scripts" / "research-agent"
DATA_PREPARER = Path(__file__).resolve().with_name("data.py")
GENERIC_OPTIMIZE = WORKSPACE_DIR / "assets" / "project-template" / "research_record" / "OPTIMIZE.md"
CORE_SRC = WORKSPACE_DIR / "src"
if str(CORE_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_SRC))

from research_agent.bootstrap import (  # noqa: E402
    BootstrapError,
    ensure_target_git_root,
    require_supported_record,
)
from research_agent.runners import supported_runners  # noqa: E402


STARTER_KIT_FILES = (
    "README.md",
    "ablation_features.py",
    "baseline.py",
    "baseline_scores.json",
    "data.py",
    "evaluate.py",
    "submit.py",
)
EFFORT_LEVELS = ("low", "medium", "high", "max")
PROJECT_ID_PATTERN = re.compile(r"^p(?P<number>[0-9]{3})-")
PROJECT_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def env_path(name: str, default: Path) -> Path:
    return Path(os.environ.get(name, str(default))).expanduser()


def _validate_project_slug(slug: str) -> None:
    if not PROJECT_SLUG_PATTERN.fullmatch(slug):
        raise ValueError(f"project slug must be lowercase kebab-case: {slug}")


def next_project_target(workspace: Path, slug: str) -> Path:
    _validate_project_slug(slug)
    workspace = workspace.expanduser().resolve()
    max_id = 0
    for scan_root in (workspace / "projects", workspace / "archive"):
        if not scan_root.is_dir():
            continue
        for entry in scan_root.rglob("*"):
            if entry.is_dir() and (match := PROJECT_ID_PATTERN.match(entry.name)):
                max_id = max(max_id, int(match.group("number")))
    return workspace / "projects" / f"p{max_id + 1:03d}-{slug}"


def latest_project_target(workspace: Path, slug: str) -> Path | None:
    _validate_project_slug(slug)
    projects = workspace.expanduser().resolve() / "projects"
    if not projects.is_dir():
        return None
    candidates: list[tuple[int, Path]] = []
    for entry in projects.iterdir():
        if not entry.is_dir() or not (match := PROJECT_ID_PATTERN.match(entry.name)):
            continue
        number = int(match.group("number"))
        if entry.name == f"p{number:03d}-{slug}":
            candidates.append((number, entry))
    return max(candidates, default=(0, None), key=lambda item: item[0])[1]


def competition_target(command: str) -> Path:
    explicit = os.environ.get("RESEARCH_AGENT_COMPETITION_TARGET")
    if explicit:
        return Path(explicit).expanduser()
    if command == "setup":
        return next_project_target(WORKSPACE_DIR, "kuairand-pure")
    return latest_project_target(WORKSPACE_DIR, "kuairand-pure") or next_project_target(
        WORKSPACE_DIR, "kuairand-pure"
    )


def run_checked(command: list[str], *, quiet: bool = False) -> None:
    kwargs: dict[str, object] = {"check": True}
    if quiet:
        kwargs["stdout"] = subprocess.DEVNULL
    subprocess.run(command, **kwargs)


def validate_starter_kit(kit_dir: Path) -> None:
    if not kit_dir.is_dir():
        raise ValueError(f"starter kit path is not a directory: {kit_dir}")
    for required in STARTER_KIT_FILES:
        if not (kit_dir / required).is_file():
            raise ValueError(f"starter kit is missing required file: {kit_dir / required}")


def safe_starter_member(name: str) -> bool:
    path = Path(name)
    if path.is_absolute() or "\\" in name or ".." in path.parts:
        return False
    parts = path.parts
    return bool(parts) and parts[0] == "kuairand-starter-kit"


def provision_starter_kit(target: Path, archive: Path, expected_sha256: str, *, output_mode: str) -> None:
    destination = target / "starter_kit"
    if destination.exists():
        validate_starter_kit(destination)
        return
    if not archive.is_file():
        raise ValueError(f"starter-kit archive does not exist: {archive}")

    actual_sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"starter-kit SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )

    with zipfile.ZipFile(archive) as starter_zip:
        for entry in starter_zip.namelist():
            if entry and not safe_starter_member(entry):
                raise ValueError(f"unsafe or unexpected path in starter-kit archive: {entry}")
        with tempfile.TemporaryDirectory(prefix=".starter-kit.", dir=target) as temporary:
            temporary_path = Path(temporary)
            starter_zip.extractall(temporary_path)
            unpacked = temporary_path / "kuairand-starter-kit"
            validate_starter_kit(unpacked)
            shutil.move(str(unpacked), str(destination))

    if output_mode == "normal":
        print(f"Provisioned starter kit: {destination}")


def seed_competition_optimize(target: Path, optimize_source: Path) -> None:
    if not optimize_source.is_file():
        raise ValueError(f"competition optimization file does not exist: {optimize_source}")
    destination = target / "research_record" / "OPTIMIZE.md"
    source_text = optimize_source.read_text(encoding="utf-8")
    if destination.is_file():
        current = destination.read_text(encoding="utf-8")
        generic = GENERIC_OPTIMIZE.read_text(encoding="utf-8") if GENERIC_OPTIMIZE.is_file() else None
        if current.strip() and current != generic:
            return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(source_text, encoding="utf-8")


def exclude_local_competition_data(target: Path) -> None:
    exclude_file = target / ".git" / "info" / "exclude"
    existing = exclude_file.read_text(encoding="utf-8") if exclude_file.exists() else ""
    if "/competition_data" not in existing.splitlines():
        exclude_file.parent.mkdir(parents=True, exist_ok=True)
        with exclude_file.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write("/competition_data\n")


def provision_competition_data(
    target: Path,
    data_root: Path,
    expected_train_rows: str,
    expected_public_rows: str,
    *,
    output_mode: str,
) -> None:
    run_checked(
        [
            sys.executable,
            str(DATA_PREPARER),
            "--source-root",
            str(data_root.resolve()),
            "--destination",
            str(target / "competition_data"),
            "--expected-train-rows",
            expected_train_rows,
            "--expected-public-rows",
            expected_public_rows,
        ],
        quiet=True,
    )
    exclude_local_competition_data(target)
    if output_mode == "normal":
        print(f"Prepared hidden-test-free development data: {target / 'competition_data'}")


def initialize_target(arguments: list[str], *, output_mode: str) -> None:
    run_checked([str(RESEARCH_AGENT), "init", *arguments], quiet=output_mode != "verbose")


def validate_initialized_target(target: Path) -> None:
    try:
        require_supported_record(target)
        ensure_target_git_root(target, create_if_missing=False)
    except BootstrapError as exc:
        raise ValueError(str(exc)) from exc


def setup_competition(
    *,
    target: Path,
    task_source: Path,
    personal_source: Path,
    optimize_source: Path,
    starter_archive: Path,
    starter_sha256: str,
    data_root: Path,
    expected_train_rows: str,
    expected_public_rows: str,
    output_mode: str,
) -> Path:
    if (target / "research_record").exists():
        if not (target / "task.md").is_file() or not (target / "PERSONAL.md").is_file():
            raise ValueError(f"initialized competition target must contain task.md and PERSONAL.md: {target}")
    elif target.exists():
        if not target.is_dir():
            raise ValueError(f"competition target is not a directory: {target}")
        if (target / "task.md").is_file() and (target / "PERSONAL.md").is_file():
            initialize_target(["--target", str(target)], output_mode=output_mode)
        elif any(target.iterdir()):
            raise ValueError(f"existing competition target must contain task.md and PERSONAL.md: {target}")
        else:
            initialize_target(
                ["--new", str(target), "--task", str(task_source), "--personal", str(personal_source)],
                output_mode=output_mode,
            )
    else:
        initialize_target(
            ["--new", str(target), "--task", str(task_source), "--personal", str(personal_source)],
            output_mode=output_mode,
        )

    validate_initialized_target(target)
    seed_competition_optimize(target, optimize_source)
    provision_starter_kit(target, starter_archive, starter_sha256, output_mode=output_mode)
    provision_competition_data(
        target,
        data_root,
        expected_train_rows,
        expected_public_rows,
        output_mode=output_mode,
    )
    return target.resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="competition.sh")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_role_options(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("--meta-cli", choices=supported_runners())
        command_parser.add_argument("--scientist-cli", choices=supported_runners())
        command_parser.add_argument("--meta-model")
        command_parser.add_argument("--scientist-model")
        command_parser.add_argument("--meta-effort", choices=EFFORT_LEVELS)
        command_parser.add_argument("--scientist-effort", choices=EFFORT_LEVELS)

    setup = subparsers.add_parser("setup")
    setup.add_argument("-v", "--verbose", action="store_true")
    setup.add_argument("-q", "--quiet", action="store_true")

    step = subparsers.add_parser("step")
    step.add_argument("-m", "--model")
    step.add_argument("-e", "--effort", choices=EFFORT_LEVELS)
    add_role_options(step)
    step.add_argument("-v", "--verbose", action="store_true")
    step.add_argument("-q", "--quiet", action="store_true")

    run = subparsers.add_parser("run")
    run.add_argument("--max-cycles", type=int, required=True)
    run.add_argument("-m", "--model")
    run.add_argument("-e", "--effort", choices=EFFORT_LEVELS)
    add_role_options(run)
    run.add_argument("-v", "--verbose", action="store_true")
    run.add_argument("-q", "--quiet", action="store_true")
    return parser


def output_mode(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    if args.verbose and args.quiet:
        parser.error("--verbose and --quiet are mutually exclusive")
    if args.verbose:
        return "verbose"
    if args.quiet:
        return "quiet"
    return "normal"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    mode = output_mode(args, parser)
    if args.command == "run" and args.max_cycles < 1:
        parser.error("run requires --max-cycles with a positive integer")

    shared_cli = os.environ.get("RESEARCH_AGENT_COMPETITION_CLI", "codex")
    meta_cli = getattr(args, "meta_cli", None) or os.environ.get(
        "RESEARCH_AGENT_COMPETITION_META_CLI", shared_cli
    )
    scientist_cli = getattr(args, "scientist_cli", None) or os.environ.get(
        "RESEARCH_AGENT_COMPETITION_SCIENTIST_CLI", shared_cli
    )

    shared_model = getattr(args, "model", None)
    if shared_model is None:
        shared_model = os.environ.get("RESEARCH_AGENT_COMPETITION_MODEL") or None
    meta_model = getattr(args, "meta_model", None) or os.environ.get(
        "RESEARCH_AGENT_COMPETITION_META_MODEL"
    ) or shared_model
    scientist_model = getattr(args, "scientist_model", None) or os.environ.get(
        "RESEARCH_AGENT_COMPETITION_SCIENTIST_MODEL"
    ) or shared_model

    shared_effort = getattr(args, "effort", None) or os.environ.get("RESEARCH_AGENT_COMPETITION_EFFORT")
    meta_effort = getattr(args, "meta_effort", None) or os.environ.get(
        "RESEARCH_AGENT_COMPETITION_META_EFFORT"
    ) or shared_effort
    scientist_effort = getattr(args, "scientist_effort", None) or os.environ.get(
        "RESEARCH_AGENT_COMPETITION_SCIENTIST_EFFORT"
    ) or shared_effort

    if meta_model == "luna" and meta_cli == "codex":
        meta_model = "gpt-5.6-luna"
    if scientist_model == "luna" and scientist_cli == "codex":
        scientist_model = "gpt-5.6-luna"

    target = competition_target(args.command)
    task_source = env_path(
        "RESEARCH_AGENT_COMPETITION_TASK",
        WORKSPACE_DIR / "competitions" / "kuairand" / "task.md",
    )
    personal_source = env_path(
        "RESEARCH_AGENT_COMPETITION_PERSONAL",
        WORKSPACE_DIR / "PERSONAL.md",
    )
    optimize_source = env_path(
        "RESEARCH_AGENT_COMPETITION_OPTIMIZE",
        WORKSPACE_DIR / "competitions" / "kuairand" / "OPTIMIZE.md",
    )
    starter_archive = env_path(
        "RESEARCH_AGENT_COMPETITION_STARTER_KIT",
        WORKSPACE_DIR / "vendor" / "kuairand-starter-kit.zip",
    )
    starter_sha256 = os.environ.get(
        "RESEARCH_AGENT_COMPETITION_STARTER_KIT_SHA256",
        "07237e62cc1a9cd8278556dab995dd5388516f10772724f582ef8320ac68b10b",
    )
    data_root = env_path(
        "RESEARCH_AGENT_COMPETITION_DATA_ROOT",
        WORKSPACE_DIR / "data" / "KuaiRand-Pure",
    )
    expected_train_rows = os.environ.get("RESEARCH_AGENT_COMPETITION_EXPECTED_TRAIN_ROWS", "1141112")
    expected_public_rows = os.environ.get("RESEARCH_AGENT_COMPETITION_EXPECTED_PUBLIC_ROWS", "124909")

    try:
        target = setup_competition(
            target=target,
            task_source=task_source,
            personal_source=personal_source,
            optimize_source=optimize_source,
            starter_archive=starter_archive,
            starter_sha256=starter_sha256,
            data_root=data_root,
            expected_train_rows=expected_train_rows,
            expected_public_rows=expected_public_rows,
            output_mode=mode,
        )
    except (OSError, ValueError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.command == "setup":
        if mode == "quiet":
            print(f"competition: ready {target}")
        else:
            print(f"Competition project ready: {target}")
        return 0

    environment = os.environ.copy()
    environment.pop("RESEARCH_AGENT_COMPETITION_DATA_ROOT", None)
    environment["RESEARCH_AGENT_DEVELOPMENT_DATA_ROOT"] = str(target / "competition_data")

    runner_args = [
        str(RESEARCH_AGENT),
        args.command,
    ]
    if meta_cli == scientist_cli:
        runner_args.extend(["--cli", meta_cli])
    else:
        runner_args.extend(["--meta-cli", meta_cli, "--scientist-cli", scientist_cli])

    if meta_model == scientist_model:
        if meta_model:
            runner_args.extend(["--model", meta_model])
    else:
        if meta_model:
            runner_args.extend(["--meta-model", meta_model])
        if scientist_model:
            runner_args.extend(["--scientist-model", scientist_model])

    if meta_effort == scientist_effort:
        if meta_effort:
            runner_args.extend(["--effort", meta_effort])
    else:
        if meta_effort:
            runner_args.extend(["--meta-effort", meta_effort])
        if scientist_effort:
            runner_args.extend(["--scientist-effort", scientist_effort])

    runner_args.extend(["--target", str(target), "--allow-edits"])
    if mode == "verbose":
        runner_args.append("--verbose")
    elif mode == "quiet":
        runner_args.append("--quiet")
    if args.command == "run":
        runner_args.extend(["--max-cycles", str(args.max_cycles)])

    os.execvpe(runner_args[0], runner_args, environment)
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
