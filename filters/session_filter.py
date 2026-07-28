"""
GTI AI
Session Filter
Version 1.0
"""

from __future__ import annotations

from datetime import datetime, timezone


class SessionFilter:
    """
    Determines whether trading is allowed based on UTC market sessions.
    """

    LONDON_OPEN = 7
    LONDON_CLOSE = 16

    NEW_YORK_OPEN = 12
    NEW_YORK_CLOSE = 21

    @staticmethod
    def current_hour() -> int:
        """
        Return the current UTC hour.
        """
        return datetime.now(timezone.utc).hour

    @classmethod
    def current_session(cls) -> str:
        """
        Return the current trading session.
        """

        hour = cls.current_hour()

        if cls.LONDON_OPEN <= hour < cls.LONDON_CLOSE:
            return "LONDON"

        if cls.NEW_YORK_OPEN <= hour < cls.NEW_YORK_CLOSE:
            return "NEW_YORK"

        return "CLOSED"

    @classmethod
    def is_trading_allowed(cls) -> bool:
        """
        Return True when trading is allowed.
        """

        return cls.current_session() != "CLOSED"

    @classmethod
    def status(cls) -> dict:
        """
        Return the current session status.
        """

        session = cls.current_session()

        return {
            "allowed": session != "CLOSED",
            "session": session,
        }
