"""Economic news normalization and file loading service."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Optional

from models.news_event import NewsEvent


class NewsService:
    """Normalize and load external economic news events."""

    @staticmethod
    def normalize_event(
        event: Mapping[str, object],
    ) -> Optional[NewsEvent]:
        """Normalize one external event mapping."""
        timestamp = NewsService._timestamp_from_event(event)

        if timestamp is None:
            return None

        currency = str(event.get("currency", "")).strip().upper()
        impact = str(event.get("impact", "")).strip().upper()

        title = str(
            event.get("title")
            or event.get("event")
            or "",
        ).strip()

        if not currency or not impact or not title:
            return None

        return NewsEvent(
            timestamp=timestamp,
            currency=currency,
            impact=impact,
            title=title,
            actual=NewsService._optional_string(event.get("actual")),
            forecast=NewsService._optional_string(event.get("forecast")),
            previous=NewsService._optional_string(event.get("previous")),
        )

    @staticmethod
    def _timestamp_from_event(
        event: Mapping[str, object],
    ) -> Optional[int]:
        """Extract a valid Unix timestamp from an event."""
        timestamp = event.get("timestamp")

        if timestamp is not None:
            try:
                value = int(timestamp)
            except (TypeError, ValueError):
                return None

            if value <= 0:
                return None

            return value

        date_value = event.get("date")

        if not isinstance(date_value, str):
            return None

        date_text = date_value.strip()

        if not date_text:
            return None

        try:
            parsed = datetime.fromisoformat(
                date_text.replace("Z", "+00:00"),
            )
        except ValueError:
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return int(parsed.timestamp())

    @staticmethod
    def _optional_string(
        value: object,
    ) -> Optional[str]:
        """Convert an optional event value to a string."""
        if value is None:
            return None

        return str(value)

    @staticmethod
    def normalize_events(
        events: Iterable[Mapping[str, object]],
    ) -> list[NewsEvent]:
        """Normalize and chronologically sort external events."""
        normalized: list[NewsEvent] = []

        for event in events:
            normalized_event = NewsService.normalize_event(event)

            if normalized_event is not None:
                normalized.append(normalized_event)

        return sorted(
            normalized,
            key=lambda event: event.timestamp,
        )

    @staticmethod
    def _payload_events(
        payload: object,
    ) -> list[Mapping[str, object]]:
        """Extract event mappings from supported JSON payloads."""
        if isinstance(payload, dict):
            if "events" in payload:
                payload = payload["events"]
            elif "calendar" in payload:
                payload = payload["calendar"]
            else:
                payload = [payload]

        if not isinstance(payload, list):
            raise ValueError("Unsupported news JSON structure.")

        return [
            item
            for item in payload
            if isinstance(item, dict)
        ]

    @staticmethod
    def load_json(path: Path) -> list[NewsEvent]:
        """Load and normalize economic events from JSON."""
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        return NewsService.normalize_events(
            NewsService._payload_events(payload),
        )

    @staticmethod
    def load_csv(path: Path) -> list[NewsEvent]:
        """Load and normalize economic events from CSV."""
        events: list[NewsEvent] = []

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                event = NewsService.normalize_event(
                    {
                        "date": row.get("date"),
                        "currency": row.get("currency"),
                        "impact": row.get("impact"),
                        "title": row.get("event") or row.get("title"),
                        "actual": row.get("actual"),
                        "forecast": row.get("forecast"),
                        "previous": row.get("previous"),
                    }
                )

                if event is not None:
                    events.append(event)

        return sorted(
            events,
            key=lambda event: event.timestamp,
        )

    @staticmethod
    def load_file(filename: str | Path) -> list[NewsEvent]:
        """Load and normalize economic events from JSON or CSV."""
        path = Path(filename)

        if not path.exists():
            raise FileNotFoundError(
                f"News file does not exist: {path}"
            )

        if path.suffix.lower() == ".csv":
            return NewsService.load_csv(path)

        return NewsService.load_json(path)

    @staticmethod
    def events(
        filename: str | Path | None = None,
    ) -> list[NewsEvent]:
        """Return normalized events from an optional news file."""
        if filename is None:
            return []

        return NewsService.load_file(filename)
