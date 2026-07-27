
"""
GTI AI
Stop Loss Engine
Version 2.0
"""

from indicators.atr_engine import ATREngine


class StopLossEngine:
    """
    Calculates ATR-based Stop Loss.
    """

    @staticmethod
    def calculate(
        entry: float,
        candles: list,
        trade_type: str,
        multiplier: float = 1.5,
    ) -> float:
        """
        Calculate Stop Loss using ATR.
        """

        atr = ATREngine.calculate(candles)

        if atr == 0:
            return entry

        trade_type = trade_type.upper()

        if trade_type == "BUY":
            return entry - (atr * multiplier)

        if trade_type == "SELL":
            return entry + (atr * multiplier)

        return entry
