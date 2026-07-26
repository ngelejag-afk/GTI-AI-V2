
"""
GTI AI
ATR Engine
Version 1.0
"""


class ATREngine:
    """
    Calculates the Average True Range (ATR).
    """

    @staticmethod
    def calculate(candles: list, period: int = 14) -> float:
        """
        Returns the ATR value.
        """
        if len(candles) < period + 1:
            return 0.0

        true_ranges = []

        for index in range(1, len(candles)):
            current = candles[index]
            previous = candles[index - 1]

            high_low = current.high - current.low
            high_close = abs(current.high - previous.close)
            low_close = abs(current.low - previous.close)

            true_range = max(
                high_low,
                high_close,
                low_close,
            )

            true_ranges.append(true_range)

        atr = sum(true_ranges[-period:]) / period

        return round(atr, 2)
