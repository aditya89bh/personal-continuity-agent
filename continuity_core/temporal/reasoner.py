"""Temporal reasoning for personal continuity.

The temporal layer looks across events over time. It detects continuity signals
that cannot be seen from a single memory: repeated loops, inactivity gaps,
contradictions, unresolved items, and momentum decay.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from itertools import pairwise

from continuity_core.memory.event import MemoryEvent


@dataclass(frozen=True)
class ContinuityGap:
    """Represents a long inactivity gap between two events."""

    start_event_id: str
    end_event_id: str
    gap_days: int


@dataclass(frozen=True)
class TemporalReport:
    """Summary of temporal continuity signals."""

    recurring_tags: dict[str, int]
    continuity_gaps: list[ContinuityGap]
    unresolved_events: list[MemoryEvent]
    contradiction_events: list[MemoryEvent]
    momentum_status: str
    momentum_score: float


class TemporalReasoner:
    """Detects continuity patterns across ordered memory events."""

    def __init__(self, inactivity_gap_days: int = 30) -> None:
        if inactivity_gap_days <= 0:
            raise ValueError("inactivity_gap_days must be greater than zero")
        self.inactivity_gap_days = inactivity_gap_days

    def analyze(self, events: list[MemoryEvent], now: datetime | None = None) -> TemporalReport:
        """Analyze events and return a temporal continuity report."""
        ordered_events = self._ordered(events)
        return TemporalReport(
            recurring_tags=self.detect_recurring_tags(ordered_events),
            continuity_gaps=self.detect_continuity_gaps(ordered_events),
            unresolved_events=self.detect_unresolved_events(ordered_events),
            contradiction_events=self.detect_contradictions(ordered_events),
            momentum_status=self.momentum_status(ordered_events, now=now),
            momentum_score=self.momentum_score(ordered_events, now=now),
        )

    def detect_recurring_tags(self, events: list[MemoryEvent], minimum_count: int = 2) -> dict[str, int]:
        """Return tags that recur at least minimum_count times."""
        if minimum_count <= 0:
            raise ValueError("minimum_count must be greater than zero")

        tag_counts: dict[str, int] = {}
        for event in events:
            for tag in event.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            tag: count
            for tag, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))
            if count >= minimum_count
        }

    def detect_continuity_gaps(self, events: list[MemoryEvent]) -> list[ContinuityGap]:
        """Return gaps where no events occurred for at least inactivity_gap_days."""
        ordered_events = self._ordered(events)
        gaps: list[ContinuityGap] = []

        for previous_event, next_event in pairwise(ordered_events):
            gap_days = (next_event.timestamp - previous_event.timestamp).days
            if gap_days >= self.inactivity_gap_days:
                gaps.append(
                    ContinuityGap(
                        start_event_id=previous_event.event_id,
                        end_event_id=next_event.event_id,
                        gap_days=gap_days,
                    )
                )

        return gaps

    def detect_unresolved_events(self, events: list[MemoryEvent]) -> list[MemoryEvent]:
        """Return events marked as unresolved through type, tag, or metadata."""
        unresolved_types = {"unresolved", "missed_commitment", "open_loop"}
        unresolved_events: list[MemoryEvent] = []

        for event in self._ordered(events):
            if event.event_type in unresolved_types:
                unresolved_events.append(event)
            elif "unresolved" in event.tags:
                unresolved_events.append(event)
            elif bool(event.metadata.get("unresolved")):
                unresolved_events.append(event)

        return unresolved_events

    def detect_contradictions(self, events: list[MemoryEvent]) -> list[MemoryEvent]:
        """Return events marked as contradictions."""
        return [
            event
            for event in self._ordered(events)
            if event.event_type == "contradiction" or "contradiction" in event.tags
        ]

    def momentum_score(self, events: list[MemoryEvent], now: datetime | None = None) -> float:
        """Estimate continuity momentum from recent progress and unresolved drag.

        The baseline formula is intentionally simple:
        - recent progress adds momentum
        - recent goals add some momentum
        - unresolved events and contradictions reduce momentum
        - long inactivity reduces momentum
        """
        ordered_events = self._ordered(events)
        if not ordered_events:
            return 0.0

        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        recent_window_start = current_time - timedelta(days=30)
        recent_events = [event for event in ordered_events if event.timestamp >= recent_window_start]

        progress_count = sum(1 for event in recent_events if event.event_type == "progress")
        goal_count = sum(1 for event in recent_events if event.event_type == "goal")
        unresolved_count = len(self.detect_unresolved_events(recent_events))
        contradiction_count = len(self.detect_contradictions(recent_events))

        days_since_last_event = max(0, (current_time - ordered_events[-1].timestamp).days)
        inactivity_penalty = min(0.4, days_since_last_event / 90)

        score = 0.3 + (progress_count * 0.2) + (goal_count * 0.1)
        score -= unresolved_count * 0.15
        score -= contradiction_count * 0.2
        score -= inactivity_penalty

        return round(max(0.0, min(1.0, score)), 4)

    def momentum_status(self, events: list[MemoryEvent], now: datetime | None = None) -> str:
        """Return human-readable momentum status."""
        score = self.momentum_score(events, now=now)
        if score >= 0.7:
            return "strong_momentum"
        if score >= 0.4:
            return "moderate_momentum"
        if score > 0.0:
            return "weak_momentum"
        return "stalled"

    @staticmethod
    def _ordered(events: list[MemoryEvent]) -> list[MemoryEvent]:
        """Return events sorted by timestamp."""
        return sorted(events, key=lambda event: event.timestamp)
