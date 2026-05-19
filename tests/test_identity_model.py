from datetime import datetime, timezone

import pytest

from continuity_core.identity.model import IdentityEvidence, IdentityModel
from continuity_core.memory.event import MemoryEvent


def build_event(content: str) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type="reflection",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        importance=0.8,
    )


def test_identity_evidence_rejects_invalid_strength() -> None:
    with pytest.raises(ValueError, match="strength must be between"):
        IdentityEvidence(
            event_id="abc",
            content="Evidence",
            timestamp=datetime.now(timezone.utc),
            strength=1.5,
        )


def test_identity_model_creates_claim_from_event() -> None:
    model = IdentityModel()
    event = build_event("User repeatedly returns to AGI research and systems thinking.")

    claim = model.add_claim(
        name="Systems-oriented thinker",
        category="cognitive_style",
        evidence_event=event,
        evidence_strength=0.9,
    )

    assert model.count() == 1
    assert claim.name == "Systems-oriented thinker"
    assert claim.category == "cognitive_style"
    assert claim.confidence == 0.3
    assert len(claim.evidence) == 1


def test_identity_model_accumulates_evidence() -> None:
    model = IdentityModel()

    event_one = build_event("User studies cognitive architectures.")
    event_two = build_event("User writes about long-term memory systems.")
    event_three = build_event("User builds continuity agent prototypes.")

    model.add_claim(
        name="AGI systems builder",
        category="identity_theme",
        evidence_event=event_one,
        evidence_strength=1.0,
    )
    model.add_claim(
        name="AGI systems builder",
        category="identity_theme",
        evidence_event=event_two,
        evidence_strength=1.0,
    )
    claim = model.add_claim(
        name="AGI systems builder",
        category="identity_theme",
        evidence_event=event_three,
        evidence_strength=1.0,
    )

    assert model.count() == 1
    assert len(claim.evidence) == 3
    assert claim.confidence == 1.0


def test_identity_model_returns_claims_by_category() -> None:
    model = IdentityModel()

    model.add_claim(
        name="Reflective",
        category="trait",
        evidence_event=build_event("User journals weekly."),
    )
    model.add_claim(
        name="Research-driven",
        category="trait",
        evidence_event=build_event("User reads research papers daily."),
    )
    model.add_claim(
        name="Long-term thinking",
        category="value",
        evidence_event=build_event("User prioritizes long-horizon goals."),
    )

    trait_claims = model.claims_by_category("trait")

    assert len(trait_claims) == 2
    assert all(claim.category == "trait" for claim in trait_claims)


def test_identity_model_returns_strongest_claims() -> None:
    model = IdentityModel()

    weak = build_event("Minor signal")
    strong = build_event("Strong repeated signal")

    model.add_claim(
        name="Occasional writer",
        category="behavior",
        evidence_event=weak,
        evidence_strength=0.5,
    )

    model.add_claim(
        name="Research-oriented",
        category="identity_theme",
        evidence_event=strong,
        evidence_strength=1.0,
    )
    model.add_claim(
        name="Research-oriented",
        category="identity_theme",
        evidence_event=strong,
        evidence_strength=1.0,
    )
    model.add_claim(
        name="Research-oriented",
        category="identity_theme",
        evidence_event=strong,
        evidence_strength=1.0,
    )

    strongest = model.strongest_claims()

    assert len(strongest) == 1
    assert strongest[0].name == "Research-oriented"


def test_identity_model_rejects_invalid_threshold() -> None:
    model = IdentityModel()

    with pytest.raises(ValueError, match="threshold must be between"):
        model.strongest_claims(1.5)
