"""
GTI AI
Trend Engine
Version 1.0
"""

from indicators.ema_engine import EMAEngine


class TrendEngine:
    """
    Determines the market trend using EMA alignment.
    """

    @staticmethod
    def analyze(prices: list[float]) -> str:
        ema20 = EMAEngine.latest(prices, 20)
        ema50 = EMAEngine.latest(prices, 50)
        ema200 = EMAEngine.latest(prices, 200)

        if ema20 is None or ema50 is None or ema200 is None:
            return "UNKNOWN"

        if ema20 > ema50 > ema200:
            return "STRONG_BULLISH"

        if ema20 < ema50 < ema200:
            return "STRONG_BEARISH"

        if ema20 > ema50:
            return "BULLISH"

        if ema20 < ema50:
            return "BEARISH"

        return "SIDEWAYS"
