"""
GTI AI
Candlestick Engine
Version 1.0
"""

from models.market_data import MarketData


class CandlestickEngine:
    """
    Detects basic candlestick patterns.
    """

    @staticmethod
    def bullish_engulfing(previous: MarketData, current: MarketData) -> bool:
        return (
            previous.close < previous.open
            and current.close > current.open
            and current.open < previous.close
            and current.close > previous.open
        )

    @staticmethod
    def bearish_engulfing(previous: MarketData, current: MarketData) -> bool:
        return (
            previous.close > previous.open
            and current.close < current.open
            and current.open > previous.close
            and current.close < previous.open
        )

    @staticmethod
    def doji(candle: MarketData) -> bool:
        body = abs(candle.close - candle.open)
        candle_range = candle.high - candle.low

        if candle_range == 0:
            return False

        return body <= candle_range * 0.1

    @staticmethod
    def hammer(candle: MarketData) -> bool:
        body = abs(candle.close - candle.open)
        lower_shadow = min(candle.open, candle.close) - candle.low
        upper_shadow = candle.high - max(candle.open, candle.close)

        return (
            lower_shadow > body * 2
            and upper_shadow < body
        )

    @staticmethod
    def shooting_star(candle: MarketData) -> bool:
        body = abs(candle.close - candle.open)
        upper_shadow = candle.high - max(candle.open, candle.close)
        lower_shadow = min(candle.open, candle.close) - candle.low

        return (
            upper_shadow > body * 2
            and lower_shadow < body
        )
