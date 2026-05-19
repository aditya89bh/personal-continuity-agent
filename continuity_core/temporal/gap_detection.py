"""Continuity gap detection.

Continuity is not only about what happened. It is also about what stopped
happening. This module detects gaps in goals, reflection, identity signals, and
repair sequences.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from continuity_core.memory.event import MemoryEvent


class GapType(StrEnum):
    """Types of continuity gaps."""

    GOAL_ABANDONMENT = "goal_abandonment"
    IDENTITY_SILENCE = "identity_silence"
    REFLECTION_SILENCE = "reflection_silence"
    REPAIR_MISSING = "repair_missing"


@dataclass(frozen=True)
class ContinuityGapFinding:
    """A detected continuity gap."""

    gap_type: GapType
    start_time: datetime
    end_time: datetime
    duration_days: int
    severity: float
    reason: str
    related_event_ids: list[str]


class ContinuityGapDetector:
    """Detects absence, decay, and unresolved gaps across memory events."""

    def __init__(self, gap_days: int = 30) -> None:
        if gap_days <= 0:
            raise ValueError("gap_days must be greater than zero")
        self.gap_days = gap_days

    def detect(self, events: list[MemoryEvent], now: datetime) -> list[ContinuityGapFinding]:
        """Return all detected continuity gaps."""
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        ordered = sorted(events, key=lambda event: event.timestamp)
        if not ordered:
            return []

        findings: list[ContinuityGapFinding] = []
        findings.extend(self.detect_goal_abandonment(ordered, now))
        findings.extend(self.detect_identity_silence(ordered, now))
        findings.extend(self.detect_reflection_silence(ordered, now))
        findings.extend(self.detect_missing_repairs(ordered, now))

        return sorted(findings, key=lambda finding: finding.severity, reverse=True)

    def detect_goal_abandonment(
        self,
        events: list[MemoryEvent],
        now: datetime,
    ) -> list[ContinuityGapFinding]:
        """Detect goals with no later progress or repair activity."""
        findings: list[ContinuityGapFinding] = []

        for event in events:
            if event.event_type != "goal":
                continue

            related_later_events = [
                later
                for later in events
                if later.timestamp > event.timestamp
                and self._shares_any_tag(event, later)
                and later.event_type in {"progress", "project_build", "repair_action", "reflection"}
            ]

            if related_later_events:
                continue

            duration_days = (now - event.timestamp).days
            if duration_days < self.gap_days:
                continue

            findings.append(
                ContinuityGapFinding(
                    gap_type=GapType.GOAL_ABANDONMENT,
                    start_time=event.timestamp,
                    end_time=now,
                    duration_days=duration_days,
                    severity=self._severity(duration_days),
                    reason="Goal has no related progress, repair, or reflection activity after declaration.",
                    related_event_ids=[event.event_id],
                )
            )

        return findings

    def detect_identity_silence(
        self,
        events: list[MemoryEvent],
        now: datetime,
    ) -> list[ContinuityGapFinding]:
        """Detect long periods after last identity-relevant memory."""
        identity_events = [event for event in events if self._is_identity_relevant(event)]
        if not identity_events:
            return []

        last_identity_event = max(identity_events, key=lambda event: event.timestamp)
        duration_days = (now - last_identity_event.timestamp).days

        if duration_days < self.gap_days:
            return []

        return [
            ContinuityGapFinding(
                gap_type=GapType.IDENTITY_SILENCE,
                start_time=last_identity_event.timestamp,
                end_time=now,
                duration_days=duration_days,
                severity=self._severity(duration_days),
                reason="No recent identity-relevant events detected.",
                related_event_ids=[last_identity_event.event_id],
            )
        ]

    def detect_reflection_silence(
        self,
        events: list[MemoryEvent],
        now: datetime,
    ) -> list[ContinuityGapFinding]:
        """Detect long periods after last reflection event."""
        reflection_events = [event for event in events if event.event_type == "reflection"]
        if not reflection_events:
            first_event = events[0]
            duration_days = (now - first_event.timestamp).days
            if duration_days < self.gap_days:
                return []
            return [
                ContinuityGapFinding(
                    gap_type=GapType.REFLECTION_SILENCE,
                    start_time=first_event.timestamp,
                    end_time=now,
                    duration_days=duration_days,
                    severity=self._severity(duration_days),
                    reason="No reflection events exist across the active memory window.",
                    related_event_ids=[first_event.event_id],
                )
            ]

        last_reflection = max(reflection_events, key=lambda event: event.timestamp)
        duration_days = (now - last_reflection.timestamp).days
        if duration_days < self.gap_days:
            return []

        return [
            ContinuityGapFinding(
                gap_type=GapType.REFLECTION_SILENCE,
                start_time=last_reflection.timestamp,
                end_time=now,
                duration_days=duration_days,
                severity=self._severity(duration_days),
                reason="No recent reflection event detected.",
                related_event_ids=[last_reflection.event_id],
            )
        ]

    def detect_missing_repairs(
        self,
        events: list[MemoryEvent],
        now: datetime,
    ) -> list[ContinuityGapFinding]:
        """Detect contradiction events without later repair actions."""
        findings: list[ContinuityGapFinding] = []

        for event in events:
            if event.event_type != "contradiction" and "contradiction" not in event.tags:
                continue

            repair_events = [
                later
                for later in events
                if later.timestamp > event.timestamp
                and later.event_type in {"repair_action", "return_after_gap"}
                and self._shares_any_tag(event, later)
            ]

            if repair_events:
                continue

            duration_days = (now - event.timestamp).days
            if duration_days < self.gap_days:
                continue

            findings.append(
                ContinuityGapFinding(
                    gap_type=GapType.REPAIR_MISSING,
                    start_time=event.timestamp,
                    end_time=now,
                    duration_days=duration_days,
                    severity=self._severity(duration_days),
                    reason="Contradiction has no related repair action after the break.",
                    related_event_ids=[event.event_id],
                )
            )

        return findings

    @staticmethod
    def _shares_any_tag(first: MemoryEvent, second: MemoryEvent) -> bool:
        if not first.tags or not second.tags:
            return False
        return bool(set(first.tags).intersection(second.tags))

    @staticmethod
    def _is_identity_relevant(event: MemoryEvent) -> bool:
        return (
            "identity" in event.tags
            or event.event_type in {"identity_synthesis", "reflection"}
            or float(event.metadata.get("identity_relevance", 0.0)) >= 0.7
        )

    def _severity(self, duration_days: int) -> float:
        return round(min(1.0, duration_days / (self.gap_days * 3)), 4)
