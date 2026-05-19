"""Continuity recovery demo for the Personal Continuity Agent.

Run from repository root:

    python examples/continuity_recovery_demo/run_demo.py

This demo simulates a user returning after a long inactivity gap. The system
reconstructs active goals, unresolved loops, identity themes, and momentum.
"""

from __future__ import annotations

from datetime import datetime, timezone

from continuity_core.identity.model import IdentityModel
from continuity_core.memory.event import MemoryEvent
from continuity_core.reflection.engine import ReflectionEngine
from continuity_core.temporal.reasoner import TemporalReasoner


def build_recovery_events() -> list[MemoryEvent]:
    """Create synthetic events with a long continuity gap."""
    return [
        MemoryEvent(
            content="User commits to building a personal continuity agent repo.",
            event_type="goal",
            timestamp=datetime(2026, 1, 5, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["repo", "continuity", "agent", "goal"],
            importance=0.95,
            metadata={"goal_relevance": 1.0, "identity_relevance": 0.9},
        ),
        MemoryEvent(
            content="User starts implementing memory, salience, identity, and temporal modules.",
            event_type="progress",
            timestamp=datetime(2026, 1, 12, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["repo", "implementation", "continuity"],
            importance=0.85,
            metadata={"goal_relevance": 1.0, "identity_relevance": 0.8},
        ),
        MemoryEvent(
            content="User leaves reflection demo unfinished before switching priorities.",
            event_type="open_loop",
            timestamp=datetime(2026, 1, 20, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["repo", "reflection", "unresolved"],
            importance=0.8,
            metadata={"unresolved": True, "goal_relevance": 0.9, "unresolved_tension": 0.8},
        ),
        MemoryEvent(
            content="User returns after a long pause and asks what should be picked up next.",
            event_type="return_after_gap",
            timestamp=datetime(2026, 4, 25, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["return", "continuity_recovery", "repo"],
            importance=0.9,
            metadata={"goal_relevance": 1.0, "identity_relevance": 0.8},
        ),
    ]


def build_recovery_identity_model(events: list[MemoryEvent]) -> IdentityModel:
    """Build identity model from pre-gap and post-gap evidence."""
    model = IdentityModel()

    model.add_claim(
        name="Continuity systems builder",
        category="identity_theme",
        evidence_event=events[0],
        evidence_strength=1.0,
    )
    model.add_claim(
        name="Continuity systems builder",
        category="identity_theme",
        evidence_event=events[1],
        evidence_strength=1.0,
    )
    model.add_claim(
        name="Agent architecture researcher",
        category="professional_identity",
        evidence_event=events[1],
        evidence_strength=0.9,
    )
    model.add_claim(
        name="Agent architecture researcher",
        category="professional_identity",
        evidence_event=events[3],
        evidence_strength=0.8,
    )

    return model


def generate_recovery_brief(events: list[MemoryEvent], identity_model: IdentityModel) -> str:
    """Generate a compact continuity recovery brief."""
    reasoner = TemporalReasoner(inactivity_gap_days=30)
    report = reasoner.analyze(events, now=datetime(2026, 4, 25, tzinfo=timezone.utc))
    strongest_claims = [claim.name for claim in identity_model.strongest_claims(threshold=0.5)]
    unresolved = report.unresolved_events
    recurring = list(report.recurring_tags.keys())[:4]

    unresolved_text = unresolved[0].content if unresolved else "No unresolved loop detected."
    identity_text = ", ".join(strongest_claims) if strongest_claims else "No strong identity theme detected."
    recurring_text = ", ".join(recurring) if recurring else "No recurring themes detected."

    return (
        "Recovery Brief:\n"
        f"- Identity context: {identity_text}\n"
        f"- Recurring themes: {recurring_text}\n"
        f"- Continuity gaps detected: {len(report.continuity_gaps)}\n"
        f"- Main unresolved loop: {unresolved_text}\n"
        "- Recommended restart: finish the reflection demo, capture output, then update README with demo results."
    )


def main() -> None:
    events = build_recovery_events()
    identity_model = build_recovery_identity_model(events)
    reflection = ReflectionEngine(TemporalReasoner(inactivity_gap_days=30)).reflect(events, identity_model)
    recovery_brief = generate_recovery_brief(events, identity_model)

    print("Personal Continuity Agent · Continuity Recovery Demo")
    print("=" * 63)
    print(f"Stored events: {len(events)}")
    print(f"Identity claims: {identity_model.count()}")
    print(f"Momentum status: {reflection.momentum_status}")
    print(f"Continuity gaps: {reflection.continuity_gaps}")
    print(f"Unresolved events: {reflection.unresolved_count}")
    print()
    print(reflection.summary)
    print()
    print(recovery_brief)


if __name__ == "__main__":
    main()
