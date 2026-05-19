"""Timeline builder for continuity events.

This module converts memory events into a structured timeline that can be used
by CLI tools, APIs, dashboards, and future visualizations.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from continuity_core.memory.event import MemoryEvent
from continuity_core.salience.scorer import SalienceScorer


@dataclass(frozen=True)
class TimelineItem:
    """A single continuity timeline item."""

    event_id: str
    date: str
    event_type: str
    content: str
    tags: list[str]
    importance: float
    salience: float


@dataclass(frozen=True)
class TimelineDay:
    """Events grouped by calendar day."""

    date: str
    events: list[TimelineItem]


class TimelineBuilder:
    """Builds salience-aware timelines from memory events."""

    def __init__(self, salience_scorer: SalienceScorer | None = None) -> None:
        self.salience_scorer = salience_scorer or SalienceScorer()

    def build(self, events: list[MemoryEvent]) -> list[TimelineDay]:
        """Return events grouped by date and sorted chronologically."""
        grouped: dict[date, list[TimelineItem]] = defaultdict(list)

        for event in sorted(events, key=lambda item: item.timestamp):
            item = TimelineItem(
                event_id=event.event_id,
                date=event.timestamp.date().isoformat(),
                event_type=event.event_type,
                content=event.content,
                tags=event.tags,
                importance=event.importance,
                salience=self.salience_scorer.score(event),
            )
            grouped[event.timestamp.date()].append(item)

        return [
            TimelineDay(
                date=day.isoformat(),
                events=sorted(items, key=lambda item: item.salience, reverse=True),
            )
            for day, items in sorted(grouped.items(), key=lambda pair: pair[0])
        ]

    def high_salience_items(
        self,
        events: list[MemoryEvent],
        threshold: float = 0.7,
    ) -> list[TimelineItem]:
        """Return timeline items with salience greater than or equal to threshold."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")

        items: list[TimelineItem] = []
        for day in self.build(events):
            items.extend(item for item in day.events if item.salience >= threshold)

        return sorted(items, key=lambda item: item.salience, reverse=True)
