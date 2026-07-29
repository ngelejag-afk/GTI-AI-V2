"""
GTI AI
Position Manager
Version 1.0
"""

from __future__ import annotations


class PositionManager:
    """
    Manages open trading positions.
    """

    _positions = []

    @classmethod
    def open_position(cls, trade: dict) -> None:
        """
        Open a new trading position.
        """

        position = {
            "symbol": trade.get("symbol", "XAUUSD"),
            "decision": trade.get("decision", "WAIT"),
            "entry": trade.get("entry", 0.0),
            "stop_loss": trade.get("stop_loss", 0.0),
            "take_profit": trade.get("take_profit", 0.0),
            "confidence": trade.get("confidence", 0),
            "status": "OPEN",
        }

        cls._positions.append(position)

    @classmethod
    def close_position(cls, index: int) -> bool:
        """
        Close a position by index.
        """

        if 0 <= index < len(cls._positions):
            cls._positions[index]["status"] = "CLOSED"
            return True

        return False

    @classmethod
    def open_positions(cls) -> list:
        """
        Return all open positions.
        """

        return [
            position
            for position in cls._positions
            if position["status"] == "OPEN"
        ]

    @classmethod
    def all_positions(cls) -> list:
        """
        Return all positions.
        """

        return list(cls._positions)

    @classmethod
    def total_open(cls) -> int:
        """
        Return total open positions.
        """

        return len(cls.open_positions())

    @classmethod
    def clear(cls) -> None:
        """
        Remove all positions.
        """

        cls._positions.clear()
