"""
GTI AI
Market Analyzer
Version 2.0
"""

from indicators.ema_engine import EMAEngine
from strategy.trend_engine import TrendEngine


class MarketAnalyzer:
    """
    Performs market analysis using EMA and trend detection.
    """

    @staticmethod
    def analyze(prices: list[float]) -> dict:
        """
        Analyze market conditions.
        """

        if not prices:
            return {
                "ema20": None,
                "ema50": None,
                "ema200": None,
                "trend": "UNKNOWN",
                "ema_aligned": False,
                "market_bias": "NEUTRAL",
            }

        ema20 = EMAEngine.latest(prices, 20)
        ema50 = EMAEngine.latest(prices, 50)
        ema200 = EMAEngine.latest(prices, 200)

        trend = TrendEngine.analyze(prices)

        bullish_alignment = (
            ema20 is not None
            and ema50 is not None
            and ema200 is not None
            and ema20 > ema50 > ema200
        )

        bearish_alignment = (
            ema20 is not None
            and ema50 is not None
            and ema200 is not None
            and ema20 < ema50 < ema200
        )

        ema_aligned = bullish_alignment or bearish_alignment

        if bullish_alignment:
            market_bias = "BULLISH"
        elif bearish_alignment:
            market_bias = "BEARISH"
        else:
            market_bias = "NEUTRAL"

        return {
            "ema20": ema20,
            "ema50": ema50,
            "ema200": ema200,
            "trend": trend,
            "ema_aligned": ema_aligned,
            "market_bias": market_bias,
        }
