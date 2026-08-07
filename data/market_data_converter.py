from __future__ import annotations
"""
GTI AI
Market Data Converter
Version 1.0
"""


from datetime import datetime

from models.market_data import MarketData


class MarketDataConverter:
    """
    Converts raw MT5 candle data into a MarketData object.
    """

    @staticmethod
    def convert(rate, symbol: str, timeframe: str) -> MarketData:
        return MarketData(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.fromtimestamp(rate["time"]),
            open=float(rate["open"]),
            high=float(rate["high"]),
            low=float(rate["low"]),
            close=float(rate["close"]),
            volume=float(rate["tick_volume"]),
            spread=float(rate["spread"]),
        )
