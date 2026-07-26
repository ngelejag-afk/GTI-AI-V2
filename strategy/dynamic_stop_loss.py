
"""
GTI AI
Dynamic Stop Loss Engine
Version 1.0
"""

from indicators.atr_engine import ATREngine


class DynamicStopLoss:
    """
    Calculates a dynamic stop loss using ATR.
    """

    DEFAULT_MULTIPLIER = 2.0

    @staticmethod
    def calculate(
        decision: str,
        entry: float,
        candles: list,
        multiplier: float = DEFAULT_MULTIPLIER,
    ) -> float:
        """
        Returns a dynamic stop loss.
        """
        atr = ATREngine.calculate(candles)

        if atr == 0:
            return 0.0

        distance = atr * multiplier

        if decision == "BUY":
            return round(entry - distance, 2)

        if decision == "SELL":
            return round(entry + distance, 2)

        return 0.0
