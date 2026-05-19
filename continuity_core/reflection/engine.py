"""Reflection engine for longitudinal continuity synthesis.

The reflection layer transforms raw memory and temporal signals into narrative
summaries, continuity interpretations, and recovery-oriented guidance.
"""

from __future__ import annotations

from dataclasses import dataclass

from continuity_core.identity.model import IdentityClaim, IdentityModel
from continuity_core.memory.event import MemoryEvent
from continuity_core.temporal.reasoner import TemporalReasoner


@dataclass(frozen=True)
class ReflectionSummary:
    """Structured output from a continuity reflection pass."""

    summary: str
    momentum_status: str
    momentum_score: float
    strongest_identity_claims: list[str]
    recurring_themes: list[str]
    unresolved_count: int
    contradiction_count: int
    continuity_gaps: int
    recommendations: list[str]


class ReflectionEngine:
    """Generates continuity-aware reflective summaries."""

    def __init__(self, temporal_reasoner: TemporalReasoner | None = None) -> None:
        self.temporal_reasoner = temporal_reasoner or TemporalReasoner()

    def reflect(
        self,
        events: list[MemoryEvent],
        identity_model: IdentityModel,
    ) -> ReflectionSummary:
        """Generate a structured reflection summary."""
        temporal_report = self.temporal_reasoner.analyze(events)

        strongest_claims = [
            claim.name for claim in identity_model.strongest_claims(threshold=0.5)
        ]

        recurring_themes = list(temporal_report.recurring_tags.keys())[:5]

        recommendations = self._recommendations(
            momentum_status=temporal_report.momentum_status,
            unresolved_count=len(temporal_report.unresolved_events),
            contradiction_count=len(temporal_report.contradiction_events),
            continuity_gap_count=len(temporal_report.continuity_gaps),
        )

        summary = self._build_summary(
            momentum_status=temporal_report.momentum_status,
            momentum_score=temporal_report.momentum_score,
            strongest_claims=strongest_claims,
            recurring_themes=recurring_themes,
            unresolved_count=len(temporal_report.unresolved_events),
            contradiction_count=len(temporal_report.contradiction_events),
            continuity_gap_count=len(temporal_report.continuity_gaps),
        )

        return ReflectionSummary(
            summary=summary,
            momentum_status=temporal_report.momentum_status,
            momentum_score=temporal_report.momentum_score,
            strongest_identity_claims=strongest_claims,
            recurring_themes=recurring_themes,
            unresolved_count=len(temporal_report.unresolved_events),
            contradiction_count=len(temporal_report.contradiction_events),
            continuity_gaps=len(temporal_report.continuity_gaps),
            recommendations=recommendations,
        )

    def _build_summary(
        self,
        momentum_status: str,
        momentum_score: float,
        strongest_claims: list[str],
        recurring_themes: list[str],
        unresolved_count: int,
        contradiction_count: int,
        continuity_gap_count: int,
    ) -> str:
        """Build human-readable continuity narrative."""
        strongest_text = ", ".join(strongest_claims) if strongest_claims else "No strong identity claims detected"
        themes_text = ", ".join(recurring_themes) if recurring_themes else "No recurring themes detected"

        return (
            f"Continuity momentum is currently '{momentum_status}' "
            f"with a score of {momentum_score:.2f}. "
            f"Strong identity themes include: {strongest_text}. "
            f"Recurring themes across memory events: {themes_text}. "
            f"Detected {unresolved_count} unresolved events, "
            f"{contradiction_count} contradictions, and "
            f"{continuity_gap_count} continuity gaps."
        )

    def _recommendations(
        self,
        momentum_status: str,
        unresolved_count: int,
        contradiction_count: int,
        continuity_gap_count: int,
    ) -> list[str]:
        """Generate continuity-oriented recommendations."""
        recommendations: list[str] = []

        if momentum_status in {"weak_momentum", "stalled"}:
            recommendations.append(
                "Reduce active goals into smaller continuity-preserving actions."
            )

        if unresolved_count > 0:
            recommendations.append(
                "Review unresolved commitments and identify the highest-leverage recovery step."
            )

        if contradiction_count > 0:
            recommendations.append(
                "Investigate recurring contradictions between stated priorities and behavior."
            )

        if continuity_gap_count > 0:
            recommendations.append(
                "Generate a continuity recovery brief after inactivity gaps."
            )

        if not recommendations:
            recommendations.append(
                "Momentum is stable. Continue reinforcing high-salience identity-aligned behaviors."
            )

        return recommendations
