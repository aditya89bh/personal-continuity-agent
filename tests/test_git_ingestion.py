from datetime import datetime, timezone

from continuity_core.ingestion.git_loader import GitActivityLoader, GitCommit


def test_git_commit_to_event_conversion() -> None:
    loader = GitActivityLoader()

    commit = GitCommit(
        commit_hash="abc123",
        author="Aditya",
        timestamp=datetime(2026, 5, 19, tzinfo=timezone.utc),
        message="Add continuity timeline architecture",
    )

    event = loader.commit_to_event(commit)

    assert event.event_type == "progress"
    assert "continuity" in event.tags
    assert event.metadata["commit_hash"] == "abc123"


def test_repair_commit_detection() -> None:
    loader = GitActivityLoader()

    commit = GitCommit(
        commit_hash="repair456",
        author="Aditya",
        timestamp=datetime(2026, 5, 19, tzinfo=timezone.utc),
        message="Fix reflection continuity repair logic",
    )

    event = loader.commit_to_event(commit)

    assert event.event_type == "repair_action"


def test_contradiction_commit_detection() -> None:
    loader = GitActivityLoader()

    commit = GitCommit(
        commit_hash="drop789",
        author="Aditya",
        timestamp=datetime(2026, 5, 19, tzinfo=timezone.utc),
        message="Remove broken continuity UI experiment",
    )

    event = loader.commit_to_event(commit)

    assert event.event_type == "contradiction"


def test_importance_scoring() -> None:
    loader = GitActivityLoader()

    commit = GitCommit(
        commit_hash="importance123",
        author="Aditya",
        timestamp=datetime(2026, 5, 19, tzinfo=timezone.utc),
        message="Implement memory continuity architecture",
    )

    event = loader.commit_to_event(commit)

    assert event.importance >= 0.7
