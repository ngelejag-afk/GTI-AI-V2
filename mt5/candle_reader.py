from __future__ import annotations

from mt5.bridge_client import BridgeMarketData


class CandleReader:
    """
    Candle reader for GTI-AI-V2.

    Android/Termux does not require the MetaTrader5 Python package.
    Candles are obtained from the read-only MT5 Bridge.
    """

    @classmethod
    def get_candles(
        cls,
        symbol: str = "XAUUSD",
        timeframe: str = "H1",
        count: int = 200,
    ):
        return BridgeMarketData.candles(
            symbol,
            timeframe,
            count,
        )

    @classmethod
    def read(
        cls,
        symbol: str = "XAUUSD",
        timeframe: str = "H1",
        count: int = 200,
    ):
        return cls.get_candles(symbol, timeframe, count)
