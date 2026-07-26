"""
GTI AI
Stop Loss Engine
Version 1.0
"""


class StopLossEngine:
    """
    Calculates the stop loss price.
    """

    DEFAULT_POINTS = 5.0

    @staticmethod
    def calculate(
        decision: str,
        entry: float,
        points: float = DEFAULT_POINTS,
    ) -> float:
        """
        Returns the stop loss price.
        """
        if decision == "BUY":
            return round(entry - points, 2)

        if decision == "SELL":
            return round(entry + points, 2)

        return 0.0
