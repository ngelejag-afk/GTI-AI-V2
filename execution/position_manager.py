"""
GTI AI
Position Manager
Version 2.0
"""

from __future__ import annotations

from datetime import datetime


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

        entry = float(trade.get("entry", 0.0))

        position = {
            "symbol": trade.get("symbol", "XAUUSD"),
            "decision": trade.get("decision", "WAIT"),
            "entry": entry,
            "current_price": entry,
            "stop_loss": float(trade.get("stop_loss", 0.0)),
            "take_profit": float(trade.get("take_profit", 0.0)),
            "lot_size": float(trade.get("lot_size", 0.01)),
            "confidence": int(trade.get("confidence", 0)),
            "floating_profit": 0.0,
            "floating_pips": 0.0,
            "floating_status": "BREAKEVEN",
            "opened_at": datetime.now(),
            "closed_at": None,
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
            cls._positions[index]["closed_at"] = datetime.now()
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
    def total_profit(cls) -> float:
        """
        Return total floating profit.
        """

        return round(
            sum(
                position.get("floating_profit", 0.0)
                for position in cls.open_positions()
            ),
            2,
        )

    @classmethod
    def clear(cls) -> None:
        """
        Remove all positions.
        """

        cls._positions.clear()
