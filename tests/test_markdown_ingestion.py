from continuity_core.ingestion.markdown_loader import MarkdownJournalLoader


SAMPLE_JOURNAL = """
# 2026-05-19

Today I resumed work on the continuity architecture repo.

I realized the UI still feels like a dashboard instead of a temporal cognition system.

Need to focus on timeline repair and memory salience.
"""


def test_markdown_journal_parsing() -> None:
    loader = MarkdownJournalLoader()

    parsed = loader.parse_markdown(SAMPLE_JOURNAL)

    assert parsed.title == "2026-05-19"
    assert "continuity" in parsed.tags


def test_markdown_event_extraction() -> None:
    loader = MarkdownJournalLoader()

    parsed = loader.parse_markdown(SAMPLE_JOURNAL)
    events = loader.extract_events(parsed)

    assert len(events) == 3
    assert events[0].event_type == "repair_action"
    assert events[1].event_type == "reflection"


def test_identity_relevance_is_attached() -> None:
    loader = MarkdownJournalLoader()

    parsed = loader.parse_markdown(SAMPLE_JOURNAL)
    events = loader.extract_events(parsed)

    relevance = events[0].metadata["identity_relevance"]

    assert relevance > 0


def test_importance_is_bounded() -> None:
    loader = MarkdownJournalLoader()

    parsed = loader.parse_markdown(SAMPLE_JOURNAL)
    events = loader.extract_events(parsed)

    for event in events:
        assert 0.0 <= event.importance <= 1.0
