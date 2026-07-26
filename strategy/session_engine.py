"""
GTI AI
Session Engine
Version 1.0
"""

from datetime import datetime, timezone


class SessionEngine:
    """
    Determines the active Forex trading session.
    Times are in UTC.
    """

    @staticmethod
    def current_session(now: datetime | None = None) -> str:
        if now is None:
            now = datetime.now(timezone.utc)

        hour = now.hour

        if 0 <= hour < 8:
            return "TOKYO"

        if 8 <= hour < 16:
            return "LONDON"

        if 13 <= hour < 22:
            return "NEW_YORK"

        return "SYDNEY"

    @staticmethod
    def london_kill_zone(now: datetime | None = None) -> bool:
        if now is None:
            now = datetime.now(timezone.utc)

        return 7 <= now.hour < 10

    @staticmethod
    def new_york_kill_zone(now: datetime | None = None) -> bool:
        if now is None:
            now = datetime.now(timezone.utc)

        return 12 <= now.hour < 15

    @staticmethod
    def trading_allowed(now: datetime | None = None) -> bool:
        return (
            SessionEngine.london_kill_zone(now)
            or SessionEngine.new_york_kill_zone(now)
        )
