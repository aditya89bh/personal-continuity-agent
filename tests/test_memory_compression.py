from datetime import datetime, timedelta, timezone

import pytest

from continuity_core.memory.compression import MemoryCompressor
from continuity_core.memory.event import MemoryEvent


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def build_event(
    content: str,
    event_type: str,
    offset_days: int,
    tags: list[str] | None = None,
    importance: float = 0.7,
) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_TIME + timedelta(days=offset_days),
        tags=tags or [],
        importance=importance,
    )


def test_memory_compression_builds_summary() -> None:
    compressor = MemoryCompressor()

    events = [
        build_event(
            "User begins continuity architecture research.",
            "goal",
            0,
            tags=["continuity", "research"],
        ),
        build_event(
            "User implements identity modeling.",
            "progress",
            5,
            tags=["identity", "continuity"],
        ),
        build_event(
            "User builds temporal reasoning demo.",
            "progress",
            10,
            tags=["temporal", "continuity"],
            importance=0.9,
        ),
    ]

    compressed = compressor.compress(events)

    assert compressed.event_count == 3
    assert compressed.highest_importance == 0.9
    assert "continuity" in compressed.recurring_tags
    assert "progress" in compressed.dominant_event_types
    assert "Compressed 3 events" in compressed.summary


def test_memory_compression_tracks_event_window() -> None:
    compressor = MemoryCompressor()

    events = [
        build_event("Start", "goal", 0),
        build_event("Middle", "progress", 10),
        build_event("End", "reflection", 20),
    ]

    compressed = compressor.compress(events)

    assert compressed.start_time == events[0].timestamp
    assert compressed.end_time == events[-1].timestamp


def test_memory_compression_preserves_source_event_ids() -> None:
    compressor = MemoryCompressor()

    events = [
        build_event("One", "goal", 0),
        build_event("Two", "progress", 1),
    ]

    compressed = compressor.compress(events)

    assert len(compressed.source_event_ids) == 2
    assert compressed.source_event_ids[0] == events[0].event_id


def test_memory_compression_rejects_empty_input() -> None:
    compressor = MemoryCompressor()

    with pytest.raises(ValueError, match="empty event list"):
        compressor.compress([])


def test_memory_compression_rejects_invalid_theme_limit() -> None:
    compressor = MemoryCompressor()

    events = [
        build_event("Test", "goal", 0),
    ]

    with pytest.raises(ValueError, match="greater than zero"):
        compressor.compress(events, max_themes=0)
