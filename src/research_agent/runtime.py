from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_run_directory(target: Path) -> tuple[str, Path]:
    run_id = uuid.uuid4().hex
    run_dir = target / "research_record" / "runtime" / "tmp" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_id, run_dir


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
