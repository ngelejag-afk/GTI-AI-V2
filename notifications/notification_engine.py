"""
GTI AI
Notification Engine
Version 2.0
"""


class NotificationEngine:
    """
    Central notification engine.

    Currently prints notifications.
    Future versions will support Android
    Push Notifications.
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
        Sends a notification.

        Version 2:
        - Prevent duplicate notifications
        - Format notification message
        """

        message = cls.format(signal)

        if message == cls._last_message:
            return False

        cls._last_message = message

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
