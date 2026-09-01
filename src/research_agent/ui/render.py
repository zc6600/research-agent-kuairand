from __future__ import annotations

from research_agent.ui.status import ResearchStatus


def _section(lines: list[str], title: str, value: str | None, *, label: str | None = None) -> None:
    if not value:
        return
    lines.append("")
    lines.append(title)
    if label:
        lines.append(f"  {label} · {value}")
    else:
        for line in value.splitlines():
            lines.append(f"  {line}")


def render_status(status: ResearchStatus) -> str:
    lines = ["Research Agent", "────────────────────────────────────────"]
    lines.append(f"Project      {status.project}")
    if status.research_cycle_id is not None:
        lines.append(f"Research cycle {status.research_cycle_id}")
        if status.cycle_id is not None and status.cycle_id != status.research_cycle_id:
            lines.append(f"META cycle   {status.cycle_id}")
    elif status.cycle_id is not None:
        lines.append(f"Cycle        {status.cycle_id}")
    if status.state_id:
        lines.append(f"State        {status.state_id}")
    if status.last_status:
        lines.append(f"Last status  {status.last_status}")

    focus_title = "Research focus"
    if status.focus_kind:
        focus_title += f" · {status.focus_kind.title()}"
    _section(lines, focus_title, status.focus, label=status.focus_id)
    _section(lines, "Latest recorded hypothesis", status.hypothesis, label=status.hypothesis_id)

    if status.experiment_id:
        suffix = f" · {status.experiment_status}" if status.experiment_status else ""
        lines.extend(["", "Latest recorded experiment", f"  {status.experiment_id}{suffix}"])
    _section(lines, "Experiment result", status.experiment_result)
    _section(lines, "Primary metric", status.experiment_metric)
    _section(lines, "Experiment conclusion", status.experiment_conclusion)

    _section(lines, "✦ Research intuition", status.intuition)

    if status.meta_concerns:
        lines.extend(["", "META concerns"])
        lines.extend(f"  - {concern}" for concern in status.meta_concerns)

    if status.last_summary:
        _section(lines, "Latest summary", status.last_summary)
    if status.next_action:
        _section(lines, "Next action", status.next_action)

    if status.usage_status:
        usage = status.usage_status
        if status.usage_total is not None and status.usage_status == "measured":
            usage = f"{status.usage_total:,} tokens"
        lines.extend(["", "Usage", f"  {usage}"])

    return "\n".join(lines)
