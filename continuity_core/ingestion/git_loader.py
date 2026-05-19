"""Git activity ingestion for continuity systems."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from continuity_core.memory.event import MemoryEvent


@dataclass(frozen=True)
class GitCommit:
    commit_hash: str
    author: str
    timestamp: datetime
    message: str


class GitActivityLoader:
    """Converts git activity into continuity memory events."""

    def load_repository(self, repo_path: str | Path, limit: int = 25) -> list[MemoryEvent]:
        commits = self.read_git_log(repo_path=repo_path, limit=limit)
        return [self.commit_to_event(commit) for commit in commits]

    def read_git_log(self, repo_path: str | Path, limit: int = 25) -> list[GitCommit]:
        repo_path = Path(repo_path)

        command = [
            "git",
            "log",
            f"--max-count={limit}",
            "--pretty=format:%H|||%an|||%ad|||%s",
            "--date=iso",
        ]

        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

        commits: list[GitCommit] = []

        for line in result.stdout.splitlines():
            parts = line.split("|||")
            if len(parts) != 4:
                continue

            commit_hash, author, raw_date, message = parts

            timestamp = datetime.fromisoformat(raw_date.strip()).astimezone(timezone.utc)

            commits.append(
                GitCommit(
                    commit_hash=commit_hash,
                    author=author,
                    timestamp=timestamp,
                    message=message,
                )
            )

        return commits

    def commit_to_event(self, commit: GitCommit) -> MemoryEvent:
        event_type = self._infer_event_type(commit.message)

        return MemoryEvent(
            content=commit.message,
            event_type=event_type,
            timestamp=commit.timestamp,
            source="git_activity",
            tags=self._extract_tags(commit.message),
            importance=self._infer_importance(commit.message),
            metadata={
                "commit_hash": commit.commit_hash,
                "author": commit.author,
            },
        )

    def _infer_event_type(self, message: str) -> str:
        lowered = message.lower()

        if any(keyword in lowered for keyword in ["fix", "repair", "resolve"]):
            return "repair_action"

        if any(keyword in lowered for keyword in ["remove", "delete", "drop"]):
            return "contradiction"

        if any(keyword in lowered for keyword in ["reflect", "refactor", "rethink"]):
            return "reflection"

        if any(keyword in lowered for keyword in ["add", "build", "implement", "create"]):
            return "progress"

        return "note"

    def _extract_tags(self, message: str) -> list[str]:
        lowered = message.lower()

        tags = []

        keyword_map = {
            "memory": "memory",
            "continuity": "continuity",
            "timeline": "timeline",
            "reflection": "reflection",
            "identity": "identity",
            "ui": "design",
            "frontend": "frontend",
            "api": "api",
        }

        for keyword, tag in keyword_map.items():
            if keyword in lowered:
                tags.append(tag)

        return sorted(set(tags))

    def _infer_importance(self, message: str) -> float:
        lowered = message.lower()

        score = 0.45

        if any(keyword in lowered for keyword in ["continuity", "identity", "memory"]):
            score += 0.25

        if any(keyword in lowered for keyword in ["architecture", "timeline", "reflection"]):
            score += 0.15

        return round(min(score, 1.0), 2)
