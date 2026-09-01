"""Tolerant parsers that adapt mutable research artifacts to stable UI semantics."""

from research_agent.ui.parsers.intuition import parse_intuition
from research_agent.ui.parsers.research_record import ResearchRecordProjection, parse_research_record
from research_agent.ui.parsers.runtime import RuntimeProjection, parse_runtime
from research_agent.ui.parsers.state import StateProjection, parse_state, parse_state_id

__all__ = [
    "ResearchRecordProjection",
    "RuntimeProjection",
    "StateProjection",
    "parse_intuition",
    "parse_research_record",
    "parse_runtime",
    "parse_state",
    "parse_state_id",
]
