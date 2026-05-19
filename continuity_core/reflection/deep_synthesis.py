"""Deep reflection synthesis.

This module upgrades reflection from flat summarization toward trajectory-level
continuity interpretation. It synthesizes narratives, gaps, identity themes,
and graph relationships into higher-order continuity observations.
"""

from __future__ import annotations

from dataclasses import dataclass

from continuity_core.identity.transition import IdentityTransitionReport
from continuity_core.memory.graph import MemoryGraph
from continuity_core.temporal.gap_detection import ContinuityGapFinding
from continuity_core.temporal.narrative import TemporalNarrative


@dataclass(frozen=True)
class DeepReflection:
    """High-level continuity synthesis."""

    trajectory_summary: str
    continuity_observations: list[str]
    unresolved_tensions: list[str]
    identity_direction: str
    graph_insights: list[str]
    recommendations: list[str]


class DeepReflectionSynthesizer:
    """Synthesizes continuity cognition layers into higher-order reflections."""

    def synthesize(
        self,
        narrative: TemporalNarrative,
        gaps: list[ContinuityGapFinding],
        identity_report: IdentityTransitionReport,
        memory_graph: MemoryGraph,
    ) -> DeepReflection:
        """Generate deep continuity reflection."""

        observations = self._continuity_observations(narrative, gaps, identity_report)
        tensions = self._unresolved_tensions(gaps)
        direction = self._identity_direction(identity_report)
        graph_insights = self._graph_insights(memory_graph)
        recommendations = self._recommendations(gaps, identity_report)

        trajectory_summary = (
            f"Continuity trajectory '{narrative.arc}' detected across "
            f"{len(narrative.phases)} narrative phase(s). "
            f"The system identified {len(gaps)} continuity gap(s), "
            f"{len(identity_report.stable_themes)} stable identity theme(s), "
            f"and {len(memory_graph.edges)} graph relationship(s)."
        )

        return DeepReflection(
            trajectory_summary=trajectory_summary,
            continuity_observations=observations,
            unresolved_tensions=tensions,
            identity_direction=direction,
            graph_insights=graph_insights,
            recommendations=recommendations,
        )

    def _continuity_observations(
        self,
        narrative: TemporalNarrative,
        gaps: list[ContinuityGapFinding],
        identity_report: IdentityTransitionReport,
    ) -> list[str]:
        observations = [
            f"Narrative arc detected: {narrative.arc}.",
            f"Stable identity themes: {len(identity_report.stable_themes)}.",
        ]

        if gaps:
            observations.append(
                f"Continuity analysis identified {len(gaps)} unresolved or quiet regions."
            )

        if identity_report.new_themes:
            observations.append(
                f"New identity themes emerging: {', '.join(theme.theme for theme in identity_report.new_themes[:3])}."
            )

        return observations

    def _unresolved_tensions(self, gaps: list[ContinuityGapFinding]) -> list[str]:
        if not gaps:
            return ["No major unresolved continuity tensions detected."]

        return [
            f"{gap.gap_type.value} active for {gap.duration_days} day(s)."
            for gap in gaps[:5]
        ]

    def _identity_direction(self, report: IdentityTransitionReport) -> str:
        if report.stable_themes:
            dominant = report.stable_themes[0].theme
            return f"Identity structure currently stabilizing around '{dominant}'."

        if report.new_themes:
            dominant = report.new_themes[0].theme
            return f"Identity structure currently exploring '{dominant}'."

        return "Identity direction remains weakly defined."

    def _graph_insights(self, graph: MemoryGraph) -> list[str]:
        if not graph.edges:
            return ["Graph memory currently contains isolated events."]

        relation_counts: dict[str, int] = {}

        for edge in graph.edges:
            relation_counts[edge.relation.value] = relation_counts.get(edge.relation.value, 0) + 1

        return [
            f"{relation}: {count} relationship(s)."
            for relation, count in sorted(relation_counts.items(), key=lambda item: item[1], reverse=True)
        ]

    def _recommendations(
        self,
        gaps: list[ContinuityGapFinding],
        report: IdentityTransitionReport,
    ) -> list[str]:
        recommendations: list[str] = []

        if gaps:
            recommendations.append(
                "Reinforce continuity around unresolved or quiet trajectories."
            )

        if report.quiet_themes:
            recommendations.append(
                "Review whether quiet identity themes should be intentionally reactivated or retired."
            )

        if report.new_themes:
            recommendations.append(
                "Monitor whether emerging themes stabilize into long-term continuity structures."
            )

        if not recommendations:
            recommendations.append(
                "Maintain current continuity trajectory and reflection cadence."
            )

        return recommendations
