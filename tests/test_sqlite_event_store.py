from datetime import datetime, timezone

import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.memory.sqlite_store import SQLiteEventStore


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def build_event(content: str, event_type: str) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_TIME,
        tags=["continuity"],
        importance=0.8,
    )


@pytest.fixture

def sqlite_store(tmp_path):
    db_path = tmp_path / "continuity_test.db"
    return SQLiteEventStore(db_path=db_path)


def test_sqlite_store_persists_event(sqlite_store: SQLiteEventStore) -> None:
    event = build_event(
        "User begins continuity research.",
        "goal",
    )

    sqlite_store.add(event)

    retrieved = sqlite_store.get(event.event_id)

    assert retrieved is not None
    assert retrieved.content == event.content
    assert retrieved.event_type == event.event_type


def test_sqlite_store_lists_all_events(sqlite_store: SQLiteEventStore) -> None:
    first = build_event("First", "goal")
    second = build_event("Second", "progress")

    sqlite_store.add(first)
    sqlite_store.add(second)

    events = sqlite_store.list_all()

    assert len(events) == 2


def test_sqlite_store_filters_by_type(sqlite_store: SQLiteEventStore) -> None:
    sqlite_store.add(build_event("Goal", "goal"))
    sqlite_store.add(build_event("Progress", "progress"))
    sqlite_store.add(build_event("Another goal", "goal"))

    goals = sqlite_store.filter_by_type("goal")

    assert len(goals) == 2
    assert all(event.event_type == "goal" for event in goals)


def test_sqlite_store_counts_events(sqlite_store: SQLiteEventStore) -> None:
    sqlite_store.add(build_event("One", "goal"))
    sqlite_store.add(build_event("Two", "progress"))

    assert sqlite_store.count() == 2


def test_sqlite_store_rejects_duplicate_event_ids(sqlite_store: SQLiteEventStore) -> None:
    event = build_event("Duplicate", "goal")

    sqlite_store.add(event)

    with pytest.raises(ValueError, match="already exists"):
        sqlite_store.add(event)


def test_sqlite_store_clears_events(sqlite_store: SQLiteEventStore) -> None:
    sqlite_store.add(build_event("One", "goal"))
    sqlite_store.add(build_event("Two", "progress"))

    sqlite_store.clear()

    assert sqlite_store.count() == 0
