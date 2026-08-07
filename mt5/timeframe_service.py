from __future__ import annotations
"""
GTI AI
Timeframe Service
Version 1.0
"""


try:
    import MetaTrader5 as mt5
except ModuleNotFoundError:
    mt5 = None


class TimeframeService:
    """
    Provides MT5 timeframe constants.
    """

    M1 = mt5.TIMEFRAME_M1 if mt5 else 1
    M5 = mt5.TIMEFRAME_M5 if mt5 else 5
    M15 = mt5.TIMEFRAME_M15 if mt5 else 15
    M30 = mt5.TIMEFRAME_M30 if mt5 else 30
    H1 = mt5.TIMEFRAME_H1 if mt5 else 60
    H4 = mt5.TIMEFRAME_H4 if mt5 else 240
    D1 = mt5.TIMEFRAME_D1 if mt5 else 1440
    W1 = mt5.TIMEFRAME_W1 if mt5 else 10080
    MN1 = mt5.TIMEFRAME_MN1 if mt5 else 43200
