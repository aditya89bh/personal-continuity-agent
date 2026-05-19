import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.salience.scorer import SalienceScorer, SalienceWeights


def test_salience_score_uses_event_importance() -> None:
    event = MemoryEvent(
        content="User made an important decision.",
        event_type="decision",
        importance=1.0,
    )
    scorer = SalienceScorer()

    assert scorer.score(event) == 0.35


def test_salience_score_uses_metadata_signals() -> None:
    event = MemoryEvent(
        content="User repeatedly returned to the same unresolved goal.",
        event_type="reflection",
        importance=0.5,
        metadata={
            "emotional_intensity": 0.8,
            "goal_relevance": 1.0,
            "identity_relevance": 0.6,
            "unresolved_tension": 1.0,
        },
    )
    scorer = SalienceScorer()

    assert scorer.score(event) == 0.725


def test_salience_score_bounds_invalid_metadata_values() -> None:
    event = MemoryEvent(
        content="User described a very intense concern.",
        event_type="emotion",
        importance=0.5,
        metadata={
            "emotional_intensity": 4.0,
            "goal_relevance": "not-a-number",
            "identity_relevance": -2,
            "unresolved_tension": 1.0,
        },
    )
    scorer = SalienceScorer()

    assert scorer.score(event) == 0.475


def test_salience_rank_orders_events_by_score() -> None:
    low = MemoryEvent(content="Small note", event_type="note", importance=0.1)
    high = MemoryEvent(
        content="Major unresolved identity-relevant goal.",
        event_type="goal",
        importance=0.9,
        metadata={
            "goal_relevance": 1.0,
            "identity_relevance": 1.0,
            "unresolved_tension": 0.8,
        },
    )
    scorer = SalienceScorer()

    ranked = scorer.rank([low, high])

    assert ranked[0][0] == high
    assert ranked[1][0] == low


def test_salience_rejects_zero_total_weights() -> None:
    weights = SalienceWeights(
        importance=0.0,
        emotional_intensity=0.0,
        goal_relevance=0.0,
        identity_relevance=0.0,
        unresolved_tension=0.0,
    )

    with pytest.raises(ValueError, match="total must be greater than zero"):
        SalienceScorer(weights)
