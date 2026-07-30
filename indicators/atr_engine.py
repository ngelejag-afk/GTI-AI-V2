"""
GTI AI
ATR Engine
Version 1.0
"""

from __future__ import annotations


class ATREngine:
    """
    Calculates the Average True Range (ATR).
    """

    @staticmethod
    def calculate(
        candles: list[dict],
        period: int = 14,
    ) -> float | None:
        """
        Calculate the latest ATR value.

        Candle format:
        {
            "high": float,
            "low": float,
            "close": float,
        }
        """

        if len(candles) < period + 1:
            return None

        true_ranges: list[float] = []

        for index in range(1, len(candles)):
            current = candles[index]
            previous = candles[index - 1]

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

        return sum(latest) / period
