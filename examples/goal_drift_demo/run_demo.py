"""Goal drift demo for the Personal Continuity Agent.

Run from repository root:

    python examples/goal_drift_demo/run_demo.py

This demo creates a synthetic timeline of user events, scores their salience,
and surfaces early signals of goal drift.
"""

from __future__ import annotations

from datetime import datetime, timezone

from continuity_core.memory.event import MemoryEvent
from continuity_core.memory.store import InMemoryEventStore
from continuity_core.salience.scorer import SalienceScorer


def build_demo_events() -> list[MemoryEvent]:
    """Create synthetic events for a goal drift scenario."""
    return [
        MemoryEvent(
            content="User commits to publishing one AGI research note every week.",
            event_type="goal",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["agi", "writing", "goal"],
            importance=0.9,
            metadata={
                "goal_relevance": 1.0,
                "identity_relevance": 0.8,
                "unresolved_tension": 0.2,
            },
        ),
        MemoryEvent(
            content="User publishes the first AGI research note.",
            event_type="progress",
            timestamp=datetime(2026, 1, 7, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["agi", "writing", "progress"],
            importance=0.7,
            metadata={
                "goal_relevance": 0.9,
                "identity_relevance": 0.6,
                "unresolved_tension": 0.0,
            },
        ),
        MemoryEvent(
            content="User skips the second weekly note because of scattered priorities.",
            event_type="missed_commitment",
            timestamp=datetime(2026, 1, 14, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["agi", "writing", "drift"],
            importance=0.8,
            metadata={
                "emotional_intensity": 0.4,
                "goal_relevance": 1.0,
                "identity_relevance": 0.7,
                "unresolved_tension": 0.8,
            },
        ),
        MemoryEvent(
            content="User says the research practice still matters but keeps moving it behind other tasks.",
            event_type="contradiction",
            timestamp=datetime(2026, 1, 21, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["agi", "writing", "drift", "contradiction"],
            importance=0.85,
            metadata={
                "emotional_intensity": 0.6,
                "goal_relevance": 1.0,
                "identity_relevance": 0.9,
                "unresolved_tension": 1.0,
            },
        ),
    ]


def detect_goal_drift(events: list[MemoryEvent]) -> dict[str, object]:
    """Detect basic goal drift signals from event types and tags."""
    drift_events = [event for event in events if "drift" in event.tags]
    contradiction_events = [event for event in events if event.event_type == "contradiction"]
    progress_events = [event for event in events if event.event_type == "progress"]

    drift_score = min(1.0, (len(drift_events) * 0.35) + (len(contradiction_events) * 0.3))

    if drift_score >= 0.7:
        status = "high_drift_risk"
    elif drift_score >= 0.35:
        status = "moderate_drift_risk"
    else:
        status = "low_drift_risk"

    return {
        "status": status,
        "drift_score": round(drift_score, 2),
        "progress_events": len(progress_events),
        "drift_events": len(drift_events),
        "contradictions": len(contradiction_events),
    }


def main() -> None:
    store = InMemoryEventStore(build_demo_events())
    scorer = SalienceScorer()
    ranked_events = scorer.rank(store.list_all())
    drift_report = detect_goal_drift(store.list_all())

    print("Personal Continuity Agent · Goal Drift Demo")
    print("=" * 52)
    print(f"Stored events: {store.count()}")
    print(f"Goal drift status: {drift_report['status']}")
    print(f"Goal drift score: {drift_report['drift_score']}")
    print(f"Progress events: {drift_report['progress_events']}")
    print(f"Drift events: {drift_report['drift_events']}")
    print(f"Contradictions: {drift_report['contradictions']}")
    print()
    print("Most salient events:")

    for event, score in ranked_events:
        print(f"- [{score:.4f}] {event.timestamp.date()} · {event.event_type}: {event.content}")

    print()
    print("Continuity recovery brief:")
    print(
        "The user still identifies with the AGI research goal, but repeated missed "
        "commitments and explicit contradiction suggest the goal is at risk of decay. "
        "Recommended next action: reduce the weekly note into a smaller 30-minute "
        "research log to preserve continuity and rebuild momentum."
    )


if __name__ == "__main__":
    main()
