"""Memory compression for continuity systems.

Compression turns many raw events into a smaller continuity summary.
This is different from deletion. Compression preserves meaning while reducing
noise, context size, and retrieval burden.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from continuity_core.memory.event import MemoryEvent


@dataclass(frozen=True)
class CompressedMemory:
    """Compressed representation of a group of memory events."""

    summary: str
    event_count: int
    start_time: datetime
    end_time: datetime
    recurring_tags: dict[str, int]
    dominant_event_types: dict[str, int]
    highest_importance: float
    source_event_ids: list[str]


class MemoryCompressor:
    """Rule-based memory compressor for event groups."""

    def compress(self, events: list[MemoryEvent], max_themes: int = 5) -> CompressedMemory:
        """Compress events into a structured continuity summary."""
        if not events:
            raise ValueError("Cannot compress an empty event list.")
        if max_themes <= 0:
            raise ValueError("max_themes must be greater than zero.")

        ordered_events = sorted(events, key=lambda event: event.timestamp)
        tag_counts = self._top_counts(
            [tag for event in ordered_events for tag in event.tags],
            max_items=max_themes,
        )
        event_type_counts = self._top_counts(
            [event.event_type for event in ordered_events],
            max_items=max_themes,
        )
        highest_importance = max(event.importance for event in ordered_events)

        summary = self._build_summary(
            ordered_events=ordered_events,
            recurring_tags=tag_counts,
            dominant_event_types=event_type_counts,
        )

        return CompressedMemory(
            summary=summary,
            event_count=len(ordered_events),
            start_time=ordered_events[0].timestamp,
            end_time=ordered_events[-1].timestamp,
            recurring_tags=tag_counts,
            dominant_event_types=event_type_counts,
            highest_importance=highest_importance,
            source_event_ids=[event.event_id for event in ordered_events],
        )

    def _build_summary(
        self,
        ordered_events: list[MemoryEvent],
        recurring_tags: dict[str, int],
        dominant_event_types: dict[str, int],
    ) -> str:
        """Build a human-readable compressed memory summary."""
        first_event = ordered_events[0]
        last_event = ordered_events[-1]

        themes = ", ".join(recurring_tags.keys()) if recurring_tags else "no dominant themes"
        event_types = ", ".join(dominant_event_types.keys()) if dominant_event_types else "no dominant event types"

        return (
            f"Compressed {len(ordered_events)} events from "
            f"{first_event.timestamp.date()} to {last_event.timestamp.date()}. "
            f"Dominant themes: {themes}. "
            f"Dominant event types: {event_types}. "
            f"Trajectory begins with: '{first_event.content}' "
            f"and ends with: '{last_event.content}'."
        )

    @staticmethod
    def _top_counts(items: list[str], max_items: int) -> dict[str, int]:
        counter = Counter(items)
        return dict(counter.most_common(max_items))
