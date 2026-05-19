from datetime import datetime, timezone

import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.memory.store import InMemoryEventStore


def test_memory_event_serializes_and_deserializes() -> None:
    event = MemoryEvent(
        content="User committed to writing one research note per week.",
        event_type="commitment",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        source="journal",
        tags=["research", "writing"],
        importance=0.8,
        metadata={"goal": "weekly research notes"},
    )

    restored = MemoryEvent.from_dict(event.to_dict())

    assert restored.event_id == event.event_id
    assert restored.content == event.content
    assert restored.event_type == "commitment"
    assert restored.tags == ["research", "writing"]
    assert restored.importance == 0.8
    assert restored.metadata["goal"] == "weekly research notes"


def test_memory_event_rejects_empty_content() -> None:
    with pytest.raises(ValueError, match="content cannot be empty"):
        MemoryEvent(content="   ", event_type="goal")


def test_memory_event_rejects_invalid_importance() -> None:
    with pytest.raises(ValueError, match="importance must be between"):
        MemoryEvent(content="Important event", event_type="goal", importance=1.5)


def test_store_adds_and_retrieves_events() -> None:
    store = InMemoryEventStore()
    event = MemoryEvent(content="User started an AGI reading plan.", event_type="goal")

    store.add(event)

    assert store.count() == 1
    assert store.get(event.event_id) == event


def test_store_rejects_duplicate_event_ids() -> None:
    event = MemoryEvent(content="User made a decision.", event_type="decision")
    store = InMemoryEventStore([event])

    with pytest.raises(ValueError, match="Event already exists"):
        store.add(event)


def test_store_filters_by_type_and_tag() -> None:
    goal = MemoryEvent(
        content="User wants to build a continuity agent repo.",
        event_type="goal",
        tags=["repo", "agent"],
    )
    decision = MemoryEvent(
        content="User chose to start with event memory.",
        event_type="decision",
        tags=["repo", "architecture"],
    )
    store = InMemoryEventStore([goal, decision])

    assert store.filter_by_type("goal") == [goal]
    assert store.filter_by_tag("architecture") == [decision]
    assert store.filter_by_tag("repo") == [goal, decision]


def test_store_returns_high_importance_events() -> None:
    low = MemoryEvent(content="Minor note", event_type="note", importance=0.2)
    high = MemoryEvent(content="Major strategic decision", event_type="decision", importance=0.9)
    store = InMemoryEventStore([low, high])

    assert store.high_importance() == [high]


def test_store_rejects_invalid_importance_threshold() -> None:
    store = InMemoryEventStore()

    with pytest.raises(ValueError, match="threshold must be between"):
        store.high_importance(1.2)
