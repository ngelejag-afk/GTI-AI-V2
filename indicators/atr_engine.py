"""
GTI AI
Average True Range Engine
Version 1.0
"""

from models.market_data import MarketData


class ATREngine:
    """
    Calculates Average True Range (ATR).
    """

    @staticmethod
    def calculate(candles: list[MarketData], period: int = 14) -> float:
        """
        Calculate ATR from candle data.
        """

        if len(candles) < period + 1:
            return 0.0

        true_ranges = []

        for i in range(1, len(candles)):
            current = candles[i]
            previous = candles[i - 1]

            tr = max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close),
            )

            true_ranges.append(tr)

        atr_values = true_ranges[-period:]

        return sum(atr_values) / period
