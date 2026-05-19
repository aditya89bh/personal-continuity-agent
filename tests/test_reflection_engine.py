from datetime import datetime, timezone

from continuity_core.identity.model import IdentityModel
from continuity_core.memory.event import MemoryEvent
from continuity_core.reflection.engine import ReflectionEngine


def build_event(
    content: str,
    event_type: str,
    day: int,
    tags: list[str] | None = None,
    metadata: dict | None = None,
    importance: float = 0.8,
) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=datetime(2026, 1, day, tzinfo=timezone.utc),
        tags=tags or [],
        metadata=metadata or {},
        importance=importance,
    )


def test_reflection_engine_generates_summary() -> None:
    identity_model = IdentityModel()

    event = build_event(
        "User repeatedly returns to AGI systems thinking.",
        "reflection",
        1,
        tags=["agi", "systems"],
    )

    identity_model.add_claim(
        name="Systems thinker",
        category="identity_theme",
        evidence_event=event,
        evidence_strength=1.0,
    )
    identity_model.add_claim(
        name="Systems thinker",
        category="identity_theme",
        evidence_event=event,
        evidence_strength=1.0,
    )

    events = [
        build_event("Research goal", "goal", 1, tags=["agi"]),
        build_event("Progress", "progress", 2, tags=["agi", "systems"]),
        build_event(
            "Missed commitment",
            "missed_commitment",
            3,
            tags=["agi", "unresolved"],
        ),
    ]

    engine = ReflectionEngine()
    reflection = engine.reflect(events, identity_model)

    assert "Continuity momentum" in reflection.summary
    assert reflection.momentum_score >= 0.0
    assert "Systems thinker" in reflection.strongest_identity_claims
    assert "agi" in reflection.recurring_themes
    assert reflection.unresolved_count == 1


def test_reflection_engine_generates_recovery_recommendations() -> None:
    identity_model = IdentityModel()

    events = [
        build_event("Goal", "goal", 1),
        build_event("Contradiction", "contradiction", 2, tags=["contradiction"]),
        build_event("Open loop", "open_loop", 3, tags=["unresolved"]),
    ]

    engine = ReflectionEngine()
    reflection = engine.reflect(events, identity_model)

    assert len(reflection.recommendations) >= 2
    assert any("contradictions" in recommendation for recommendation in reflection.recommendations)
    assert any("unresolved" in recommendation for recommendation in reflection.recommendations)


def test_reflection_engine_handles_empty_identity_model() -> None:
    identity_model = IdentityModel()

    events = [
        build_event("Initial goal", "goal", 1),
        build_event("Progress", "progress", 2),
    ]

    engine = ReflectionEngine()
    reflection = engine.reflect(events, identity_model)

    assert reflection.strongest_identity_claims == []
    assert reflection.momentum_status in {
        "strong_momentum",
        "moderate_momentum",
        "weak_momentum",
        "stalled",
    }


def test_reflection_engine_generates_stability_recommendation() -> None:
    identity_model = IdentityModel()

    event = build_event("Consistent progress", "progress", 1)

    identity_model.add_claim(
        name="Research-oriented",
        category="identity_theme",
        evidence_event=event,
        evidence_strength=1.0,
    )
    identity_model.add_claim(
        name="Research-oriented",
        category="identity_theme",
        evidence_event=event,
        evidence_strength=1.0,
    )
    identity_model.add_claim(
        name="Research-oriented",
        category="identity_theme",
        evidence_event=event,
        evidence_strength=1.0,
    )

    events = [
        build_event("Goal", "goal", 1),
        build_event("Progress", "progress", 2),
        build_event("More progress", "progress", 3),
    ]

    engine = ReflectionEngine()
    reflection = engine.reflect(events, identity_model)

    assert any("Momentum is stable" in recommendation for recommendation in reflection.recommendations)
