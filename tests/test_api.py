from fastapi.testclient import TestClient

from continuity_core.api import app, store


client = TestClient(app)


def setup_function() -> None:
    store.clear()


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_add_event_endpoint() -> None:
    response = client.post(
        "/events",
        json={
            "content": "Started continuity architecture work",
            "event_type": "goal",
            "tags": ["continuity"],
            "importance": 0.9,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "Started continuity architecture work"
    assert data["event_type"] == "goal"


def test_list_events_endpoint() -> None:
    client.post(
        "/events",
        json={
            "content": "First event",
            "event_type": "goal",
        },
    )

    response = client.get("/events")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_reflection_endpoint_without_events() -> None:
    response = client.get("/reflection")

    assert response.status_code == 200
    assert "No events available" in response.json()["summary"]


def test_reflection_endpoint_with_events() -> None:
    client.post(
        "/events",
        json={
            "content": "User resumes continuity research",
            "event_type": "progress",
            "tags": ["identity", "continuity"],
            "importance": 0.9,
            "metadata": {
                "identity_relevance": 1.0,
            },
        },
    )

    response = client.get("/reflection")

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert "recommendations" in data
