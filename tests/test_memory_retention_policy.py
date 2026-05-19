from datetime import datetime, timedelta, timezone

import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.memory.policy import (
    MemoryRetentionPolicy,
    RetentionAction,
)


BASE_NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


def build_event(
    content: str,
    event_type: str,
    days_old: int,
    tags: list[str] | None = None,
    metadata: dict | None = None,
    importance: float = 0.7,
) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_NOW - timedelta(days=days_old),
        tags=tags or [],
        metadata=metadata or {},
        importance=importance,
    )


def test_recent_event_is_retained() -> None:
    policy = MemoryRetentionPolicy()

    event = build_event(
        "Recent project update",
        "progress",
        days_old=5,
    )

    decision = policy.decide(event, now=BASE_NOW)

    assert decision.action == RetentionAction.RETAIN
    assert decision.adjusted_importance == event.importance


def test_identity_level_event_is_reinforced() -> None:
    policy = MemoryRetentionPolicy()

    event = build_event(
        "Identity-level realization",
        "reflection",
        days_old=120,
        metadata={"identity_relevance": 1.0},
        importance=0.6,
    )

    decision = policy.decide(event, now=BASE_NOW)

    assert decision.action == RetentionAction.REINFORCE
    assert decision.adjusted_importance >= 0.85


def test_unresolved_event_remains_active() -> None:
    policy = MemoryRetentionPolicy()

    event = build_event(
        "Unfinished continuity module",
        "open_loop",
        days_old=80,
        tags=["unresolved"],
    )

    decision = policy.decide(event, now=BASE_NOW)

    assert decision.action == RetentionAction.RETAIN
    assert "unresolved" in decision.reason


def test_old_noncritical_event_is_archived() -> None:
    policy = MemoryRetentionPolicy(archive_after_days=90)

    event = build_event(
        "Old low-signal status update",
        "status_update",
        days_old=120,
        importance=0.5,
    )

    decision = policy.decide(event, now=BASE_NOW)

    assert decision.action == RetentionAction.ARCHIVE
    assert decision.adjusted_importance < event.importance


def test_mid_age_event_decays() -> None:
    policy = MemoryRetentionPolicy(decay_after_days=30)

    event = build_event(
        "Intermediate memory",
        "note",
        days_old=45,
        importance=0.8,
    )

    decision = policy.decide(event, now=BASE_NOW)

    assert decision.action == RetentionAction.DECAY
    assert decision.adjusted_importance < event.importance


def test_policy_rejects_invalid_thresholds() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        MemoryRetentionPolicy(archive_after_days=0)

    with pytest.raises(ValueError, match="greater than zero"):
        MemoryRetentionPolicy(decay_after_days=0)

    with pytest.raises(ValueError, match="cannot exceed"):
        MemoryRetentionPolicy(archive_after_days=30, decay_after_days=90)
