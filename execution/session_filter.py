from __future__ import annotations
"""
GTI AI
Session Filter
Version 1.0
"""


from datetime import datetime, timezone


class SessionFilter:
    """
    Validates whether trading is allowed during
    the configured trading sessions.
    """

    LONDON_OPEN = 7
    LONDON_CLOSE = 16

    NEW_YORK_OPEN = 12
    NEW_YORK_CLOSE = 21

    @staticmethod
    def validate() -> dict:
        """
        Validate whether the current UTC time is
        inside the supported trading sessions.
        """

        hour = datetime.now(timezone.utc).hour

        london = (
            SessionFilter.LONDON_OPEN
            <= hour
            < SessionFilter.LONDON_CLOSE
        )

        new_york = (
            SessionFilter.NEW_YORK_OPEN
            <= hour
            < SessionFilter.NEW_YORK_CLOSE
        )

        valid = london or new_york

        if london:
            session = "LONDON"
        elif new_york:
            session = "NEW_YORK"
        else:
            session = "CLOSED"

        return {
            "valid": valid,
            "session": session,
            "hour": hour,
            "reason": (
                f"{session} session active."
                if valid
                else "Outside supported trading sessions."
            ),
        }
