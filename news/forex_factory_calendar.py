from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone, timedelta

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
LOOKBACK_MINUTES = 30
LOOKAHEAD_MINUTES = 120
USD = "USD"
HIGH = "HIGH"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_time(value: str) -> datetime:
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _fetch() -> list[dict]:
    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "GTI-AI-V2/1.0"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"NEWS_HTTP_{response.status}")
        data = json.loads(response.read().decode("utf-8"))

    if not isinstance(data, list) or not data:
        raise RuntimeError("NEWS_DATA_EMPTY")

    return data


def check() -> dict:
    now = _utc_now()

    try:
        raw_events = _fetch()
    except Exception as exc:
        return {
            "available": False,
            "safe": False,
            "risk": "HIGH",
            "reason": "NEWS_SOURCE_UNAVAILABLE",
            "error": f"{type(exc).__name__}: {exc}",
        }

    events = []

    try:
        for item in raw_events:
            if not isinstance(item, dict):
                continue

            currency = str(item.get("currency", "")).strip().upper()
            impact = str(item.get("impact", "")).strip().upper()
            title = str(
                item.get("title")
                or item.get("event")
                or item.get("name")
                or ""
            ).strip()

            date_value = item.get("date") or item.get("timestamp")
            if not date_value:
                continue

            event_time = _parse_time(str(date_value))

            events.append({
                "time_utc": event_time,
                "currency": currency,
                "impact": impact,
                "title": title,
            })
    except Exception as exc:
        return {
            "available": False,
            "safe": False,
            "risk": "HIGH",
            "reason": "NEWS_DATA_INVALID",
            "error": f"{type(exc).__name__}: {exc}",
        }

    if not events:
        return {
            "available": False,
            "safe": False,
            "risk": "HIGH",
            "reason": "NEWS_DATA_INVALID",
            "error": "NO_VALID_EVENTS",
        }

    relevant_start = now - timedelta(days=7)
    relevant_end = now + timedelta(days=7)

    if not any(
        relevant_start <= event["time_utc"] <= relevant_end
        for event in events
    ):
        return {
            "available": False,
            "safe": False,
            "risk": "HIGH",
            "reason": "NEWS_DATA_STALE",
            "events_checked": len(events),
        }

    window_start = now - timedelta(minutes=LOOKBACK_MINUTES)
    window_end = now + timedelta(minutes=LOOKAHEAD_MINUTES)

    blocking = [
        event for event in events
        if (
            event["currency"] == USD
            and event["impact"] == HIGH
            and window_start <= event["time_utc"] <= window_end
        )
    ]

    if blocking:
        event = sorted(blocking, key=lambda x: x["time_utc"])[0]
        minutes = int((event["time_utc"] - now).total_seconds() / 60)

        return {
            "available": True,
            "safe": False,
            "risk": "HIGH",
            "reason": "USD_HIGH_IMPACT_NEWS_WINDOW",
            "blocking_event": {
                "title": event["title"],
                "currency": event["currency"],
                "impact": event["impact"],
                "event_time_utc": event["time_utc"].isoformat(),
                "minutes_from_now": minutes,
            },
            "events_checked": len(events),
        }

    return {
        "available": True,
        "safe": True,
        "risk": "LOW",
        "reason": "NO_USD_HIGH_IMPACT_EVENT_IN_WINDOW",
        "events_checked": len(events),
    }


if __name__ == "__main__":
    result = check()

    for key, value in result.items():
        if isinstance(value, dict):
            value = json.dumps(value, default=str)
        print(f"{key}: {value}")
