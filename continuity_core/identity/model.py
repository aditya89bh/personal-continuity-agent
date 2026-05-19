"""Identity model for long-term personal continuity.

The identity layer tracks evidence-backed traits, values, motivations, and
behavioral tendencies. It should not be treated as a fixed personality profile.
Every identity claim should remain inspectable and tied to supporting evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from continuity_core.memory.event import MemoryEvent


@dataclass(frozen=True)
class IdentityEvidence:
    """Evidence linking an identity claim to a memory event."""

    event_id: str
    content: str
    timestamp: datetime
    strength: float = 1.0

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("IdentityEvidence event_id cannot be empty.")
        if not self.content.strip():
            raise ValueError("IdentityEvidence content cannot be empty.")
        if self.timestamp.tzinfo is None:
            raise ValueError("IdentityEvidence timestamp must be timezone-aware.")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("IdentityEvidence strength must be between 0.0 and 1.0.")


@dataclass
class IdentityClaim:
    """A single identity-level claim backed by evidence."""

    name: str
    category: str
    confidence: float = 0.0
    evidence: list[IdentityEvidence] = field(default_factory=list)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("IdentityClaim name cannot be empty.")
        if not self.category.strip():
            raise ValueError("IdentityClaim category cannot be empty.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("IdentityClaim confidence must be between 0.0 and 1.0.")
        if self.updated_at.tzinfo is None:
            raise ValueError("IdentityClaim updated_at must be timezone-aware.")

    def add_evidence(self, evidence: IdentityEvidence) -> None:
        """Attach evidence and update confidence."""
        self.evidence.append(evidence)
        self.updated_at = datetime.now(timezone.utc)
        self.confidence = self._calculate_confidence()

    def _calculate_confidence(self) -> float:
        """Calculate confidence from accumulated evidence.

        This simple baseline saturates as evidence accumulates. Later versions
        can account for contradiction, decay, recency, source quality, and user
        correction.
        """
        if not self.evidence:
            return 0.0
        total_strength = sum(item.strength for item in self.evidence)
        return round(min(1.0, total_strength / 3.0), 4)


class IdentityModel:
    """Evidence-backed model of user identity claims."""

    def __init__(self) -> None:
        self._claims: dict[str, IdentityClaim] = {}

    def add_claim(
        self,
        name: str,
        category: str,
        evidence_event: MemoryEvent,
        evidence_strength: float = 1.0,
    ) -> IdentityClaim:
        """Add or update an identity claim using a MemoryEvent as evidence."""
        key = self._claim_key(name=name, category=category)
        claim = self._claims.get(key)
        if claim is None:
            claim = IdentityClaim(name=name, category=category)
            self._claims[key] = claim

        claim.add_evidence(
            IdentityEvidence(
                event_id=evidence_event.event_id,
                content=evidence_event.content,
                timestamp=evidence_event.timestamp,
                strength=evidence_strength,
            )
        )
        return claim

    def get_claim(self, name: str, category: str) -> IdentityClaim | None:
        """Return a claim by name and category."""
        return self._claims.get(self._claim_key(name=name, category=category))

    def list_claims(self) -> list[IdentityClaim]:
        """Return all identity claims sorted by confidence, highest first."""
        return sorted(self._claims.values(), key=lambda claim: claim.confidence, reverse=True)

    def claims_by_category(self, category: str) -> list[IdentityClaim]:
        """Return all claims in a category."""
        return [claim for claim in self.list_claims() if claim.category == category]

    def strongest_claims(self, threshold: float = 0.7) -> list[IdentityClaim]:
        """Return claims with confidence greater than or equal to threshold."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")
        return [claim for claim in self.list_claims() if claim.confidence >= threshold]

    def count(self) -> int:
        """Return number of identity claims."""
        return len(self._claims)

    @staticmethod
    def _claim_key(name: str, category: str) -> str:
        """Normalize identity claim key."""
        return f"{category.strip().lower()}::{name.strip().lower()}"
