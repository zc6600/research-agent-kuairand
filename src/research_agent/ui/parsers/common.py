from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8") if path.is_file() else ""
    except OSError:
        return ""


def read_json(path: Path) -> dict[str, Any]:
    text = read_text(path)
    if not text:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def read_yaml(path: Path) -> dict[str, Any]:
    text = read_text(path)
    if not text:
        return {}
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError:
        return {}
    return value if isinstance(value, dict) else {}


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def mappings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def scalar_text(value: Any) -> str | None:
    if value is None or isinstance(value, (dict, list, tuple, set)):
        return None
    text = str(value).strip()
    if not text or text.lower() in {"null", "none"} or text.startswith("<"):
        return None
    return text


def first_text(value: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        text = scalar_text(value.get(key))
        if text:
            return text
    return None
