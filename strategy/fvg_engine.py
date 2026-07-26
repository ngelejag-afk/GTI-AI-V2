"""
GTI AI
Fair Value Gap Engine
Version 1.0
"""

from models.market_data import MarketData


class FVGEngine:
    """
    Detects basic Fair Value Gaps (FVG).
    """

    @staticmethod
    def bullish(
        first: MarketData,
        second: MarketData,
        third: MarketData,
    ) -> bool:
        """
        Bullish FVG:
        Third candle low remains above
        the first candle high.
        """
        return third.low > first.high

    @staticmethod
    def bearish(
        first: MarketData,
        second: MarketData,
        third: MarketData,
    ) -> bool:
        """
        Bearish FVG:
        Third candle high remains below
        the first candle low.
        """
        return third.high < first.low

    @staticmethod
    def signal(
        first: MarketData,
        second: MarketData,
        third: MarketData,
    ) -> str:

        if FVGEngine.bullish(first, second, third):
            return "BULLISH_FVG"

        if FVGEngine.bearish(first, second, third):
            return "BEARISH_FVG"

        return "NO_FVG"
