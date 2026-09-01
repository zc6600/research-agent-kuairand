from __future__ import annotations

import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from research_agent.launcher import run_invocation
from research_agent.runners.base import Invocation


@unittest.skipUnless(os.name == "posix", "process-group cancellation is POSIX-specific")
class LauncherCancellationTests(unittest.TestCase):
    def test_cancel_event_interrupts_owned_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ready = root / "ready"
            child_signal = root / "child-signal"
            child_script = root / "child.py"
            parent_script = root / "parent.py"
            child_script.write_text(
                """import signal\nimport sys\nimport time\nfrom pathlib import Path\n\nmarker = Path(sys.argv[1])\n\ndef stop(signum, _frame):\n    marker.write_text(signal.Signals(signum).name, encoding='utf-8')\n    raise SystemExit(0)\n\nsignal.signal(signal.SIGINT, stop)\nsignal.signal(signal.SIGTERM, stop)\nwhile True:\n    time.sleep(0.05)\n""",
                encoding="utf-8",
            )
            parent_script.write_text(
                """import subprocess\nimport sys\nimport time\nfrom pathlib import Path\n\nready = Path(sys.argv[1])\nchild_script = sys.argv[2]\nmarker = sys.argv[3]\nsubprocess.Popen([sys.executable, child_script, marker])\nready.write_text('ready', encoding='utf-8')\nwhile True:\n    time.sleep(0.05)\n""",
                encoding="utf-8",
            )
            invocation = Invocation(
                (sys.executable, str(parent_script), str(ready), str(child_script), str(child_signal)),
                root,
            )
            cancel = threading.Event()
            errors: list[BaseException] = []

            def run() -> None:
                try:
                    run_invocation(
                        invocation,
                        output_path=root / "runner.log",
                        stream_output=False,
                        cancel_event=cancel,
                    )
                except BaseException as exc:  # expected cancellation result
                    errors.append(exc)

            worker = threading.Thread(target=run)
            worker.start()
            deadline = time.monotonic() + 5
            while not ready.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(ready.exists())
            cancel.set()
            worker.join(timeout=6)

            self.assertFalse(worker.is_alive())
            self.assertTrue(errors)
            self.assertIn("cancelled by coordinator", str(errors[0]))
            deadline = time.monotonic() + 3
            while not child_signal.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(child_signal.exists())
            self.assertIn(child_signal.read_text(encoding="utf-8"), {"SIGINT", "SIGTERM"})


if __name__ == "__main__":
    unittest.main()
