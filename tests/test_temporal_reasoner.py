from datetime import datetime, timedelta, timezone

import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.temporal.reasoner import TemporalReasoner


def build_event(
    content: str,
    event_type: str,
    day_offset: int,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> MemoryEvent:
    base_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=base_date + timedelta(days=day_offset - 1),
        tags=tags or [],
        metadata=metadata or {},
        importance=0.7,
    )


def test_temporal_reasoner_detects_recurring_tags() -> None:
    events = [
        build_event("Goal 1", "goal", 1, tags=["agi", "writing"]),
        build_event("Goal 2", "goal", 2, tags=["agi"]),
        build_event("Progress", "progress", 3, tags=["writing"]),
    ]

    reasoner = TemporalReasoner()
    recurring = reasoner.detect_recurring_tags(events)

    assert recurring == {"agi": 2, "writing": 2}


def test_temporal_reasoner_detects_continuity_gaps() -> None:
    events = [
        build_event("Start", "goal", 1),
        build_event("Long pause", "note", 20),
        build_event("Return", "progress", 70),
    ]

    reasoner = TemporalReasoner(inactivity_gap_days=30)
    gaps = reasoner.detect_continuity_gaps(events)

    assert len(gaps) == 1
    assert gaps[0].gap_days == 50


def test_temporal_reasoner_detects_unresolved_events() -> None:
    events = [
        build_event("Open issue", "open_loop", 1),
        build_event("Missed commitment", "missed_commitment", 2),
        build_event("Tagged unresolved", "note", 3, tags=["unresolved"]),
        build_event("Metadata unresolved", "note", 4, metadata={"unresolved": True}),
    ]

    reasoner = TemporalReasoner()
    unresolved = reasoner.detect_unresolved_events(events)

    assert len(unresolved) == 4


def test_temporal_reasoner_detects_contradictions() -> None:
    events = [
        build_event("Normal goal", "goal", 1),
        build_event("Behavior contradiction", "contradiction", 2),
        build_event("Tagged contradiction", "note", 3, tags=["contradiction"]),
    ]

    reasoner = TemporalReasoner()
    contradictions = reasoner.detect_contradictions(events)

    assert len(contradictions) == 2


def test_temporal_reasoner_calculates_momentum() -> None:
    events = [
        build_event("New goal", "goal", 1),
        build_event("Progress", "progress", 2),
        build_event("More progress", "progress", 3),
    ]

    reasoner = TemporalReasoner()

    score = reasoner.momentum_score(
        events,
        now=datetime(2026, 1, 10, tzinfo=timezone.utc),
    )

    assert score > 0.7
    assert reasoner.momentum_status(events, now=datetime(2026, 1, 10, tzinfo=timezone.utc)) == "strong_momentum"


def test_temporal_reasoner_detects_stalled_momentum() -> None:
    events = [
        build_event("Goal", "goal", 1),
        build_event("Missed commitment", "missed_commitment", 2),
        build_event("Contradiction", "contradiction", 3, tags=["contradiction"]),
    ]

    reasoner = TemporalReasoner()

    score = reasoner.momentum_score(
        events,
        now=datetime(2026, 5, 1, tzinfo=timezone.utc),
    )

    assert score == 0.0
    assert reasoner.momentum_status(events, now=datetime(2026, 5, 1, tzinfo=timezone.utc)) == "stalled"


def test_temporal_reasoner_rejects_invalid_gap_threshold() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        TemporalReasoner(inactivity_gap_days=0)


def test_temporal_reasoner_rejects_invalid_recurring_threshold() -> None:
    reasoner = TemporalReasoner()

    with pytest.raises(ValueError, match="greater than zero"):
        reasoner.detect_recurring_tags([], minimum_count=0)
