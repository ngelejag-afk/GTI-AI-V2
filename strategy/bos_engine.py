"""
GTI AI
Break Of Structure Engine
Version 1.0
"""

from models.market_data import MarketData


class BOSEngine:
    """
    Detects Break Of Structure (BOS).
    """

    @staticmethod
    def bullish(previous: MarketData, current: MarketData) -> bool:
        """
        Bullish BOS:
        Current candle closes above the previous high.
        """
        return current.close > previous.high

    @staticmethod
    def bearish(previous: MarketData, current: MarketData) -> bool:
        """
        Bearish BOS:
        Current candle closes below the previous low.
        """
        return current.close < previous.low
