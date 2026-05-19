"""Salience scoring for continuity events.

Salience estimates how much an event should matter to the continuity engine.
It is not the same as raw importance. Importance may be user-provided.
Salience combines multiple signals that affect whether memory should be
retrieved, reflected on, reinforced, or escalated.
"""

from __future__ import annotations

from dataclasses import dataclass

from continuity_core.memory.event import MemoryEvent


@dataclass(frozen=True)
class SalienceWeights:
    """Weights used by the salience scorer."""

    importance: float = 0.35
    emotional_intensity: float = 0.20
    goal_relevance: float = 0.20
    identity_relevance: float = 0.15
    unresolved_tension: float = 0.10

    def total(self) -> float:
        """Return total configured weight."""
        return (
            self.importance
            + self.emotional_intensity
            + self.goal_relevance
            + self.identity_relevance
            + self.unresolved_tension
        )


class SalienceScorer:
    """Deterministic salience scorer for MemoryEvent objects."""

    def __init__(self, weights: SalienceWeights | None = None) -> None:
        self.weights = weights or SalienceWeights()
        if self.weights.total() <= 0:
            raise ValueError("SalienceWeights total must be greater than zero.")

    def score(self, event: MemoryEvent) -> float:
        """Return a salience score between 0.0 and 1.0."""
        metadata = event.metadata

        raw_score = (
            self.weights.importance * event.importance
            + self.weights.emotional_intensity * self._bounded(metadata.get("emotional_intensity", 0.0))
            + self.weights.goal_relevance * self._bounded(metadata.get("goal_relevance", 0.0))
            + self.weights.identity_relevance * self._bounded(metadata.get("identity_relevance", 0.0))
            + self.weights.unresolved_tension * self._bounded(metadata.get("unresolved_tension", 0.0))
        )

        normalized = raw_score / self.weights.total()
        return round(self._bounded(normalized), 4)

    def rank(self, events: list[MemoryEvent]) -> list[tuple[MemoryEvent, float]]:
        """Return events ranked by salience score, highest first."""
        scored = [(event, self.score(event)) for event in events]
        return sorted(scored, key=lambda item: item[1], reverse=True)

    @staticmethod
    def _bounded(value: object) -> float:
        """Convert numeric-like values into the 0.0 to 1.0 range."""
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, numeric))
