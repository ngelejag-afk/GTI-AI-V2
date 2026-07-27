"""
GTI AI
Liquidity Sweep Engine
Version 1.0
"""

from models.market_data import MarketData


class LiquiditySweepEngine:
    """
    Detects basic liquidity sweeps.
    """

    @staticmethod
    def buy_side(previous: MarketData, current: MarketData) -> bool:
        """
        Buy-side liquidity sweep:
        Price trades above the previous high
        but closes back below it.
        """
        return (
            current.high > previous.high
            and current.close < previous.high
        )

    @staticmethod
    def sell_side(previous: MarketData, current: MarketData) -> bool:
        """
        Sell-side liquidity sweep:
        Price trades below the previous low
        but closes back above it.
        """
        return (
            current.low < previous.low
            and current.close > previous.low
        )

    @staticmethod
    def signal(previous: MarketData, current: MarketData) -> str:
        if LiquiditySweepEngine.buy_side(previous, current):
            return "BUY_SIDE_LIQUIDITY"

        if LiquiditySweepEngine.sell_side(previous, current):
            return "SELL_SIDE_LIQUIDITY"

        return "NO_LIQUIDITY_SWEEP"
