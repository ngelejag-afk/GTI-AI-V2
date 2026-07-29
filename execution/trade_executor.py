"""
GTI AI
Trade History
Version 1.0
"""

from __future__ import annotations

from datetime import datetime


class TradeHistory:
    """
    Stores executed trades in memory.
    """

    _trades = []

    @classmethod
    def add(cls, trade: dict) -> None:
        """
        Store a trade record.
        """

        record = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": trade.get("symbol", "XAUUSD"),
            "decision": trade.get("decision", "WAIT"),
            "entry": trade.get("entry", 0.0),
            "stop_loss": trade.get("stop_loss", 0.0),
            "take_profit": trade.get("take_profit", 0.0),
            "confidence": trade.get("confidence", 0),
            "status": trade.get("status", "OPEN"),
        }

        cls._trades.append(record)

    @classmethod
    def all(cls) -> list:
        """
        Return all trades.
        """

        return list(cls._trades)

    @classmethod
    def latest(cls, limit: int = 10) -> list:
        """
        Return the latest trades.
        """

        if limit <= 0:
            return []

        return cls._trades[-limit:]

    @classmethod
    def total(cls) -> int:
        """
        Return total number of trades.
        """

        return len(cls._trades)

    @classmethod
    def clear(cls) -> None:
        """
        Clear trade history.
        """

        cls._trades.clear()
