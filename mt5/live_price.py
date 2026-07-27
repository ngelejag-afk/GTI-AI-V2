"""
GTI AI
Live Price Service
Version 1.0
"""

from __future__ import annotations

try:
    import MetaTrader5 as mt5
except ModuleNotFoundError:
    mt5 = None


class LivePriceService:
    """
    Reads the latest market price.
    """

    @staticmethod
    def get_price(symbol: str) -> dict:
        """
        Return the latest price information.

        Returns an empty dictionary if MT5 is unavailable.
        """
        if mt5 is None:
            return {}

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            return {}

        return {
            "bid": tick.bid,
            "ask": tick.ask,
            "last": tick.last,
            "volume": tick.volume,
            "time": tick.time,
        }
