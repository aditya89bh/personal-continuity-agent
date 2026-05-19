from datetime import datetime, timedelta, timezone

import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.temporal.gap_detection import ContinuityGapDetector, GapType


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)
NOW = datetime(2026, 3, 15, tzinfo=timezone.utc)


def make_event(
    content: str,
    event_type: str,
    day: int,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_TIME + timedelta(days=day),
        tags=tags or [],
        metadata=metadata or {},
        importance=0.8,
    )


def test_detects_goal_abandonment() -> None:
    detector = ContinuityGapDetector(gap_days=30)
    events = [
        make_event("Define continuity writing goal.", "goal", 0, tags=["writing"]),
    ]

    findings = detector.detect(events, now=NOW)

    assert any(finding.gap_type == GapType.GOAL_ABANDONMENT for finding in findings)


def test_goal_with_later_progress_is_not_abandoned() -> None:
    detector = ContinuityGapDetector(gap_days=30)
    events = [
        make_event("Define continuity writing goal.", "goal", 0, tags=["writing"]),
        make_event("Publish continuity note.", "progress", 10, tags=["writing"]),
    ]

    findings = detector.detect_goal_abandonment(events, now=NOW)

    assert findings == []


def test_detects_identity_silence() -> None:
    detector = ContinuityGapDetector(gap_days=30)
    events = [
        make_event(
            "Identity-level continuity note.",
            "reflection",
            0,
            tags=["identity"],
            metadata={"identity_relevance": 1.0},
        ),
    ]

    findings = detector.detect_identity_silence(events, now=NOW)

    assert len(findings) == 1
    assert findings[0].gap_type == GapType.IDENTITY_SILENCE


def test_detects_reflection_silence_when_no_reflections_exist() -> None:
    detector = ContinuityGapDetector(gap_days=30)
    events = [
        make_event("Initial goal.", "goal", 0, tags=["continuity"]),
    ]

    findings = detector.detect_reflection_silence(events, now=NOW)

    assert len(findings) == 1
    assert findings[0].gap_type == GapType.REFLECTION_SILENCE


def test_detects_missing_repair() -> None:
    detector = ContinuityGapDetector(gap_days=30)
    events = [
        make_event("Recorded continuity break.", "contradiction", 0, tags=["continuity"]),
    ]

    findings = detector.detect_missing_repairs(events, now=NOW)

    assert len(findings) == 1
    assert findings[0].gap_type == GapType.REPAIR_MISSING


def test_repair_event_prevents_missing_repair_gap() -> None:
    detector = ContinuityGapDetector(gap_days=30)
    events = [
        make_event("Recorded continuity break.", "contradiction", 0, tags=["continuity"]),
        make_event("Restarted continuity routine.", "repair_action", 10, tags=["continuity"]),
    ]

    findings = detector.detect_missing_repairs(events, now=NOW)

    assert findings == []


def test_gap_detector_rejects_invalid_threshold() -> None:
    with pytest.raises(ValueError):
        ContinuityGapDetector(gap_days=0)
