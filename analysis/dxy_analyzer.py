from __future__ import annotations
"""
GTI AI
DXY Analyzer
Version 1.0
"""


from analysis.market_analyzer import MarketAnalyzer


class DXYAnalyzer:
    """
    Analyzes the US Dollar Index (DXY) and provides
    confirmation for XAUUSD trading decisions.
    """

    @staticmethod
    def analyze(prices: list[float]) -> dict:
        """
        Analyze DXY market conditions.
        """

        market = MarketAnalyzer.analyze(prices)

        trend = market["trend"]

        if trend in ("STRONG_BULLISH", "BULLISH"):
            signal = "USD_STRENGTH"

        elif trend in ("STRONG_BEARISH", "BEARISH"):
            signal = "USD_WEAKNESS"

        else:
            signal = "NEUTRAL"

        return {
            "trend": trend,
            "market_bias": market["market_bias"],
            "ema_aligned": market["ema_aligned"],
            "signal": signal,
            "confirmed": signal != "NEUTRAL",
        }
