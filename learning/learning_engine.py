"""
GTI AI
Learning Engine
Version 1.0
"""


class LearningEngine:
    """
    Learns from completed trades.
    """

    def __init__(self):
        self.statistics = {
            "total": 0,
            "wins": 0,
            "losses": 0,
        }

    def update(self, trade: dict) -> None:
        """
        Update learning statistics.
        """

        status = trade.get("status")

        if status not in ("WIN", "LOSS"):
            return

        self.statistics["total"] += 1

        if status == "WIN":
            self.statistics["wins"] += 1
        else:
            self.statistics["losses"] += 1

    def confidence(self) -> float:
        """
        Return current win percentage.
        """

        total = self.statistics["total"]

        if total == 0:
            return 0.0

        return round(
            (self.statistics["wins"] / total) * 100,
            2,
        )

    def report(self) -> dict:
        """
        Return learning statistics.
        """

        return {
            **self.statistics,
            "confidence": self.confidence(),
        }
