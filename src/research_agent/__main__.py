from __future__ import annotations

import sys

from research_agent.cli import main as cli_main
from research_agent.state import main as state_main


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args[:1] == ["state"]:
        return state_main(args[1:])
    if args[:1] == ["baseline"]:
        from research_agent.baseline import baseline_main

        return baseline_main(args[1:])
    if args[:1] in (["status"], ["watch"], ["gui"]):
        from research_agent.ui.cli import gui_main, status_main, watch_main

        if args[0] == "status":
            return status_main(args[1:])
        if args[0] == "watch":
            return watch_main(args[1:])
        return gui_main(args[1:])
    return cli_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
