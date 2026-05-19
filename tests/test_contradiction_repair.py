from datetime import datetime, timezone

import pytest

from continuity_core.memory.event import MemoryEvent
from continuity_core.temporal.repair import (
    ContradictionRepairTracker,
    RepairStatus,
)


BASE_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def build_event(
    content: str,
    event_type: str,
    tags: list[str] | None = None,
) -> MemoryEvent:
    return MemoryEvent(
        content=content,
        event_type=event_type,
        timestamp=BASE_TIME,
        tags=tags or [],
        importance=0.8,
    )


def test_open_repair_record() -> None:
    tracker = ContradictionRepairTracker()

    contradiction = build_event(
        "User abandons stated research goal.",
        "contradiction",
        tags=["contradiction"],
    )

    record = tracker.open_repair(contradiction)

    assert record.status == RepairStatus.OPEN
    assert len(tracker.list_records()) == 1


def test_add_repair_action_moves_status_to_in_progress() -> None:
    tracker = ContradictionRepairTracker()

    contradiction = build_event(
        "User stops publishing weekly notes.",
        "contradiction",
        tags=["contradiction"],
    )

    repair_action = build_event(
        "User resumes weekly research logs.",
        "repair_action",
    )

    tracker.open_repair(contradiction)
    record = tracker.add_repair_action(
        contradiction.event_id,
        repair_action,
    )

    assert record.status == RepairStatus.IN_PROGRESS
    assert len(record.repair_actions) == 1


def test_repair_record_can_be_completed() -> None:
    tracker = ContradictionRepairTracker()

    contradiction = build_event(
        "User repeatedly avoids strategic writing.",
        "contradiction",
        tags=["contradiction"],
    )

    repair_action = build_event(
        "User publishes two strategic essays.",
        "repair_action",
    )

    tracker.open_repair(contradiction)
    tracker.add_repair_action(contradiction.event_id, repair_action)

    repaired = tracker.mark_repaired(contradiction.event_id)

    assert repaired.status == RepairStatus.REPAIRED
    assert tracker.repair_rate() == 1.0


def test_repair_summary_is_generated() -> None:
    tracker = ContradictionRepairTracker()

    contradiction = build_event(
        "User says focus matters but constantly switches priorities.",
        "contradiction",
        tags=["contradiction"],
    )

    record = tracker.open_repair(contradiction)

    summary = record.repair_summary()

    assert "Contradiction" in summary
    assert "open" in summary


def test_non_contradiction_event_is_rejected() -> None:
    tracker = ContradictionRepairTracker()

    non_contradiction = build_event(
        "Regular progress update.",
        "progress",
    )

    with pytest.raises(ValueError, match="contradiction event"):
        tracker.open_repair(non_contradiction)


def test_duplicate_repair_record_is_rejected() -> None:
    tracker = ContradictionRepairTracker()

    contradiction = build_event(
        "Repeated contradiction.",
        "contradiction",
        tags=["contradiction"],
    )

    tracker.open_repair(contradiction)

    with pytest.raises(ValueError, match="Repair already exists"):
        tracker.open_repair(contradiction)


def test_marking_repaired_without_actions_fails() -> None:
    tracker = ContradictionRepairTracker()

    contradiction = build_event(
        "Unrepaired contradiction.",
        "contradiction",
        tags=["contradiction"],
    )

    tracker.open_repair(contradiction)

    with pytest.raises(ValueError, match="without repair actions"):
        tracker.mark_repaired(contradiction.event_id)
