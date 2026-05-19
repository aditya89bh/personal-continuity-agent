"""Temporal narrative engine for continuity systems.

The narrative layer turns flat memory events into higher-order continuity arcs.
It identifies phases such as exploration, progress, contradiction, repair, and
stabilization so the system can reason about a life/work trajectory instead of
only listing events chronologically.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from continuity_core.memory.event import MemoryEvent


@dataclass(frozen=True)
class NarrativePhase:
    """A phase in a continuity trajectory."""

    phase_type: str
    start_time: datetime
    end_time: datetime
    event_count: int
    dominant_tags: list[str]
    summary: str


@dataclass(frozen=True)
class TemporalNarrative:
    """Narrative interpretation of a sequence of memory events."""

    phases: list[NarrativePhase]
    arc: str
    summary: str


class TemporalNarrativeEngine:
    """Builds narrative arcs from ordered memory events."""

    def build(self, events: list[MemoryEvent]) -> TemporalNarrative:
        """Return a temporal narrative from memory events."""
        if not events:
            raise ValueError("Cannot build narrative from empty events.")

        ordered = sorted(events, key=lambda event: event.timestamp)
        phases = self._build_phases(ordered)
        arc = self._infer_arc(phases)
        summary = self._build_summary(phases, arc)

        return TemporalNarrative(phases=phases, arc=arc, summary=summary)

    def _build_phases(self, events: list[MemoryEvent]) -> list[NarrativePhase]:
        phases: list[NarrativePhase] = []
        current_group: list[MemoryEvent] = []
        current_phase_type: str | None = None

        for event in events:
            phase_type = self._phase_type(event)

            if current_phase_type is None:
                current_phase_type = phase_type
                current_group = [event]
                continue

            if phase_type == current_phase_type:
                current_group.append(event)
                continue

            phases.append(self._phase_from_group(current_phase_type, current_group))
            current_phase_type = phase_type
            current_group = [event]

        if current_group and current_phase_type:
            phases.append(self._phase_from_group(current_phase_type, current_group))

        return phases

    def _phase_type(self, event: MemoryEvent) -> str:
        if event.event_type in {"contradiction", "missed_commitment"}:
            return "contradiction"

        if event.event_type in {"repair_action", "return_after_gap"}:
            return "repair"

        if event.event_type in {"goal", "work_focus", "research_focus"}:
            return "exploration"

        if event.event_type in {"progress", "project_build"}:
            return "progress"

        if event.event_type in {"reflection", "identity_synthesis"}:
            return "integration"

        return "observation"

    def _phase_from_group(
        self,
        phase_type: str,
        events: list[MemoryEvent],
    ) -> NarrativePhase:
        tags = Counter(tag for event in events for tag in event.tags)
        dominant_tags = [tag for tag, _ in tags.most_common(4)]

        first = events[0]
        last = events[-1]

        summary = (
            f"{phase_type.title()} phase from {first.timestamp.date()} to "
            f"{last.timestamp.date()} across {len(events)} event(s). "
            f"Starts with: '{first.content}'. Ends with: '{last.content}'."
        )

        return NarrativePhase(
            phase_type=phase_type,
            start_time=first.timestamp,
            end_time=last.timestamp,
            event_count=len(events),
            dominant_tags=dominant_tags,
            summary=summary,
        )

    def _infer_arc(self, phases: list[NarrativePhase]) -> str:
        phase_sequence = [phase.phase_type for phase in phases]

        if "contradiction" in phase_sequence and "repair" in phase_sequence:
            return "disruption_to_repair"

        if "exploration" in phase_sequence and "progress" in phase_sequence and "integration" in phase_sequence:
            return "exploration_to_integration"

        if phase_sequence.count("progress") >= 2:
            return "sustained_progress"

        if phase_sequence[-1] == "contradiction":
            return "open_disruption"

        return "emerging_continuity"

    def _build_summary(self, phases: list[NarrativePhase], arc: str) -> str:
        phase_names = " → ".join(phase.phase_type for phase in phases)
        return (
            f"Temporal arc '{arc}' detected across {len(phases)} phase(s): "
            f"{phase_names}. The trajectory should be read as a continuity pattern, "
            f"not a flat list of events."
        )
