"""
GTI AI
Take Profit Engine
Version 2.0
"""

from indicators.atr_engine import ATREngine


class TakeProfitEngine:
    """
    Calculates ATR-based Take Profit levels.
    """

    @staticmethod
    def calculate(
        entry: float,
        candles: list,
        trade_type: str,
    ) -> dict:
        """
        Calculate ATR-based TP levels.
        """

        atr = ATREngine.calculate(candles)

        if atr == 0:
            return {
                "tp1": entry,
                "tp2": entry,
                "tp3": entry,
            }

        trade_type = trade_type.upper()

        if trade_type == "BUY":
            return {
                "tp1": entry + (atr * 2),
                "tp2": entry + (atr * 3),
                "tp3": entry + (atr * 5),
            }

        if trade_type == "SELL":
            return {
                "tp1": entry - (atr * 2),
                "tp2": entry - (atr * 3),
                "tp3": entry - (atr * 5),
            }

        return {
            "tp1": entry,
            "tp2": entry,
            "tp3": entry,
        }
