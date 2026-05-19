from examples.goal_drift_demo.run_demo import build_demo_events, detect_goal_drift
from continuity_core.salience.scorer import SalienceScorer


def test_goal_drift_demo_builds_synthetic_timeline() -> None:
    events = build_demo_events()

    assert len(events) == 4
    assert events[0].event_type == "goal"
    assert events[-1].event_type == "contradiction"


def test_goal_drift_demo_detects_high_drift_risk() -> None:
    events = build_demo_events()
    report = detect_goal_drift(events)

    assert report["status"] == "high_drift_risk"
    assert report["drift_score"] == 1.0
    assert report["progress_events"] == 1
    assert report["drift_events"] == 2
    assert report["contradictions"] == 1


def test_goal_drift_demo_salience_ranking_surfaces_contradiction() -> None:
    events = build_demo_events()
    scorer = SalienceScorer()

    ranked = scorer.rank(events)

    top_event, top_score = ranked[0]
    assert top_event.event_type == "contradiction"
    assert top_score > 0.8
