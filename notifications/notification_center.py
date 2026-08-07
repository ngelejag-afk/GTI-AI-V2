from __future__ import annotations
"""
GTI AI
Notification Center
Version 1.0
"""


from collections import Counter

from notifications.notification_history import NotificationHistory


class NotificationCenter:
    """
    Provides notification statistics and history.
    """

    @staticmethod
    def history() -> list:
        """
        Return all stored notifications.
        """
        return NotificationHistory.get_all()

    @staticmethod
    def total() -> int:
        """
        Return total notifications.
        """
        return NotificationHistory.count()

    @staticmethod
    def statistics() -> dict:
        """
        Return BUY / SELL / WAIT counts.
        """
        history = NotificationHistory.get_all()

        counter = Counter(
            item.get("decision", "WAIT")
            for item in history
        )

        return {
            "BUY": counter.get("BUY", 0),
            "SELL": counter.get("SELL", 0),
            "WAIT": counter.get("WAIT", 0),
            "TOTAL": len(history),
        }

    @staticmethod
    def latest(limit: int = 10) -> list:
        """
        Return the latest notifications.
        """
        history = NotificationHistory.get_all()

        if limit <= 0:
            return []

        return history[-limit:]
