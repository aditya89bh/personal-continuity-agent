"""Identity transition engine.

This module tracks how identity themes change across time windows. It helps the
continuity system detect which themes are newly appearing, which are becoming
stable, and which have not appeared recently.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from continuity_core.memory.event import MemoryEvent


@dataclass(frozen=True)
class IdentityThemeTrend:
    """A measured theme trend across identity-relevant events."""

    theme: str
    first_seen: datetime
    last_seen: datetime
    event_count: int
    strength: float
    status: str
    source_event_ids: list[str]


@dataclass(frozen=True)
class IdentityTransitionReport:
    """Summary of identity theme transitions."""

    new_themes: list[IdentityThemeTrend]
    stable_themes: list[IdentityThemeTrend]
    quiet_themes: list[IdentityThemeTrend]
    summary: str


class IdentityTransitionEngine:
    """Analyzes identity theme transitions across continuity events."""

    THEME_KEYWORDS = {
        "identity",
        "continuity",
        "memory",
        "cognition",
        "architecture",
        "reflection",
        "timeline",
        "agents",
        "robotics",
        "design",
    }

    def __init__(self, quiet_after_days: int = 45) -> None:
        if quiet_after_days <= 0:
            raise ValueError("quiet_after_days must be greater than zero")
        self.quiet_after_days = quiet_after_days

    def analyze(self, events: list[MemoryEvent], now: datetime) -> IdentityTransitionReport:
        """Return identity transition report."""
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        relevant_events = [event for event in events if self._is_identity_relevant(event)]
        trends = self._build_trends(relevant_events, now)

        new_themes = [trend for trend in trends if trend.status == "new"]
        stable_themes = [trend for trend in trends if trend.status == "stable"]
        quiet_themes = [trend for trend in trends if trend.status == "quiet"]

        summary = (
            f"Identity transition report: {len(new_themes)} new theme(s), "
            f"{len(stable_themes)} stable theme(s), and {len(quiet_themes)} quiet theme(s)."
        )

        return IdentityTransitionReport(
            new_themes=sorted(new_themes, key=lambda trend: trend.strength, reverse=True),
            stable_themes=sorted(stable_themes, key=lambda trend: trend.strength, reverse=True),
            quiet_themes=sorted(quiet_themes, key=lambda trend: trend.strength, reverse=True),
            summary=summary,
        )

    def _build_trends(
        self,
        events: list[MemoryEvent],
        now: datetime,
    ) -> list[IdentityThemeTrend]:
        grouped: dict[str, list[MemoryEvent]] = defaultdict(list)

        for event in events:
            for theme in self._themes_for_event(event):
                grouped[theme].append(event)

        trends: list[IdentityThemeTrend] = []

        for theme, theme_events in grouped.items():
            ordered = sorted(theme_events, key=lambda event: event.timestamp)
            first_seen = ordered[0].timestamp
            last_seen = ordered[-1].timestamp
            days_since_last_seen = (now - last_seen).days
            strength = self._theme_strength(ordered)

            if days_since_last_seen >= self.quiet_after_days:
                status = "quiet"
            elif len(ordered) >= 3 or strength >= 0.75:
                status = "stable"
            else:
                status = "new"

            trends.append(
                IdentityThemeTrend(
                    theme=theme,
                    first_seen=first_seen,
                    last_seen=last_seen,
                    event_count=len(ordered),
                    strength=strength,
                    status=status,
                    source_event_ids=[event.event_id for event in ordered],
                )
            )

        return trends

    def _themes_for_event(self, event: MemoryEvent) -> list[str]:
        themes = [tag for tag in event.tags if tag in self.THEME_KEYWORDS]
        if event.event_type in {"identity_synthesis", "reflection"}:
            themes.append("reflection")
        return sorted(set(themes))

    def _is_identity_relevant(self, event: MemoryEvent) -> bool:
        return (
            bool(set(event.tags).intersection(self.THEME_KEYWORDS))
            or event.event_type in {"identity_synthesis", "reflection"}
            or float(event.metadata.get("identity_relevance", 0.0)) >= 0.5
        )

    @staticmethod
    def _theme_strength(events: list[MemoryEvent]) -> float:
        avg_importance = sum(event.importance for event in events) / len(events)
        avg_identity_relevance = sum(
            float(event.metadata.get("identity_relevance", 0.0)) for event in events
        ) / len(events)
        return round(min(1.0, (avg_importance * 0.5) + (avg_identity_relevance * 0.5)), 4)
