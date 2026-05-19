"""Graph memory for continuity systems.

The graph layer links memory events into meaningful relationships. This allows
continuity reasoning to move beyond a flat timeline into connected structures:
goals, progress, reflections, repairs, identity themes, and related events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from continuity_core.memory.event import MemoryEvent


class MemoryRelation(StrEnum):
    """Supported graph relation types between memory events."""

    RELATES_TO = "relates_to"
    SUPPORTS = "supports"
    REFLECTS_ON = "reflects_on"
    REPAIRS = "repairs"
    SHARES_THEME = "shares_theme"


@dataclass(frozen=True)
class MemoryEdge:
    """Directed relationship between two memory events."""

    source_event_id: str
    target_event_id: str
    relation: MemoryRelation
    weight: float
    reason: str


@dataclass
class MemoryGraph:
    """In-memory graph of continuity events."""

    nodes: dict[str, MemoryEvent] = field(default_factory=dict)
    edges: list[MemoryEdge] = field(default_factory=list)

    def add_event(self, event: MemoryEvent) -> None:
        self.nodes[event.event_id] = event

    def add_edge(self, edge: MemoryEdge) -> None:
        if edge.source_event_id not in self.nodes:
            raise ValueError(f"Unknown source event: {edge.source_event_id}")
        if edge.target_event_id not in self.nodes:
            raise ValueError(f"Unknown target event: {edge.target_event_id}")
        if not 0.0 <= edge.weight <= 1.0:
            raise ValueError("edge weight must be between 0.0 and 1.0")
        self.edges.append(edge)

    def neighbors(self, event_id: str) -> list[MemoryEvent]:
        neighbor_ids = [edge.target_event_id for edge in self.edges if edge.source_event_id == event_id]
        return [self.nodes[node_id] for node_id in neighbor_ids]

    def edges_for_event(self, event_id: str) -> list[MemoryEdge]:
        return [
            edge
            for edge in self.edges
            if edge.source_event_id == event_id or edge.target_event_id == event_id
        ]

    def related_by_theme(self, theme: str) -> list[MemoryEvent]:
        return [event for event in self.nodes.values() if theme in event.tags]


class MemoryGraphBuilder:
    """Builds graph relationships from memory event metadata and tags."""

    def build(self, events: list[MemoryEvent]) -> MemoryGraph:
        graph = MemoryGraph()
        ordered = sorted(events, key=lambda event: event.timestamp)

        for event in ordered:
            graph.add_event(event)

        for index, source in enumerate(ordered):
            for target in ordered[index + 1 :]:
                relation = self._infer_relation(source, target)
                if relation is None:
                    continue

                graph.add_edge(
                    MemoryEdge(
                        source_event_id=source.event_id,
                        target_event_id=target.event_id,
                        relation=relation,
                        weight=self._relation_weight(source, target, relation),
                        reason=self._relation_reason(source, target, relation),
                    )
                )

        return graph

    def _infer_relation(
        self,
        source: MemoryEvent,
        target: MemoryEvent,
    ) -> MemoryRelation | None:
        if target.event_type in {"repair_action", "return_after_gap"} and source.event_type in {
            "contradiction",
            "missed_commitment",
            "open_loop",
        }:
            return MemoryRelation.REPAIRS

        if target.event_type == "reflection":
            return MemoryRelation.REFLECTS_ON

        if source.event_type == "goal" and target.event_type in {"progress", "project_build"}:
            return MemoryRelation.SUPPORTS

        if self._shared_tags(source, target):
            return MemoryRelation.SHARES_THEME

        return None

    def _relation_weight(
        self,
        source: MemoryEvent,
        target: MemoryEvent,
        relation: MemoryRelation,
    ) -> float:
        shared_tag_count = len(self._shared_tags(source, target))
        base_weight = {
            MemoryRelation.REPAIRS: 0.95,
            MemoryRelation.SUPPORTS: 0.85,
            MemoryRelation.REFLECTS_ON: 0.75,
            MemoryRelation.SHARES_THEME: 0.55,
            MemoryRelation.RELATES_TO: 0.45,
        }[relation]
        return round(min(1.0, base_weight + (shared_tag_count * 0.05)), 4)

    def _relation_reason(
        self,
        source: MemoryEvent,
        target: MemoryEvent,
        relation: MemoryRelation,
    ) -> str:
        if relation == MemoryRelation.REPAIRS:
            return "Later event repairs an earlier continuity break."
        if relation == MemoryRelation.SUPPORTS:
            return "Later event supports an earlier goal."
        if relation == MemoryRelation.REFLECTS_ON:
            return "Later reflection interprets earlier continuity events."
        if relation == MemoryRelation.SHARES_THEME:
            themes = ", ".join(self._shared_tags(source, target))
            return f"Events share theme(s): {themes}."
        return "Events are related."

    @staticmethod
    def _shared_tags(source: MemoryEvent, target: MemoryEvent) -> set[str]:
        return set(source.tags).intersection(target.tags)
