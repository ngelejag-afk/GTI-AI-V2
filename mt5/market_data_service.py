"""
GTI AI
Market Data Service
Version 1.0
"""

from __future__ import annotations

from mt5.multi_timeframe_reader import MultiTimeframeReader


class MarketDataService:
    """
    Provides market data for both simulation and live trading.
    """

    @staticmethod
    def get_market_data(
        symbol: str = "XAUUSD",
        bars: int = 500,
    ) -> dict:
        """
        Returns candles and close prices for all supported timeframes.

        If market data is unavailable, empty collections are returned.
        """

        timeframes = MultiTimeframeReader.read(
            symbol=symbol,
            bars=bars,
        )

        close_prices: dict[str, list[float]] = {}

        for timeframe, candles in timeframes.items():
            closes: list[float] = []

            for candle in candles:
                try:
                    closes.append(float(candle["close"]))
                except (KeyError, IndexError, TypeError):
                    continue

            close_prices[timeframe] = closes

        return {
            "symbol": symbol,
            "timeframes": timeframes,
            "close_prices": close_prices,
        }
