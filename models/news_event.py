"""Canonical economic news event model."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class NewsEvent:
    """Represents one normalized economic news event."""

    timestamp: int
    currency: str
    impact: str
    title: str
    actual: Optional[str] = None
    forecast: Optional[str] = None
    previous: Optional[str] = None

    @property
    def event_time(self) -> datetime:
        """Return the event timestamp as an aware UTC datetime."""
        return datetime.fromtimestamp(
            self.timestamp,
            tz=timezone.utc,
        )
