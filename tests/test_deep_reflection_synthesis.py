from datetime import datetime, timedelta, timezone

from continuity_core.identity.transition import IdentityTransitionEngine
from continuity_core.memory.event import MemoryEvent
from continuity_core.memory.graph import MemoryGraphBuilder
from continuity_core.reflection.deep_synthesis import DeepReflectionSynthesizer
from continuity_core.temporal.gap_detection import ContinuityGapDetector
from continuity_core.temporal.narrative import TemporalNarrativeEngine


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)
NOW = datetime(2026, 3, 1, tzinfo=timezone.utc)


def make_event(content: str, event_type: str, day: int, tags: list[str]) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_TIME + timedelta(days=day),
        tags=tags,
        importance=0.8,
        metadata={"identity_relevance": 0.8},
    )


def test_deep_reflection_generates_summary() -> None:
    events = [
        make_event("Define continuity goal.", "goal", 0, ["continuity"]),
        make_event("Build continuity module.", "progress", 5, ["continuity", "memory"]),
        make_event("Reflect on continuity direction.", "reflection", 10, ["reflection"]),
    ]

    narrative = TemporalNarrativeEngine().build(events)
    gaps = ContinuityGapDetector(gap_days=20).detect(events, now=NOW)
    identity_report = IdentityTransitionEngine().analyze(events, now=NOW)
    graph = MemoryGraphBuilder().build(events)

    reflection = DeepReflectionSynthesizer().synthesize(
        narrative=narrative,
        gaps=gaps,
        identity_report=identity_report,
        memory_graph=graph,
    )

    assert "Continuity trajectory" in reflection.trajectory_summary
    assert len(reflection.continuity_observations) >= 1
    assert len(reflection.graph_insights) >= 1
    assert len(reflection.recommendations) >= 1


def test_deep_reflection_reports_tensions_when_gaps_exist() -> None:
    events = [
        make_event("Define continuity goal.", "goal", 0, ["continuity"]),
    ]

    narrative = TemporalNarrativeEngine().build(events)
    gaps = ContinuityGapDetector(gap_days=20).detect(events, now=NOW)
    identity_report = IdentityTransitionEngine().analyze(events, now=NOW)
    graph = MemoryGraphBuilder().build(events)

    reflection = DeepReflectionSynthesizer().synthesize(
        narrative=narrative,
        gaps=gaps,
        identity_report=identity_report,
        memory_graph=graph,
    )

    assert len(reflection.unresolved_tensions) >= 1


def test_deep_reflection_detects_identity_direction() -> None:
    events = [
        make_event("Memory architecture note.", "reflection", 0, ["memory"]),
        make_event("Memory architecture follow-up.", "reflection", 1, ["memory"]),
        make_event("Memory architecture refinement.", "reflection", 2, ["memory"]),
    ]

    narrative = TemporalNarrativeEngine().build(events)
    gaps = ContinuityGapDetector(gap_days=20).detect(events, now=NOW)
    identity_report = IdentityTransitionEngine().analyze(events, now=NOW)
    graph = MemoryGraphBuilder().build(events)

    reflection = DeepReflectionSynthesizer().synthesize(
        narrative=narrative,
        gaps=gaps,
        identity_report=identity_report,
        memory_graph=graph,
    )

    assert "memory" in reflection.identity_direction.lower()
