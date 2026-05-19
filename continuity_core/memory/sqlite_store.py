"""SQLite-backed event store for persistent continuity memory.

This is the first production-oriented storage layer. It keeps the same
MemoryEvent abstraction while adding durable local persistence.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from continuity_core.memory.event import MemoryEvent


class SQLiteEventStore:
    """Persistent SQLite store for MemoryEvent objects."""

    def __init__(self, db_path: str | Path = "continuity_memory.db") -> None:
        self.db_path = Path(db_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_events (
                    event_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    importance REAL NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_events_timestamp ON memory_events(timestamp)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_events_type ON memory_events(event_type)"
            )

    def add(self, event: MemoryEvent) -> MemoryEvent:
        """Persist a memory event.

        Raises:
            ValueError: If an event with the same id already exists.
        """
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO memory_events (
                        event_id,
                        content,
                        event_type,
                        timestamp,
                        source,
                        tags,
                        importance,
                        metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._event_to_row(event),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Event already exists: {event.event_id}") from error

        return event

    def add_many(self, events: Iterable[MemoryEvent]) -> list[MemoryEvent]:
        """Persist multiple memory events."""
        saved: list[MemoryEvent] = []
        for event in events:
            saved.append(self.add(event))
        return saved

    def get(self, event_id: str) -> MemoryEvent | None:
        """Return an event by id, or None if missing."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM memory_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()

        if row is None:
            return None
        return self._row_to_event(row)

    def list_all(self) -> list[MemoryEvent]:
        """Return all events sorted by timestamp."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM memory_events ORDER BY timestamp ASC"
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def filter_by_type(self, event_type: str) -> list[MemoryEvent]:
        """Return events matching an event type."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM memory_events WHERE event_type = ? ORDER BY timestamp ASC",
                (event_type,),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def count(self) -> int:
        """Return number of persisted events."""
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) FROM memory_events").fetchone()
        return int(row[0])

    def clear(self) -> None:
        """Delete all events from the store."""
        with self._connect() as connection:
            connection.execute("DELETE FROM memory_events")

    @staticmethod
    def _event_to_row(event: MemoryEvent) -> tuple[str, str, str, str, str, str, float, str]:
        return (
            event.event_id,
            event.content,
            event.event_type,
            event.timestamp.isoformat(),
            event.source,
            json.dumps(event.tags),
            event.importance,
            json.dumps(event.metadata),
        )

    @staticmethod
    def _row_to_event(row: tuple) -> MemoryEvent:
        return MemoryEvent.from_dict(
            {
                "event_id": row[0],
                "content": row[1],
                "event_type": row[2],
                "timestamp": row[3],
                "source": row[4],
                "tags": json.loads(row[5]),
                "importance": row[6],
                "metadata": json.loads(row[7]),
            }
        )
