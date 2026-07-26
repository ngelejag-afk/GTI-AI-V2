"""
GTI AI
Market Analyzer
Version 1.0
"""

from indicators.ema_engine import EMAEngine
from strategy.trend_engine import TrendEngine


class MarketAnalyzer:
    """
    Coordinates market analysis.
    """

    @staticmethod
    def analyze(prices: list[float]) -> dict:
        ema20 = EMAEngine.latest(prices, 20)
        ema50 = EMAEngine.latest(prices, 50)
        ema200 = EMAEngine.latest(prices, 200)

        trend = TrendEngine.analyze(prices)

        ema_aligned = (
            ema20 is not None
            and ema50 is not None
            and ema200 is not None
            and ema20 > ema50 > ema200
        )

        return {
            "ema20": ema20,
            "ema50": ema50,
            "ema200": ema200,
            "trend": trend,
            "ema_aligned": ema_aligned,
        }
