from __future__ import annotations
"""
GTI AI
Performance Monitor
Version 1.0
"""


from collections import Counter


class PerformanceMonitor:
    """
    Tracks AI trading performance.
    """

    _results = []

    @classmethod
    def record(
        cls,
        decision: str,
        confidence: float,
        result: str,
    ) -> None:
        """
        Store a completed trade result.

        result:
            WIN
            LOSS
            BREAKEVEN
        """

        cls._results.append(
            {
                "decision": decision,
                "confidence": confidence,
                "result": result,
            }
        )

    @classmethod
    def summary(cls) -> dict:
        """
        Return overall AI statistics.
        """

        counter = Counter(item["result"] for item in cls._results)

        total = len(cls._results)

        wins = counter.get("WIN", 0)
        losses = counter.get("LOSS", 0)
        breakeven = counter.get("BREAKEVEN", 0)

        if total == 0:
            win_rate = 0.0
            average_confidence = 0.0
        else:
            win_rate = round((wins / total) * 100, 2)
            average_confidence = round(
                sum(item["confidence"] for item in cls._results) / total,
                2,
            )

        return {
            "total": total,
            "wins": wins,
            "losses": losses,
            "breakeven": breakeven,
            "win_rate": win_rate,
            "average_confidence": average_confidence,
        }

    @classmethod
    def history(cls) -> list:
        """
        Return all recorded results.
        """
        return list(cls._results)

    @classmethod
    def reset(cls) -> None:
        """
        Clear all stored performance data.
        """
        cls._results.clear()
