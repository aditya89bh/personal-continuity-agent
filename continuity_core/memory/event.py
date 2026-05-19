"""Event schema for the Personal Continuity Agent.

The event object is the atomic unit of continuity. It captures something
that happened, when it happened, why it may matter, and how it connects to
future identity, reflection, and temporal reasoning layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class MemoryEvent:
    """Structured event stored by the continuity engine.

    Attributes:
        content: Human-readable description of the event.
        event_type: Category of event, such as goal, decision, reflection, routine, or emotion.
        timestamp: UTC timestamp for when the event was recorded.
        event_id: Stable unique identifier.
        source: Origin of the event, such as chat, journal, calendar, or synthetic_demo.
        tags: Searchable semantic tags.
        importance: Initial importance score from 0.0 to 1.0.
        metadata: Optional structured payload for downstream modules.
    """

    content: str
    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = field(default_factory=lambda: str(uuid4()))
    source: str = "manual"
    tags: list[str] = field(default_factory=list)
    importance: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("MemoryEvent content cannot be empty.")
        if not self.event_type.strip():
            raise ValueError("MemoryEvent event_type cannot be empty.")
        if not 0.0 <= self.importance <= 1.0:
            raise ValueError("MemoryEvent importance must be between 0.0 and 1.0.")
        if self.timestamp.tzinfo is None:
            raise ValueError("MemoryEvent timestamp must be timezone-aware.")

    def to_dict(self) -> dict[str, Any]:
        """Convert the event to a JSON-serializable dictionary."""
        return {
            "event_id": self.event_id,
            "content": self.content,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "tags": list(self.tags),
            "importance": self.importance,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MemoryEvent":
        """Create a MemoryEvent from a JSON-style dictionary."""
        data = dict(payload)
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
