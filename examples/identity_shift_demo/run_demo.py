"""Identity shift demo for the Personal Continuity Agent.

Run from repository root:

    python examples/identity_shift_demo/run_demo.py

This demo shows how the identity model accumulates evidence over time and
surfaces an evolving user identity from repeated memory events.
"""

from __future__ import annotations

from datetime import datetime, timezone

from continuity_core.identity.model import IdentityModel
from continuity_core.memory.event import MemoryEvent
from continuity_core.reflection.engine import ReflectionEngine


def build_identity_shift_events() -> list[MemoryEvent]:
    """Create synthetic events showing identity evolution."""
    return [
        MemoryEvent(
            content="User focuses on robotics deployment and customer demos.",
            event_type="work_focus",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["robotics", "operations", "customer_demos"],
            importance=0.8,
            metadata={"identity_relevance": 0.8, "goal_relevance": 0.7},
        ),
        MemoryEvent(
            content="User studies memory systems and long-horizon AI agents.",
            event_type="research_focus",
            timestamp=datetime(2026, 2, 1, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["agi", "memory", "agents"],
            importance=0.9,
            metadata={"identity_relevance": 1.0, "goal_relevance": 0.9},
        ),
        MemoryEvent(
            content="User starts framing memory as a design material for intelligent systems.",
            event_type="reflection",
            timestamp=datetime(2026, 3, 1, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["memory", "design", "cognitive_architecture"],
            importance=0.9,
            metadata={"identity_relevance": 1.0, "goal_relevance": 0.8},
        ),
        MemoryEvent(
            content="User builds a continuity-aware AI architecture prototype.",
            event_type="project_build",
            timestamp=datetime(2026, 4, 1, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["continuity", "architecture", "agents"],
            importance=0.95,
            metadata={"identity_relevance": 1.0, "goal_relevance": 1.0},
        ),
        MemoryEvent(
            content="User connects embodied AI, robotics memory, and personal continuity into one thesis.",
            event_type="identity_synthesis",
            timestamp=datetime(2026, 5, 1, tzinfo=timezone.utc),
            source="synthetic_demo",
            tags=["embodied_ai", "robotics", "memory", "continuity"],
            importance=1.0,
            metadata={"identity_relevance": 1.0, "goal_relevance": 1.0},
        ),
    ]


def build_identity_model(events: list[MemoryEvent]) -> IdentityModel:
    """Build an identity model from synthetic evidence."""
    model = IdentityModel()

    model.add_claim(
        name="Robotics founder",
        category="professional_identity",
        evidence_event=events[0],
        evidence_strength=0.9,
    )
    model.add_claim(
        name="AGI systems thinker",
        category="professional_identity",
        evidence_event=events[1],
        evidence_strength=1.0,
    )
    model.add_claim(
        name="AGI systems thinker",
        category="professional_identity",
        evidence_event=events[2],
        evidence_strength=1.0,
    )
    model.add_claim(
        name="Cognitive architecture builder",
        category="identity_theme",
        evidence_event=events[2],
        evidence_strength=0.9,
    )
    model.add_claim(
        name="Cognitive architecture builder",
        category="identity_theme",
        evidence_event=events[3],
        evidence_strength=1.0,
    )
    model.add_claim(
        name="Embodied continuity researcher",
        category="identity_theme",
        evidence_event=events[4],
        evidence_strength=1.0,
    )
    model.add_claim(
        name="Embodied continuity researcher",
        category="identity_theme",
        evidence_event=events[4],
        evidence_strength=0.9,
    )

    return model


def main() -> None:
    events = build_identity_shift_events()
    identity_model = build_identity_model(events)
    reflection = ReflectionEngine().reflect(events, identity_model)

    print("Personal Continuity Agent · Identity Shift Demo")
    print("=" * 56)
    print(f"Stored events: {len(events)}")
    print(f"Identity claims: {identity_model.count()}")
    print()

    print("Identity claims by confidence:")
    for claim in identity_model.list_claims():
        print(
            f"- [{claim.confidence:.4f}] {claim.category}: {claim.name} "
            f"({len(claim.evidence)} evidence items)"
        )

    print()
    print("Continuity interpretation:")
    print(reflection.summary)

    print()
    print("Identity shift reading:")
    print(
        "The user begins with a robotics/operator identity, then increasingly "
        "accumulates evidence around AGI systems, cognitive architectures, memory, "
        "and embodied continuity. The model does not erase the robotics identity. "
        "It reframes it as part of a broader continuity-aware AI trajectory."
    )


if __name__ == "__main__":
    main()
