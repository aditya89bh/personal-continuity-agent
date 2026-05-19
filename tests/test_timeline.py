from datetime import datetime, timedelta, timezone

import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.temporal.timeline import TimelineBuilder


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def build_event(
    content: str,
    event_type: str,
    offset_days: int,
    importance: float,
) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_TIME + timedelta(days=offset_days),
        tags=["continuity"],
        importance=importance,
    )


def test_timeline_groups_events_by_day() -> None:
    builder = TimelineBuilder()

    events = [
        build_event("Start", "goal", 0, 0.9),
        build_event("Progress", "progress", 0, 0.8),
        build_event("Reflection", "reflection", 1, 0.7),
    ]

    timeline = builder.build(events)

    assert len(timeline) == 2
    assert len(timeline[0].events) == 2


def test_timeline_orders_by_salience() -> None:
    builder = TimelineBuilder()

    low = build_event("Low", "note", 0, 0.3)
    high = build_event("High", "reflection", 0, 0.9)

    timeline = builder.build([low, high])

    assert timeline[0].events[0].content == "High"


def test_high_salience_items_filtering() -> None:
    builder = TimelineBuilder()

    low = build_event("Low", "note", 0, 0.2)
    high = build_event("High", "reflection", 0, 0.95)

    items = builder.high_salience_items([low, high], threshold=0.7)

    assert len(items) == 1
    assert items[0].content == "High"


def test_invalid_salience_threshold_rejected() -> None:
    builder = TimelineBuilder()

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        builder.high_salience_items([], threshold=2.0)
