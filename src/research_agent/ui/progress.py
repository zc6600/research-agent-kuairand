from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from research_agent.ui.status import ResearchStatus, inspect_status


@dataclass
class SemanticProgress:
    target: Path
    previous: ResearchStatus | None = None

    def __post_init__(self) -> None:
        self.previous = inspect_status(self.target)

    def poll(self) -> None:
        current = inspect_status(self.target)
        for line in diff_status(self.previous, current):
            print(line, flush=True)
        self.previous = current


def diff_status(previous: ResearchStatus | None, current: ResearchStatus) -> tuple[str, ...]:
    if previous is None:
        return ()
    events: list[str] = []
    if current.cycle_id is not None and current.cycle_id != previous.cycle_id:
        events.append(f"→ Cycle {current.cycle_id}")
    if current.focus_id and current.focus_id != previous.focus_id:
        kind = (current.focus_kind or "research focus").title()
        label = f" · {current.focus}" if current.focus else ""
        events.append(f"  {kind} · {current.focus_id}{label}")
    if current.hypothesis_id and current.hypothesis_id != previous.hypothesis_id:
        label = f" · {current.hypothesis}" if current.hypothesis else ""
        events.append(f"  Hypothesis · {current.hypothesis_id}{label}")
    if current.experiment_id and current.experiment_id != previous.experiment_id:
        suffix = f" · {current.experiment_status}" if current.experiment_status else ""
        events.append(f"  Experiment · {current.experiment_id}{suffix}")
    elif current.experiment_id and current.experiment_status != previous.experiment_status:
        events.append(f"✓ Experiment · {current.experiment_id} · {current.experiment_status or 'updated'}")
    if current.state_id and current.state_id != previous.state_id:
        events.append(f"✓ State · {current.state_id}")
    if current.intuition and current.intuition != previous.intuition:
        verb = "formed" if not previous.intuition else "revised"
        events.append(f"✦ Research intuition {verb}")
        events.append(f"  {current.intuition}")
    return tuple(events)
