from datetime import datetime, timedelta, timezone

import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.memory.graph import MemoryGraphBuilder, MemoryRelation


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_event(
    content: str,
    event_type: str,
    day: int,
    tags: list[str],
) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_TIME + timedelta(days=day),
        tags=tags,
        importance=0.8,
    )


def test_graph_builder_links_goal_to_progress() -> None:
    builder = MemoryGraphBuilder()

    events = [
        make_event("Define continuity goal.", "goal", 0, ["continuity"]),
        make_event("Build continuity module.", "progress", 1, ["continuity"]),
    ]

    graph = builder.build(events)

    assert len(graph.edges) >= 1
    assert graph.edges[0].relation == MemoryRelation.SUPPORTS


def test_graph_builder_creates_repair_relationship() -> None:
    builder = MemoryGraphBuilder()

    events = [
        make_event("Continuity break recorded.", "contradiction", 0, ["continuity"]),
        make_event("Continuity repair action.", "repair_action", 10, ["continuity"]),
    ]

    graph = builder.build(events)

    repair_edges = [edge for edge in graph.edges if edge.relation == MemoryRelation.REPAIRS]

    assert len(repair_edges) == 1


def test_graph_neighbors_returns_connected_events() -> None:
    builder = MemoryGraphBuilder()

    events = [
        make_event("Reflection goal.", "goal", 0, ["reflection"]),
        make_event("Reflection note.", "reflection", 1, ["reflection"]),
    ]

    graph = builder.build(events)

    neighbors = graph.neighbors(events[0].event_id)

    assert len(neighbors) == 1
    assert neighbors[0].event_id == events[1].event_id


def test_graph_related_by_theme_filters_correctly() -> None:
    builder = MemoryGraphBuilder()

    events = [
        make_event("Memory systems note.", "reflection", 0, ["memory"]),
        make_event("Robotics systems note.", "reflection", 1, ["robotics"]),
    ]

    graph = builder.build(events)

    memory_events = graph.related_by_theme("memory")

    assert len(memory_events) == 1
    assert memory_events[0].tags == ["memory"]


def test_graph_rejects_invalid_edge_weight() -> None:
    builder = MemoryGraphBuilder()

    event = make_event("Memory note.", "reflection", 0, ["memory"])
    graph = builder.build([event])

    with pytest.raises(ValueError):
        graph.add_edge(
            edge=type(graph.edges)([
            ])
        )
