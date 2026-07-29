"""
GTI AI
Order Manager
Version 1.0
"""

from __future__ import annotations


class OrderManager:
    """
    Validates and prepares trade orders.
    """

    _last_order = None

    @classmethod
    def validate(cls, order: dict) -> bool:
        """
        Validate an order before execution.
        """

        decision = order.get("decision", "WAIT")

        if decision not in ("BUY", "SELL"):
            return False

        entry = float(order.get("entry", 0))

        if entry <= 0:
            return False

        return True

    @classmethod
    def is_duplicate(cls, order: dict) -> bool:
        """
        Check whether this order matches the last submitted order.
        """

        current = (
            order.get("symbol", "XAUUSD"),
            order.get("decision"),
            order.get("entry"),
        )

        return current == cls._last_order

    @classmethod
    def prepare(cls, order: dict) -> dict:
        """
        Prepare a validated order.
        """

        prepared = {
            "symbol": order.get("symbol", "XAUUSD"),
            "decision": order.get("decision"),
            "entry": order.get("entry"),
            "stop_loss": order.get("stop_loss"),
            "take_profit": order.get("take_profit"),
            "confidence": order.get("confidence", 0),
            "status": "READY",
        }

        return prepared

    @classmethod
    def submit(cls, order: dict) -> dict | None:
        """
        Validate and submit an order.
        """

        if not cls.validate(order):
            return None

        if cls.is_duplicate(order):
            return None

        prepared = cls.prepare(order)

        cls._last_order = (
            prepared["symbol"],
            prepared["decision"],
            prepared["entry"],
        )

        return prepared

    @classmethod
    def reset(cls) -> None:
        """
        Reset duplicate order tracking.
        """

        cls._last_order = None
