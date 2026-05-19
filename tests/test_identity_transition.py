from datetime import datetime, timedelta, timezone

import pytest

from continuity_core.identity.transition import IdentityTransitionEngine
from continuity_core.memory.event import MemoryEvent


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)
NOW = datetime(2026, 3, 1, tzinfo=timezone.utc)


def make_event(
    content: str,
    day: int,
    tags: list[str],
    importance: float = 0.8,
    identity_relevance: float = 0.8,
    event_type: str = "reflection",
) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_TIME + timedelta(days=day),
        tags=tags,
        importance=importance,
        metadata={"identity_relevance": identity_relevance},
    )


def test_identity_transition_detects_stable_theme() -> None:
    engine = IdentityTransitionEngine(quiet_after_days=45)
    events = [
        make_event("Memory systems note one.", 40, ["memory"]),
        make_event("Memory systems note two.", 42, ["memory"]),
        make_event("Memory systems note three.", 44, ["memory"]),
    ]

    report = engine.analyze(events, now=NOW)

    assert len(report.stable_themes) >= 1
    assert report.stable_themes[0].theme == "memory"


def test_identity_transition_detects_new_theme() -> None:
    engine = IdentityTransitionEngine(quiet_after_days=45)
    events = [
        make_event("New design note.", 55, ["design"], importance=0.5, identity_relevance=0.4),
    ]

    report = engine.analyze(events, now=NOW)

    assert len(report.new_themes) == 1
    assert report.new_themes[0].theme == "design"


def test_identity_transition_detects_quiet_theme() -> None:
    engine = IdentityTransitionEngine(quiet_after_days=30)
    events = [
        make_event("Robotics identity note.", 0, ["robotics"]),
    ]

    report = engine.analyze(events, now=NOW)

    assert len(report.quiet_themes) == 1
    assert report.quiet_themes[0].theme == "robotics"


def test_identity_transition_ignores_non_identity_events() -> None:
    engine = IdentityTransitionEngine()
    events = [
        MemoryEvent(
            content="Low relevance status update.",
            event_type="note",
            timestamp=BASE_TIME,
            tags=["misc"],
            importance=0.4,
            metadata={"identity_relevance": 0.0},
        )
    ]

    report = engine.analyze(events, now=NOW)

    assert report.new_themes == []
    assert report.stable_themes == []
    assert report.quiet_themes == []


def test_identity_transition_requires_timezone_aware_now() -> None:
    engine = IdentityTransitionEngine()

    with pytest.raises(ValueError):
        engine.analyze([], now=datetime(2026, 1, 1))
