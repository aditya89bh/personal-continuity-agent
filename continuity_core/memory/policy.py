"""Memory retention and forgetting policies.

Continuity is not just remembering. A useful continuity system must decide what
should be retained, reinforced, compressed, archived, or allowed to decay.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum

from continuity_core.memory.event import MemoryEvent


class RetentionAction(StrEnum):
    """Possible retention actions for memory events."""

    RETAIN = "retain"
    REINFORCE = "reinforce"
    COMPRESS = "compress"
    ARCHIVE = "archive"
    DECAY = "decay"


@dataclass(frozen=True)
class RetentionDecision:
    """Decision returned by the memory retention policy."""

    event_id: str
    action: RetentionAction
    reason: str
    adjusted_importance: float


class MemoryRetentionPolicy:
    """Rule-based baseline for memory retention decisions."""

    def __init__(self, archive_after_days: int = 90, decay_after_days: int = 30) -> None:
        if archive_after_days <= 0:
            raise ValueError("archive_after_days must be greater than zero")
        if decay_after_days <= 0:
            raise ValueError("decay_after_days must be greater than zero")
        if decay_after_days > archive_after_days:
            raise ValueError("decay_after_days cannot exceed archive_after_days")

        self.archive_after_days = archive_after_days
        self.decay_after_days = decay_after_days

    def decide(self, event: MemoryEvent, now: datetime | None = None) -> RetentionDecision:
        """Decide how a memory event should be retained."""
        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        age_days = max(0, (current_time - event.timestamp).days)

        if self._is_identity_level(event):
            return RetentionDecision(
                event_id=event.event_id,
                action=RetentionAction.REINFORCE,
                reason="identity-level memory should be reinforced",
                adjusted_importance=max(event.importance, 0.85),
            )

        if self._is_unresolved(event):
            return RetentionDecision(
                event_id=event.event_id,
                action=RetentionAction.RETAIN,
                reason="unresolved memory should remain active until resolved",
                adjusted_importance=max(event.importance, 0.75),
            )

        if age_days >= self.archive_after_days:
            return RetentionDecision(
                event_id=event.event_id,
                action=RetentionAction.ARCHIVE,
                reason="event is old and not identity-level or unresolved",
                adjusted_importance=self._decayed_importance(event.importance, age_days),
            )

        if age_days >= self.decay_after_days:
            return RetentionDecision(
                event_id=event.event_id,
                action=RetentionAction.DECAY,
                reason="event is aging and should lose active priority",
                adjusted_importance=self._decayed_importance(event.importance, age_days),
            )

        return RetentionDecision(
            event_id=event.event_id,
            action=RetentionAction.RETAIN,
            reason="recent event remains active",
            adjusted_importance=event.importance,
        )

    def decide_many(
        self,
        events: list[MemoryEvent],
        now: datetime | None = None,
    ) -> list[RetentionDecision]:
        """Return retention decisions for multiple events."""
        return [self.decide(event, now=now) for event in events]

    @staticmethod
    def _is_identity_level(event: MemoryEvent) -> bool:
        return (
            event.event_type in {"identity_synthesis", "reflection"}
            or "identity" in event.tags
            or float(event.metadata.get("identity_relevance", 0.0)) >= 0.85
        )

    @staticmethod
    def _is_unresolved(event: MemoryEvent) -> bool:
        return (
            event.event_type in {"open_loop", "missed_commitment", "unresolved"}
            or "unresolved" in event.tags
            or bool(event.metadata.get("unresolved"))
        )

    @staticmethod
    def _decayed_importance(importance: float, age_days: int) -> float:
        decay_factor = min(0.8, age_days / 180)
        return round(max(0.0, importance * (1.0 - decay_factor)), 4)
