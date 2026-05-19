"""Contradiction repair for continuity systems.

Continuity does not mean avoiding contradictions. It means detecting breaks
between stated intent and behavior, then tracking whether the system can recover
coherence through repair actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from continuity_core.memory.event import MemoryEvent


class RepairStatus(StrEnum):
    """Lifecycle state for a contradiction repair record."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REPAIRED = "repaired"
    ABANDONED = "abandoned"


@dataclass
class RepairRecord:
    """Tracks a contradiction and its repair trajectory."""

    contradiction_event: MemoryEvent
    status: RepairStatus = RepairStatus.OPEN
    repair_actions: list[MemoryEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        if self.updated_at.tzinfo is None:
            raise ValueError("updated_at must be timezone-aware")
        if not self._is_contradiction(self.contradiction_event):
            raise ValueError("RepairRecord requires a contradiction event")

    def add_repair_action(self, event: MemoryEvent) -> None:
        """Attach a repair action and move record into progress."""
        self.repair_actions.append(event)
        self.status = RepairStatus.IN_PROGRESS
        self.updated_at = datetime.now(timezone.utc)

    def mark_repaired(self) -> None:
        """Mark the contradiction as repaired."""
        if not self.repair_actions:
            raise ValueError("Cannot mark repaired without repair actions")
        self.status = RepairStatus.REPAIRED
        self.updated_at = datetime.now(timezone.utc)

    def mark_abandoned(self) -> None:
        """Mark the repair attempt as abandoned."""
        self.status = RepairStatus.ABANDONED
        self.updated_at = datetime.now(timezone.utc)

    def repair_summary(self) -> str:
        """Return a compact repair summary."""
        return (
            f"Contradiction '{self.contradiction_event.content}' is {self.status}. "
            f"Repair actions: {len(self.repair_actions)}."
        )

    @staticmethod
    def _is_contradiction(event: MemoryEvent) -> bool:
        return event.event_type == "contradiction" or "contradiction" in event.tags


class ContradictionRepairTracker:
    """Tracks contradiction records and repair progress."""

    def __init__(self) -> None:
        self._records: dict[str, RepairRecord] = {}

    def open_repair(self, contradiction_event: MemoryEvent) -> RepairRecord:
        """Open a repair record for a contradiction event."""
        if contradiction_event.event_id in self._records:
            raise ValueError(f"Repair already exists: {contradiction_event.event_id}")

        record = RepairRecord(contradiction_event=contradiction_event)
        self._records[contradiction_event.event_id] = record
        return record

    def add_repair_action(self, contradiction_event_id: str, repair_event: MemoryEvent) -> RepairRecord:
        """Attach a repair event to an existing repair record."""
        record = self.get(contradiction_event_id)
        if record is None:
            raise ValueError(f"Unknown repair record: {contradiction_event_id}")

        record.add_repair_action(repair_event)
        return record

    def mark_repaired(self, contradiction_event_id: str) -> RepairRecord:
        """Mark a repair record as repaired."""
        record = self.get(contradiction_event_id)
        if record is None:
            raise ValueError(f"Unknown repair record: {contradiction_event_id}")

        record.mark_repaired()
        return record

    def get(self, contradiction_event_id: str) -> RepairRecord | None:
        """Return repair record by contradiction event id."""
        return self._records.get(contradiction_event_id)

    def list_records(self) -> list[RepairRecord]:
        """Return all repair records."""
        return list(self._records.values())

    def open_records(self) -> list[RepairRecord]:
        """Return records that still need repair."""
        return [
            record
            for record in self._records.values()
            if record.status in {RepairStatus.OPEN, RepairStatus.IN_PROGRESS}
        ]

    def repaired_records(self) -> list[RepairRecord]:
        """Return repaired records."""
        return [record for record in self._records.values() if record.status == RepairStatus.REPAIRED]

    def repair_rate(self) -> float:
        """Return repaired records divided by total records."""
        total = len(self._records)
        if total == 0:
            return 0.0
        return round(len(self.repaired_records()) / total, 4)
