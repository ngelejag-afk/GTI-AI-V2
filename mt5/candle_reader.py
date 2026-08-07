from __future__ import annotations

"""
GTI AI
Candle Reader
Version 2.0
"""


from mt5.mt5_connector import MT5Connector


class CandleReader:
    """
    Reads candle data from MetaTrader 5.
    """

    def __init__(self) -> None:
        self.connector = MT5Connector()

    def get_candles(self, symbol: str, timeframe, count: int = 100):
        """
        Return the latest candles.

        Returns an empty list if MT5 is unavailable.
        """

        if not self.connector.connect():
            return []

        try:
            import MetaTrader5 as mt5
        except ModuleNotFoundError:
            return []

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)

        if rates is None:
            return []

        return list(rates)

    @staticmethod
    def read(symbol: str, timeframe, count: int = 100):
        """
        Compatibility wrapper used by MultiTimeframeReader.
        """

        return CandleReader().get_candles(
            symbol=symbol,
            timeframe=timeframe,
            count=count,
        )
