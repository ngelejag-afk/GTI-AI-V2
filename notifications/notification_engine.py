"""
GTI AI
Notification Engine
Version 1.0
"""


class NotificationEngine:
    """
    Central notification engine.
    """

    _last_message = ""

    @classmethod
    def send(cls, signal: dict) -> bool:
        """
        Stores the latest notification.
        """

        message = (
            f"{signal.get('decision', 'WAIT')} | "
            f"{signal.get('confidence', 0)}% | "
            f"Entry: {signal.get('entry', 0)}"
        )

        if message == cls._last_message:
            return False

        cls._last_message = message

        print("=" * 45)
        print(" GTI AI NOTIFICATION")
        print("=" * 45)
        print(message)
        print("=" * 45)

        return True

    @classmethod
    def last_message(cls) -> str:
        return cls._last_message
