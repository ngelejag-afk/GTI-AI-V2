from __future__ import annotations
"""
GTI AI
EMA Engine
Version 1.0
"""


from typing import List


class EMAEngine:
    """
    Calculates Exponential Moving Averages.
    """

    @staticmethod
    def calculate(prices: List[float], period: int) -> List[float]:
        """
        Calculate EMA values for a list of closing prices.
        """
        if len(prices) < period:
            return []

        multiplier = 2 / (period + 1)

        ema = [sum(prices[:period]) / period]

        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])

        return ema

    @staticmethod
    def latest(prices: List[float], period: int) -> float | None:
        """
        Return the latest EMA value.
        """
        values = EMAEngine.calculate(prices, period)

        if not values:
            return None

        return values[-1]
