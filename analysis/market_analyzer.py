"""
GTI AI
Market Analyzer
Version 2.0
"""

from typing import Sequence

from strategy.domain.models import Candle
from strategy.domain.trend_engine import TrendEngine


class MarketAnalyzer:
    """Performs market analysis using domain trend detection."""

    @staticmethod
    def analyze(candles: Sequence[Candle]) -> dict:
        """Analyze market conditions from closed candles."""
        candles = candles or []

        if not candles:
            return {
                "trend": TrendEngine.INSUFFICIENT_DATA,
                "ema_aligned": False,
                "market_bias": "NEUTRAL",
            }

        trend = TrendEngine.analyze(candles)

        ema_aligned = trend in {
            TrendEngine.BULLISH,
            TrendEngine.BEARISH,
        }

        if trend == TrendEngine.BULLISH:
            market_bias = "BULLISH"
        elif trend == TrendEngine.BEARISH:
            market_bias = "BEARISH"
        else:
            market_bias = "NEUTRAL"

        return {
            "trend": trend,
            "ema_aligned": ema_aligned,
            "market_bias": market_bias,
        }
