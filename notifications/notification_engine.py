"""
GTI AI
Notification Engine
Version 3.0
"""

from __future__ import annotations

from notifications.notification_history import NotificationHistory


class NotificationEngine:
    """
    Central notification engine.

    Features:
    - Formats notifications
    - Prevents duplicate notifications
    - Stores notification history
    """

    _last_message = ""

    @staticmethod
    def format(signal: dict) -> str:
        return (
            f"{signal.get('decision', 'WAIT')}\n"
            f"Confidence : {signal.get('confidence', 0)}%\n"
            f"Trend      : {signal.get('market_bias', 'Unknown')}\n"
            f"Entry      : {signal.get('entry', 0)}\n"
            f"Stop Loss  : {signal.get('stop_loss', 0)}\n"
            f"Take Profit: {signal.get('take_profit', 0)}"
        )

    @classmethod
    def send(cls, signal: dict) -> bool:
        """
        Send a notification if it is new.
        """

        message = cls.format(signal)

        if message == cls._last_message:
            return False

        cls._last_message = message

        NotificationHistory.add(signal)

        print()
        print("=" * 50)
        print(" GTI AI NOTIFICATION")
        print("=" * 50)
        print(message)
        print("=" * 50)

        return True

    @classmethod
    def last_message(cls) -> str:
        return cls._last_message

    @classmethod
    def history(cls) -> list:
        return NotificationHistory.get_all()

    @classmethod
    def clear_history(cls) -> None:
        NotificationHistory.clear()
