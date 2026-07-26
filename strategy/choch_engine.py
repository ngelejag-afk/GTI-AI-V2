"""
GTI AI
Change Of Character Engine
Version 1.0
"""

from models.market_data import MarketData


class CHOCHEngine:
    """
    Detects Change of Character (CHOCH).
    """

    @staticmethod
    def bullish(previous: MarketData, current: MarketData) -> bool:
        """
        Bullish CHOCH:
        Current candle creates both a higher high
        and a higher low.
        """
        return (
            current.high > previous.high
            and current.low > previous.low
        )

    @staticmethod
    def bearish(previous: MarketData, current: MarketData) -> bool:
        """
        Bearish CHOCH:
        Current candle creates both a lower high
        and a lower low.
        """
        return (
            current.high < previous.high
            and current.low < previous.low
        )

    @staticmethod
    def signal(previous: MarketData, current: MarketData) -> str:
        if CHOCHEngine.bullish(previous, current):
            return "BULLISH_CHOCH"

        if CHOCHEngine.bearish(previous, current):
            return "BEARISH_CHOCH"

        return "NO_CHOCH"
