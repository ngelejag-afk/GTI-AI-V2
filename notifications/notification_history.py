<<<<<<< HEAD
class NotificationHistory:
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def add(cls, *args, **kwargs):
        pass

    def add_notification(self, *args, **kwargs):
        pass

    def get_history(self, *args, **kwargs):
        return []

    @classmethod
    def get_all(cls, *args, **kwargs):
        return []
=======
"""
GTI AI
Notification History
Version 1.0
"""

from __future__ import annotations

from collections import deque


class NotificationHistory:
    """
    Stores recent notifications.
    """

    _history = deque(maxlen=50)

    @classmethod
    def add(cls, signal: dict) -> None:
        cls._history.append({
            "decision": signal.get("decision"),
            "confidence": signal.get("confidence"),
            "market_bias": signal.get("market_bias"),
            "entry": signal.get("entry"),
            "stop_loss": signal.get("stop_loss"),
            "take_profit": signal.get("take_profit"),
        })

    @classmethod
    def get_all(cls) -> list:
        return list(cls._history)

    @classmethod
    def clear(cls) -> None:
        cls._history.clear()

    @classmethod
    def count(cls) -> int:
        return len(cls._history)

