"""
GTI AI
MT5 Timeframe Service
Version 1.0
"""

import MetaTrader5 as mt5


class TimeframeService:
    """
    Provides MetaTrader 5 timeframe constants.
    """

    M1 = mt5.TIMEFRAME_M1
    M5 = mt5.TIMEFRAME_M5
    M15 = mt5.TIMEFRAME_M15
    M30 = mt5.TIMEFRAME_M30

    H1 = mt5.TIMEFRAME_H1
    H4 = mt5.TIMEFRAME_H4

    D1 = mt5.TIMEFRAME_D1
    W1 = mt5.TIMEFRAME_W1
    MN1 = mt5.TIMEFRAME_MN1

    @staticmethod
    def all() -> dict:
        """
        Returns all supported timeframes.
        """
        return {
            "M1": TimeframeService.M1,
            "M5": TimeframeService.M5,
            "M15": TimeframeService.M15,
            "M30": TimeframeService.M30,
            "H1": TimeframeService.H1,
            "H4": TimeframeService.H4,
            "D1": TimeframeService.D1,
            "W1": TimeframeService.W1,
            "MN1": TimeframeService.MN1,
        }
