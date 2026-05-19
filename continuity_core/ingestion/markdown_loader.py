"""Markdown journal ingestion for continuity systems."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from continuity_core.memory.event import MemoryEvent


IDENTITY_KEYWORDS = {
    "identity",
    "continuity",
    "architecture",
    "memory",
    "cognition",
    "reflection",
    "timeline",
    "repair",
}


@dataclass(frozen=True)
class ParsedJournal:
    title: str
    date: datetime
    body: str
    tags: list[str]


class MarkdownJournalLoader:
    """Converts markdown journals into MemoryEvent objects."""

    def load_file(self, path: str | Path) -> list[MemoryEvent]:
        path = Path(path)
        content = path.read_text(encoding="utf-8")
        parsed = self.parse_markdown(content)
        return self.extract_events(parsed)

    def parse_markdown(self, markdown: str) -> ParsedJournal:
        lines = [line.strip() for line in markdown.splitlines() if line.strip()]

        title = "Untitled Journal"
        body_lines: list[str] = []
        parsed_date = datetime.now(timezone.utc)

        for line in lines:
            if line.startswith("# "):
                title = line.replace("# ", "", 1)
                possible_date = self._extract_date(title)
                if possible_date:
                    parsed_date = possible_date
            else:
                body_lines.append(line)

        body = "\n".join(body_lines)
        tags = self._extract_tags(body)

        return ParsedJournal(
            title=title,
            date=parsed_date,
            body=body,
            tags=tags,
        )

    def extract_events(self, parsed: ParsedJournal) -> list[MemoryEvent]:
        paragraphs = [
            paragraph.strip()
            for paragraph in parsed.body.split("\n")
            if paragraph.strip()
        ]

        events: list[MemoryEvent] = []

        for paragraph in paragraphs:
            event_type = self._infer_event_type(paragraph)
            importance = self._infer_importance(paragraph)
            identity_relevance = self._identity_relevance(paragraph)

            event = MemoryEvent(
                content=paragraph,
                event_type=event_type,
                timestamp=parsed.date,
                source="markdown_journal",
                tags=parsed.tags,
                importance=importance,
                metadata={
                    "identity_relevance": identity_relevance,
                    "journal_title": parsed.title,
                },
            )

            events.append(event)

        return events

    def _infer_event_type(self, text: str) -> str:
        lowered = text.lower()

        if any(word in lowered for word in ["contradiction", "abandon", "drift"]):
            return "contradiction"

        if any(word in lowered for word in ["repair", "resume", "restart"]):
            return "repair_action"

        if any(word in lowered for word in ["realized", "reflection", "understand"]):
            return "reflection"

        if any(word in lowered for word in ["build", "implement", "finished"]):
            return "progress"

        return "note"

    def _infer_importance(self, text: str) -> float:
        length_score = min(len(text) / 300, 1.0)
        keyword_bonus = 0.2 if self._identity_relevance(text) > 0.4 else 0.0
        return round(min(0.4 + length_score + keyword_bonus, 1.0), 2)

    def _identity_relevance(self, text: str) -> float:
        lowered = text.lower()
        matches = sum(1 for keyword in IDENTITY_KEYWORDS if keyword in lowered)
        return round(min(matches / 4, 1.0), 2)

    def _extract_tags(self, text: str) -> list[str]:
        lowered = text.lower()
        tags = [keyword for keyword in IDENTITY_KEYWORDS if keyword in lowered]
        return sorted(set(tags))

    @staticmethod
    def _extract_date(text: str) -> datetime | None:
        match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        if not match:
            return None

        parsed = datetime.strptime(match.group(1), "%Y-%m-%d")
        return parsed.replace(tzinfo=timezone.utc)
