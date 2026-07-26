"""
GTI AI
Market Structure Engine
Version 1.0
"""

from models.market_data import MarketData


class MarketStructureEngine:
    """
    Detects basic market structure.
    """

    @staticmethod
    def higher_high(previous: MarketData, current: MarketData) -> bool:
        return current.high > previous.high

    @staticmethod
    def higher_low(previous: MarketData, current: MarketData) -> bool:
        return current.low > previous.low

    @staticmethod
    def lower_high(previous: MarketData, current: MarketData) -> bool:
        return current.high < previous.high

    @staticmethod
    def lower_low(previous: MarketData, current: MarketData) -> bool:
        return current.low < previous.low

    @staticmethod
    def trend(previous: MarketData, current: MarketData) -> str:
        if (
            MarketStructureEngine.higher_high(previous, current)
            and MarketStructureEngine.higher_low(previous, current)
        ):
            return "UPTREND"

        if (
            MarketStructureEngine.lower_high(previous, current)
            and MarketStructureEngine.lower_low(previous, current)
        ):
            return "DOWNTREND"

        return "RANGE"
