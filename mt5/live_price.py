
"""
GTI AI
MT5 Live Price Service
Version 1.0
"""

from datetime import datetime

import MetaTrader5 as mt5


class LivePriceService:
    """
    Reads live prices from MetaTrader 5.
    """

    @staticmethod
    def get(symbol: str) -> dict | None:
        """
        Returns the latest tick data.
        """
        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            return None

        return {
            "symbol": symbol,
            "bid": tick.bid,
            "ask": tick.ask,
            "last": tick.last,
            "volume": tick.volume,
            "time": datetime.fromtimestamp(tick.time),
        }
