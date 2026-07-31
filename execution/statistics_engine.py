"""
GTI AI
Statistics Engine
Version 1.0
"""

from __future__ import annotations


class StatisticsEngine:
    """
    Tracks trading performance statistics.
    """

    _stats = {
        "total_trades": 0,
        "wins": 0,
        "losses": 0,
        "breakeven": 0,
        "consecutive_wins": 0,
        "consecutive_losses": 0,
        "gross_profit": 0.0,
        "gross_loss": 0.0,
    }

    @classmethod
    def record(
        cls,
        result: str,
        profit: float = 0.0,
    ) -> None:
        """
        Record a completed trade.
        """

        cls._stats["total_trades"] += 1

        result = result.upper()

        if result == "WIN":
            cls._stats["wins"] += 1
            cls._stats["consecutive_wins"] += 1
            cls._stats["consecutive_losses"] = 0
            cls._stats["gross_profit"] += abs(profit)

        elif result == "LOSS":
            cls._stats["losses"] += 1
            cls._stats["consecutive_losses"] += 1
            cls._stats["consecutive_wins"] = 0
            cls._stats["gross_loss"] += abs(profit)

        else:
            cls._stats["breakeven"] += 1
            cls._stats["consecutive_wins"] = 0
            cls._stats["consecutive_losses"] = 0

    @classmethod
    def summary(cls) -> dict:
        """
        Return trading statistics.
        """

        total = cls._stats["total_trades"]

        if total == 0:
            win_rate = 0.0
        else:
            win_rate = round(
                cls._stats["wins"] / total * 100,
                2,
            )

        if cls._stats["gross_loss"] == 0:
            profit_factor = 0.0
        else:
            profit_factor = round(
                cls._stats["gross_profit"]
                / cls._stats["gross_loss"],
                2,
            )

        return {
            **cls._stats,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
        }

    @classmethod
    def reset(cls) -> None:
        """
        Reset all statistics.
        """

        cls._stats = {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "breakeven": 0,
            "consecutive_wins": 0,
            "consecutive_losses": 0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
        }
