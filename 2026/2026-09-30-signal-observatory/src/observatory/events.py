"""Living Event Ledger and Chronological History System.

Tracks events over time as they unfold across platforms, attaching
milestones, raw media footage (TikTok, YouTube, Facebook, citizen cameras),
and auditable artifact provenance IDs.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field


class EventMilestone(BaseModel):
    """A chronological occurrence or observation within an event."""

    timestamp: str  # ISO 8601 or YYYY-MM-DD HH:MM
    headline: str
    description: str = ""
    author: str | None = None
    platform: str | None = None
    source_url: str | None = None
    media_path: str | None = None
    artifact_id: str | None = None


class Event(BaseModel):
    """A tracked real-world or digital event with an unfolding history."""

    id: str
    title: str
    category: str = "general"  # civil_action, nightlife, public_safety, labor, etc.
    location: str = ""
    summary: str = ""
    date_start: str
    date_end: str | None = None
    status: str = "active"  # active, developing, concluded, archived
    milestones: list[EventMilestone] = Field(default_factory=list)
    artifact_ids: list[str] = Field(default_factory=list)
    media_files: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def add_milestone(self, milestone: EventMilestone) -> None:
        """Add a milestone and sort chronologically."""
        self.milestones.append(milestone)
        self.milestones.sort(key=lambda m: m.timestamp)
        self.updated_at = datetime.now(UTC).isoformat()
        if milestone.artifact_id and milestone.artifact_id not in self.artifact_ids:
            self.artifact_ids.append(milestone.artifact_id)
        if milestone.media_path and milestone.media_path not in self.media_files:
            self.media_files.append(milestone.media_path)


class EventLedger:
    """Manages event persistence and retrieval."""

    def __init__(self, storage_dir: Path | str = "data/events") -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _event_path(self, event_id: str) -> Path:
        return self.storage_dir / f"{event_id}.json"

    def list_events(self) -> list[Event]:
        """List all tracked events."""
        events: list[Event] = []
        for p in sorted(self.storage_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                events.append(Event.model_validate(data))
            except Exception:
                continue
        return events

    def get_event(self, event_id: str) -> Event | None:
        """Retrieve an event by ID."""
        p = self._event_path(event_id)
        if not p.exists():
            return None
        data = json.loads(p.read_text(encoding="utf-8"))
        return Event.model_validate(data)

    def save_event(self, event: Event) -> None:
        """Save or update an event."""
        event.updated_at = datetime.now(UTC).isoformat()
        p = self._event_path(event.id)
        p.write_text(event.model_dump_json(indent=2), encoding="utf-8")

    def create_event(
        self,
        event_id: str,
        title: str,
        category: str = "general",
        location: str = "",
        summary: str = "",
        date_start: str = "",
    ) -> Event:
        """Create and save a new event."""
        if not date_start:
            date_start = datetime.now(UTC).strftime("%Y-%m-%d")
        event = Event(
            id=event_id,
            title=title,
            category=category,
            location=location,
            summary=summary,
            date_start=date_start,
        )
        self.save_event(event)
        return event

    def generate_timeline_markdown(self, event_id: str) -> str:
        """Render a readable chronological timeline in Markdown."""
        event = self.get_event(event_id)
        if not event:
            return f"Event `{event_id}` not found."

        lines = [
            f"# Event History: {event.title}",
            "",
            f"- **ID:** `{event.id}`",
            f"- **Category:** {event.category.title()} | **Status:** {event.status.upper()}",
            f"- **Location:** {event.location}",
            f"- **Date Range:** {event.date_start} to {event.date_end or 'Present (Ongoing)'}",
            f"- **Linked Evidence Artifacts:** {len(event.artifact_ids)}",
            f"- **Captured Media Footage Clips:** {len(event.media_files)}",
            "",
            "## Summary",
            event.summary or "*(No summary provided)*",
            "",
            "## Chronological Timeline & Primary Evidence",
            "",
        ]

        if not event.milestones:
            lines.append("*(No milestones recorded yet)*")
        else:
            for i, m in enumerate(event.milestones, 1):
                author_str = f" by @{m.author}" if m.author else ""
                plat_str = f" [{m.platform.upper()}]" if m.platform else ""
                lines.append(f"### {i}. {m.timestamp} — {m.headline}{plat_str}{author_str}")
                if m.description:
                    lines.append(f"> {m.description}")
                if m.source_url:
                    lines.append(f"- **Source:** [Original Post / Feed]({m.source_url})")
                if m.media_path:
                    lines.append(f"- **Local Video File:** `{m.media_path}`")
                lines.append("")

        if event.media_files:
            lines.append("## Captured Media Assets")
            for mf in event.media_files:
                lines.append(f"- `{mf}`")
            lines.append("")

        return "\n".join(lines)
