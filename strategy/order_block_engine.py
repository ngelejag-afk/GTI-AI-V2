"""
GTI AI
Order Block Engine
Version 1.0
"""

from models.market_data import MarketData


class OrderBlockEngine:
    """
    Detects basic bullish and bearish order blocks.
    """

    @staticmethod
    def bullish(previous: MarketData, current: MarketData) -> bool:
        """
        Bullish Order Block:
        Previous candle is bearish and
        current candle closes above the previous high.
        """
        return (
            previous.close < previous.open
            and current.close > previous.high
        )

    @staticmethod
    def bearish(previous: MarketData, current: MarketData) -> bool:
        """
        Bearish Order Block:
        Previous candle is bullish and
        current candle closes below the previous low.
        """
        return (
            previous.close > previous.open
            and current.close < previous.low
        )

    @staticmethod
    def signal(previous: MarketData, current: MarketData) -> str:
        if OrderBlockEngine.bullish(previous, current):
            return "BULLISH_ORDER_BLOCK"

        if OrderBlockEngine.bearish(previous, current):
            return "BEARISH_ORDER_BLOCK"

        return "NO_ORDER_BLOCK"
