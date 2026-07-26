"""
GTI AI
MT5 Symbol Service
Version 1.0
"""

import MetaTrader5 as mt5


class SymbolService:
    """
    Reads symbol information from MetaTrader 5.
    """

    @staticmethod
    def get(symbol: str) -> dict | None:
        """
        Returns symbol information.
        """
        info = mt5.symbol_info(symbol)

        if info is None:
            return None

        return {
            "symbol": info.name,
            "description": info.description,
            "bid": info.bid,
            "ask": info.ask,
            "spread": info.spread,
            "digits": info.digits,
            "point": info.point,
            "trade_mode": info.trade_mode,
            "visible": info.visible,
        }

    @staticmethod
    def ensure_visible(symbol: str) -> bool:
        """
        Makes a symbol visible in Market Watch.
        """
        info = mt5.symbol_info(symbol)

        if info is None:
            return False

        if info.visible:
            return True

        return mt5.symbol_select(symbol, True)
