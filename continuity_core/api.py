"""FastAPI server for the Personal Continuity Agent."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from continuity_core.identity.model import IdentityModel
from continuity_core.memory.event import MemoryEvent
from continuity_core.memory.sqlite_store import SQLiteEventStore
from continuity_core.reflection.engine import ReflectionEngine


app = FastAPI(
    title="Personal Continuity Agent",
    description="Continuity-aware memory and reflection system.",
    version="0.1.0",
)

store = SQLiteEventStore()


class EventRequest(BaseModel):
    content: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    source: str = "api"
    tags: list[str] = []
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: dict = {}


@app.get("/")
def root() -> dict:
    return {
        "name": "Personal Continuity Agent",
        "status": "running",
    }


@app.post("/events")
def add_event(request: EventRequest) -> dict:
    event = MemoryEvent(
        content=request.content,
        event_type=request.event_type,
        source=request.source,
        tags=request.tags,
        importance=request.importance,
        metadata=request.metadata,
    )

    store.add(event)

    return {
        "event_id": event.event_id,
        "content": event.content,
        "event_type": event.event_type,
    }


@app.get("/events")
def list_events() -> list[dict]:
    events = store.list_all()

    return [
        {
            "event_id": event.event_id,
            "content": event.content,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "tags": event.tags,
            "importance": event.importance,
        }
        for event in events
    ]


@app.get("/reflection")
def reflection() -> dict:
    events = store.list_all()

    if not events:
        return {
            "summary": "No events available for reflection.",
            "recommendations": [],
        }

    identity_model = IdentityModel()

    for event in events:
        if event.metadata.get("identity_relevance", 0.0) or "identity" in event.tags:
            identity_model.add_claim(
                name="Identity continuity signal",
                category="identity_theme",
                evidence_event=event,
                evidence_strength=0.8,
            )

    reflection_result = ReflectionEngine().reflect(events, identity_model)

    return {
        "summary": reflection_result.summary,
        "recommendations": reflection_result.recommendations,
        "momentum_status": reflection_result.momentum_status,
        "continuity_gaps": reflection_result.continuity_gaps,
    }
