from __future__ import annotations
"""
GTI AI
Trade History
Version 1.0
"""



class TradeHistory:
    """
    Stores executed and simulated trades.
    """

    _history: list[dict] = []

    @classmethod
    def add(cls, trade: dict) -> None:
        """
        Save a trade.
        """
        cls._history.append(dict(trade))

    @classmethod
    def all(cls) -> list[dict]:
        """
        Return all saved trades.
        """
        return list(cls._history)

    @classmethod
    def latest(cls) -> dict | None:
        """
        Return the most recent trade.
        """
        if not cls._history:
            return None

        return cls._history[-1]

    @classmethod
    def total(cls) -> int:
        """
        Return total number of saved trades.
        """
        return len(cls._history)

    @classmethod
    def clear(cls) -> None:
        """
        Remove all stored trades.
        """
        cls._history.clear()
