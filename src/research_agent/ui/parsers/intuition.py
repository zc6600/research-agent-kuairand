from __future__ import annotations

import re
from pathlib import Path

from research_agent.ui.parsers.common import read_text


def parse_intuition(path: Path) -> str | None:
    text = read_text(path)
    marker = re.search(r"(?m)^##\s+Intuitions\s*$", text)
    if not marker:
        return None
    body = re.sub(r"<!--.*?-->", "", text[marker.end():], flags=re.DOTALL).strip()
    if not body:
        return None
    return re.split(r"\n\s*\n", body, maxsplit=1)[0].strip() or None
