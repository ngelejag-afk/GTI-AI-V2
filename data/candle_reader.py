"""
GTI AI
MT5 Candle Reader
Version 1.0
"""

from __future__ import annotations

from typing import List

import MetaTrader5 as mt5


class CandleReader:
    """
    Reads candle data from MetaTrader 5.
    """

    def get_rates(self, symbol: str, timeframe: int, count: int = 100) -> List:
        """
        Return the latest candles.
        """
        rates = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            0,
            count,
        )

        if rates is None:
            return []

        return list(rates)
