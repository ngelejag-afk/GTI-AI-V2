
"""
GTI AI
Stop Loss Engine
Version 2.0
"""


class StopLossEngine:
    """
    Calculates Stop Loss using
    a configurable percentage.
    """

    @staticmethod
    def calculate(
        entry: float,
        decision: str,
        risk_percent: float = 0.5,
    ) -> float:

        decision = decision.upper()

        distance = entry * (risk_percent / 100)

        if decision == "BUY":
            return round(entry - distance, 2)

        if decision == "SELL":
            return round(entry + distance, 2)

        return round(entry, 2)
