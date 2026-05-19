"""In-memory event store for continuity events.

This store is intentionally simple. It gives the project a working baseline
before adding persistence, indexing, salience ranking, or graph retrieval.
"""

from __future__ import annotations

from collections.abc import Iterable

from continuity_core.memory.event import MemoryEvent


class InMemoryEventStore:
    """Simple event store for MemoryEvent objects."""

    def __init__(self, events: Iterable[MemoryEvent] | None = None) -> None:
        self._events: dict[str, MemoryEvent] = {}
        if events:
            for event in events:
                self.add(event)

    def add(self, event: MemoryEvent) -> MemoryEvent:
        """Add an event to the store.

        Raises:
            ValueError: If an event with the same id already exists.
        """
        if event.event_id in self._events:
            raise ValueError(f"Event already exists: {event.event_id}")
        self._events[event.event_id] = event
        return event

    def get(self, event_id: str) -> MemoryEvent | None:
        """Return an event by id, or None if it does not exist."""
        return self._events.get(event_id)

    def list_all(self) -> list[MemoryEvent]:
        """Return all events sorted by timestamp."""
        return sorted(self._events.values(), key=lambda event: event.timestamp)

    def filter_by_type(self, event_type: str) -> list[MemoryEvent]:
        """Return events matching a specific event type."""
        return [event for event in self.list_all() if event.event_type == event_type]

    def filter_by_tag(self, tag: str) -> list[MemoryEvent]:
        """Return events containing a specific tag."""
        return [event for event in self.list_all() if tag in event.tags]

    def high_importance(self, threshold: float = 0.7) -> list[MemoryEvent]:
        """Return events with importance greater than or equal to threshold."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")
        return [event for event in self.list_all() if event.importance >= threshold]

    def count(self) -> int:
        """Return the number of stored events."""
        return len(self._events)

    def clear(self) -> None:
        """Remove all events from the store."""
        self._events.clear()
