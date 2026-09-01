from __future__ import annotations

import os
import signal
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from research_agent.launcher import run_invocation
from research_agent.runners.base import Invocation


def interrupt_when_ready(ready: Path) -> None:
    deadline = time.monotonic() + 5
    while not ready.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    os.kill(os.getpid(), signal.SIGINT)


@unittest.skipUnless(os.name == "posix", "PTY-backed Goal mode is POSIX-specific")
class InteractiveInvocationTests(unittest.TestCase):
    def test_interactive_invocation_provides_tty_and_submits_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            runner = directory / "runner.py"
            received = directory / "received.txt"
            output = directory / "runner.log"
            runner.write_text(
                """import os
import sys
from pathlib import Path

received = Path(sys.argv[1])
print('Ask Codex to do anything', flush=True)
received.write_text(f'isatty={os.isatty(0)}', encoding='utf-8')
data = os.read(0, 4096)
received.write_text(received.read_text(encoding='utf-8') + '\\n' + data.decode(), encoding='utf-8')
print('goal received', flush=True)
""",
                encoding="utf-8",
            )

            invocation = Invocation(
                (sys.executable, str(runner), str(received)),
                directory,
                interactive=True,
                input_text="/goal test objective\r",
            )

            self.assertEqual(
                run_invocation(invocation, output_path=output, stream_output=False),
                0,
            )
            self.assertIn("isatty=True", received.read_text(encoding="utf-8"))
            self.assertIn("/goal test objective", received.read_text(encoding="utf-8"))
            self.assertIn("Ask Codex to do anything", output.read_text(encoding="utf-8"))


@unittest.skipUnless(os.name == "posix", "process-group ownership is POSIX-specific")
class ProcessGroupOwnershipTests(unittest.TestCase):
    def test_nested_invocation_joins_outer_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            ready = directory / "ready.txt"
            marker = directory / "worker-signal.txt"
            worker_script = directory / "worker.py"
            nested_script = directory / "nested.py"

            worker_script.write_text(
                """import signal
import sys
import time
from pathlib import Path

ready = Path(sys.argv[1])
marker = Path(sys.argv[2])

def interrupt(_signum, _frame):
    marker.write_text("SIGINT", encoding="utf-8")
    raise SystemExit(130)

signal.signal(signal.SIGINT, interrupt)
ready.write_text("ready", encoding="utf-8")
while True:
    time.sleep(0.05)
""",
                encoding="utf-8",
            )
            nested_script.write_text(
                """import sys
from pathlib import Path

from research_agent.launcher import run_invocation
from research_agent.runners.base import Invocation

directory = Path(sys.argv[1])
worker = Path(sys.argv[2])
try:
    run_invocation(Invocation((sys.executable, str(worker), sys.argv[3], sys.argv[4]), directory))
except KeyboardInterrupt:
    raise SystemExit(130)
""",
                encoding="utf-8",
            )

            invocation = Invocation(
                (
                    sys.executable,
                    str(nested_script),
                    str(directory),
                    str(worker_script),
                    str(ready),
                    str(marker),
                ),
                directory,
            )
            interrupter = threading.Thread(target=interrupt_when_ready, args=(ready,), daemon=True)
            interrupter.start()

            with self.assertRaises(KeyboardInterrupt):
                run_invocation(invocation)
            interrupter.join(timeout=1)

            self.assertEqual(marker.read_text(encoding="utf-8"), "SIGINT")

    def test_cleanup_tracks_group_after_runner_leader_exits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            ready = directory / "ready.txt"
            child_ready = directory / "child-ready.txt"
            parent_marker = directory / "parent-signal.txt"
            child_marker = directory / "child-signal.txt"
            worker_script = directory / "worker.py"
            runner_script = directory / "runner.py"

            worker_script.write_text(
                """import signal
import sys
import time
from pathlib import Path

ready = Path(sys.argv[1])
marker = Path(sys.argv[2])

def terminate(_signum, _frame):
    marker.write_text("SIGTERM", encoding="utf-8")
    raise SystemExit(143)

signal.signal(signal.SIGINT, signal.SIG_IGN)
signal.signal(signal.SIGTERM, terminate)
ready.write_text("ready", encoding="utf-8")
while True:
    time.sleep(0.05)
""",
                encoding="utf-8",
            )
            runner_script.write_text(
                """import signal
import subprocess
import sys
import time
from pathlib import Path

ready = Path(sys.argv[1])
child_ready = Path(sys.argv[2])
parent_marker = Path(sys.argv[3])
child_marker = Path(sys.argv[4])
worker_script = Path(sys.argv[5])
subprocess.Popen([sys.executable, str(worker_script), str(child_ready), str(child_marker)])

def interrupt(_signum, _frame):
    parent_marker.write_text("SIGINT", encoding="utf-8")
    raise SystemExit(130)

signal.signal(signal.SIGINT, interrupt)
deadline = time.monotonic() + 5
while not child_ready.exists() and time.monotonic() < deadline:
    time.sleep(0.01)
ready.write_text("ready", encoding="utf-8")
while True:
    time.sleep(0.05)
""",
                encoding="utf-8",
            )

            invocation = Invocation(
                (
                    sys.executable,
                    str(runner_script),
                    str(ready),
                    str(child_ready),
                    str(parent_marker),
                    str(child_marker),
                    str(worker_script),
                ),
                directory,
            )
            interrupter = threading.Thread(target=interrupt_when_ready, args=(ready,), daemon=True)
            interrupter.start()

            with (
                patch("research_agent.launcher.INTERRUPT_GRACE_SECONDS", 0.05),
                patch("research_agent.launcher.TERMINATE_GRACE_SECONDS", 0.5),
                self.assertRaises(KeyboardInterrupt),
            ):
                run_invocation(invocation)
            interrupter.join(timeout=1)

            self.assertEqual(parent_marker.read_text(encoding="utf-8"), "SIGINT")
            self.assertEqual(child_marker.read_text(encoding="utf-8"), "SIGTERM")


if __name__ == "__main__":
    unittest.main()
