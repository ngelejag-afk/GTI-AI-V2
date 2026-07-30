"""
GTI AI
ATR Engine
Version 1.1
"""

from __future__ import annotations


class ATREngine:
    """
    Calculates the Average True Range (ATR).
    """

    @staticmethod
    def calculate(
        candles: list,
        period: int = 14,
    ) -> float:
        """
        Calculate the latest ATR value.

        Supports both:

        - Objects with .high/.low/.close
        - Dictionaries with "high"/"low"/"close"
        """

        if len(candles) < period + 1:
            return 0.0

        true_ranges: list[float] = []

        for index in range(1, len(candles)):
            current = candles[index]
            previous = candles[index - 1]

            if hasattr(current, "high"):
                high = float(current.high)
                low = float(current.low)
                previous_close = float(previous.close)
            else:
                high = float(current["high"])
                low = float(current["low"])
                previous_close = float(previous["close"])

            true_range = max(
                high - low,
                abs(high - previous_close),
                abs(low - previous_close),
            )

            true_ranges.append(true_range)

        latest = true_ranges[-period:]

        return round(sum(latest) / period, 2)
