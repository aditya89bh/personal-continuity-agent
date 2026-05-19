"""Command-line explorer for the Personal Continuity Agent.

Example usage:

    python -m continuity_core.cli add-event --content "Started continuity repo" --event-type goal
    python -m continuity_core.cli list-events
    python -m continuity_core.cli reflect
"""

from __future__ import annotations

import argparse
from pathlib import Path

from continuity_core.identity.model import IdentityModel
from continuity_core.memory.event import MemoryEvent
from continuity_core.memory.sqlite_store import SQLiteEventStore
from continuity_core.reflection.engine import ReflectionEngine


DEFAULT_DB_PATH = Path("continuity_memory.db")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="personal-continuity-agent",
        description="CLI for storing and reflecting on continuity memory events.",
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB_PATH),
        help="SQLite database path. Defaults to continuity_memory.db.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_event = subparsers.add_parser("add-event", help="Add a memory event.")
    add_event.add_argument("--content", required=True, help="Event content.")
    add_event.add_argument("--event-type", required=True, help="Event type, such as goal or progress.")
    add_event.add_argument("--source", default="cli", help="Event source.")
    add_event.add_argument("--tag", action="append", default=[], help="Tag. Can be repeated.")
    add_event.add_argument("--importance", type=float, default=0.5, help="Importance from 0.0 to 1.0.")

    subparsers.add_parser("list-events", help="List stored events.")
    subparsers.add_parser("reflect", help="Generate a basic continuity reflection.")

    return parser


def add_event_command(store: SQLiteEventStore, args: argparse.Namespace) -> None:
    event = MemoryEvent(
        content=args.content,
        event_type=args.event_type,
        source=args.source,
        tags=args.tag,
        importance=args.importance,
    )
    store.add(event)
    print(f"Added event: {event.event_id}")
    print(f"Type: {event.event_type}")
    print(f"Content: {event.content}")


def list_events_command(store: SQLiteEventStore) -> None:
    events = store.list_all()
    if not events:
        print("No events stored.")
        return

    for event in events:
        tags = ", ".join(event.tags) if event.tags else "no-tags"
        print(f"- {event.timestamp.date()} · {event.event_type} · {tags} · {event.content}")


def reflect_command(store: SQLiteEventStore) -> None:
    events = store.list_all()
    if not events:
        print("No events available for reflection.")
        return

    identity_model = IdentityModel()
    for event in events:
        if event.metadata.get("identity_relevance", 0.0) or "identity" in event.tags:
            identity_model.add_claim(
                name="Identity-relevant continuity signal",
                category="identity_theme",
                evidence_event=event,
                evidence_strength=0.8,
            )

    reflection = ReflectionEngine().reflect(events, identity_model)
    print(reflection.summary)
    print()
    print("Recommendations:")
    for recommendation in reflection.recommendations:
        print(f"- {recommendation}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    store = SQLiteEventStore(db_path=args.db)

    if args.command == "add-event":
        add_event_command(store, args)
    elif args.command == "list-events":
        list_events_command(store)
    elif args.command == "reflect":
        reflect_command(store)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
