from __future__ import annotations

import json
import mimetypes
import threading
import webbrowser
from collections import deque
from dataclasses import asdict
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from research_agent.ui.lifecycle import RunLifecycle, latest_run, run_directory
from research_agent.ui.progress import diff_status
from research_agent.ui.status import ResearchStatus, inspect_status

RAW_FILES = {
    "brief": "research_record/runtime/current-brief.json",
    "version": "research_record/VERSION",
    "state": "research_record/STATE.yaml",
    "record": "research_record/RESEARCH_RECORD.yaml",
    "intuition": "research_record/RESEARCH_INTUITION.md",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event_kind(text: str) -> str:
    if text.startswith("✦"):
        return "intuition"
    if text.startswith("✓"):
        return "success"
    if text.startswith("→"):
        return "progress"
    if text.lstrip().startswith("Bottleneck"):
        return "bottleneck"
    if text.lstrip().startswith("Hypothesis"):
        return "hypothesis"
    if text.lstrip().startswith("Experiment"):
        return "experiment"
    return "detail"


def _read_raw(target: Path, relative: str) -> dict[str, str]:
    path = target / relative
    try:
        content = path.read_text(encoding="utf-8") if path.is_file() else ""
    except OSError:
        content = ""
    return {"path": relative, "content": content}


class DashboardState:
    """In-memory read-only projection used only by the local GUI process."""

    def __init__(self, target: Path, *, max_events: int = 200) -> None:
        self.target = target.expanduser().resolve()
        self._lock = threading.Lock()
        self._status: ResearchStatus = inspect_status(self.target)
        self._run: RunLifecycle | None = latest_run(self.target)
        self._events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self._next_event_id = 1
        if self._run is not None and self._run.status == "running":
            self._append_event(
                f"→ Run {self._run.run_id[:8]} · {self._run.kind or 'run'} started",
                at=self._run.started_at,
            )

    def _append_event(self, text: str, *, at: str | None = None) -> None:
        self._events.append({
            "id": self._next_event_id,
            "at": at or _now(),
            "kind": _event_kind(text),
            "text": text.strip(),
        })
        self._next_event_id += 1

    def refresh(self) -> None:
        with self._lock:
            current_status = inspect_status(self.target)
            for event in diff_status(self._status, current_status):
                self._append_event(event)
            self._status = current_status

            current_run = latest_run(self.target)
            previous_run = self._run
            if current_run is not None:
                if previous_run is None or current_run.run_id != previous_run.run_id:
                    if current_run.status == "running":
                        self._append_event(
                            f"→ Run {current_run.run_id[:8]} · {current_run.kind or 'run'} started",
                            at=current_run.started_at,
                        )
                    elif current_run.status == "closed":
                        self._append_event(
                            f"✓ Run {current_run.run_id[:8]} · {current_run.terminal_status or 'closed'}",
                            at=current_run.ended_at,
                        )
                elif previous_run.status != current_run.status and current_run.status == "closed":
                    self._append_event(
                        f"✓ Run {current_run.run_id[:8]} · {current_run.terminal_status or 'closed'}",
                        at=current_run.ended_at,
                    )
            self._run = current_run

    def payload(self) -> dict[str, Any]:
        self.refresh()
        with self._lock:
            return {
                "generated_at": _now(),
                "research": asdict(self._status),
                "run": asdict(self._run) if self._run is not None else None,
                "events": list(self._events),
            }

    def raw_files(self) -> dict[str, dict[str, str]]:
        values = {key: _read_raw(self.target, relative) for key, relative in RAW_FILES.items()}
        run = latest_run(self.target)
        if run is None:
            values["usage"] = {"path": "", "content": ""}
        else:
            run_dir = run_directory(self.target, run)
            if run.kind == "baseline":
                candidates = ("baseline/model-usage.json", "baseline/usage.json")
            else:
                candidates = ("meta/model-usage.json", "meta/usage.json")
            for suffix in candidates:
                path = run_dir / suffix
                if path.is_file():
                    values["usage"] = _read_raw(self.target, str(path.relative_to(self.target)))
                    break
            else:
                values["usage"] = {"path": "", "content": ""}

            if run.kind == "parallel":
                for key, suffix in (
                    ("parallel-manifest", "parallel/manifest.json"),
                    ("parallel-result", "parallel/result.json"),
                    ("parallel-aggregate", "parallel/aggregate.md"),
                ):
                    path = run_dir / suffix
                    if path.is_file():
                        values[key] = _read_raw(self.target, str(path.relative_to(self.target)))
        return values


def _handler(state: DashboardState) -> type[BaseHTTPRequestHandler]:
    static_root = Path(__file__).resolve().with_name("static")

    class DashboardHandler(BaseHTTPRequestHandler):
        server_version = "ResearchAgentGUI/1"

        def log_message(self, format: str, *args: object) -> None:
            return

        def _bytes(self, data: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _json(self, value: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
            data = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self._bytes(data, "application/json; charset=utf-8", status)

        def _static(self, name: str) -> None:
            path = static_root / name
            if not path.is_file() or path.parent != static_root:
                self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
                return
            try:
                data = path.read_bytes()
            except OSError:
                self._json({"error": "cannot read asset"}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
                content_type += "; charset=utf-8"
            self._bytes(data, content_type)

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/api/status":
                self._json(state.payload())
                return
            if path == "/api/files":
                self._json(state.raw_files())
                return
            if path in {"/", "/index.html"}:
                self._static("index.html")
                return
            if path == "/app.js":
                self._static("app.js")
                return
            if path == "/style.css":
                self._static("style.css")
                return
            self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    return DashboardHandler


def serve_dashboard(
    target: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    open_browser: bool = True,
) -> int:
    state = DashboardState(target)
    server = ThreadingHTTPServer((host, port), _handler(state))
    url = f"http://{host}:{server.server_port}/"
    print(f"Research Agent GUI · {url}")
    print(f"Project            · {state.target}")
    print("Press Ctrl-C to stop.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
