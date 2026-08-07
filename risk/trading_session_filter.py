from __future__ import annotations
"""
GTI AI
Trading Session Filter
Version 1.0
"""


from datetime import datetime, time


class TradingSessionFilter:
    """
    Controls whether trading is allowed based on
    the current trading session.
    """

    SESSIONS = {
        "ASIA": (
            time(hour=0, minute=0),
            time(hour=8, minute=59),
        ),
        "LONDON": (
            time(hour=9, minute=0),
            time(hour=16, minute=59),
        ),
        "NEW_YORK": (
            time(hour=17, minute=0),
            time(hour=23, minute=59),
        ),
    }

    ENABLED_SESSIONS = {
        "LONDON",
        "NEW_YORK",
    }

    @classmethod
    def current_session(cls) -> str:
        """
        Return the current trading session.
        """

        now = datetime.utcnow().time()

        for name, (start, end) in cls.SESSIONS.items():
            if start <= now <= end:
                return name

        return "UNKNOWN"

    @classmethod
    def trading_allowed(cls) -> bool:
        """
        Check whether trading is allowed.
        """

        return cls.current_session() in cls.ENABLED_SESSIONS

    @classmethod
    def status(cls) -> dict:
        """
        Return the current session status.
        """

        session = cls.current_session()

        return {
            "current_session": session,
            "enabled_sessions": sorted(cls.ENABLED_SESSIONS),
            "trading_allowed": session in cls.ENABLED_SESSIONS,
        }

    @classmethod
    def enable_session(cls, session: str) -> None:
        """
        Enable a trading session.
        """

        cls.ENABLED_SESSIONS.add(session.upper())

    @classmethod
    def disable_session(cls, session: str) -> None:
        """
        Disable a trading session.
        """

        cls.ENABLED_SESSIONS.discard(session.upper())
