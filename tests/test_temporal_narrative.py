from datetime import datetime, timedelta, timezone

import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.temporal.narrative import TemporalNarrativeEngine


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_event(content: str, event_type: str, day: int) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_TIME + timedelta(days=day),
        tags=["continuity"],
        importance=0.8,
    )


def test_narrative_engine_builds_basic_arc() -> None:
    engine = TemporalNarrativeEngine()
    events = [
        make_event("Define continuity goal.", "goal", 0),
        make_event("Implement memory module.", "progress", 1),
        make_event("Reflect on system direction.", "reflection", 2),
    ]

    narrative = engine.build(events)

    assert narrative.arc == "exploration_to_integration"
    assert len(narrative.phases) == 3
    assert "Temporal arc" in narrative.summary


def test_narrative_engine_groups_same_phase() -> None:
    engine = TemporalNarrativeEngine()
    events = [
        make_event("Build module one.", "progress", 0),
        make_event("Build module two.", "project_build", 1),
    ]

    narrative = engine.build(events)

    assert len(narrative.phases) == 1
    assert narrative.phases[0].phase_type == "progress"
    assert narrative.phases[0].event_count == 2


def test_narrative_engine_requires_events() -> None:
    engine = TemporalNarrativeEngine()

    with pytest.raises(ValueError):
        engine.build([])
