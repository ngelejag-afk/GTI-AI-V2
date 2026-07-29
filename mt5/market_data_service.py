"""
GTI AI
Market Data Service
Version 2.0
"""

from __future__ import annotations

from mt5.multi_timeframe_reader import MultiTimeframeReader


class MarketDataService:
    """
    Provides centralized market data for
    simulation, paper trading and live trading.
    """

    DEFAULT_TIMEFRAME = "M15"

    @staticmethod
    def get_market_data(
        symbol: str = "XAUUSD",
        bars: int = 500,
    ) -> dict:
        """
        Return market candles, close prices and latest price.
        """

        timeframes = MultiTimeframeReader.read(
            symbol=symbol,
            bars=bars,
        )

        close_prices: dict[str, list[float]] = {}

        latest_price: float | None = None

        for timeframe, candles in timeframes.items():
            closes: list[float] = []

            for candle in candles:
                try:
                    closes.append(float(candle["close"]))
                except (KeyError, IndexError, TypeError):
                    continue

            close_prices[timeframe] = closes

            if (
                timeframe == MarketDataService.DEFAULT_TIMEFRAME
                and closes
            ):
                latest_price = closes[-1]

        if latest_price is None:
            for closes in close_prices.values():
                if closes:
                    latest_price = closes[-1]
                    break

        return {
            "symbol": symbol,
            "timeframes": timeframes,
            "close_prices": close_prices,
            "latest_price": latest_price,
        }
