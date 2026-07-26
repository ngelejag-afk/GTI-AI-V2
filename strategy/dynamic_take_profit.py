"""
GTI AI
Dynamic Take Profit Engine
Version 1.0
"""

from indicators.atr_engine import ATREngine


class DynamicTakeProfit:
    """
    Calculates dynamic take profit levels using ATR.
    """

    TP1_MULTIPLIER = 2.0
    TP2_MULTIPLIER = 3.0
    TP3_MULTIPLIER = 4.0

    @staticmethod
    def calculate(
        decision: str,
        entry: float,
        candles: list,
    ) -> dict:
        """
        Returns dynamic TP1, TP2 and TP3.
        """
        atr = ATREngine.calculate(candles)

        if atr == 0:
            return {
                "tp1": 0.0,
                "tp2": 0.0,
                "tp3": 0.0,
            }

        if decision == "BUY":
            return {
                "tp1": round(entry + (atr * DynamicTakeProfit.TP1_MULTIPLIER), 2),
                "tp2": round(entry + (atr * DynamicTakeProfit.TP2_MULTIPLIER), 2),
                "tp3": round(entry + (atr * DynamicTakeProfit.TP3_MULTIPLIER), 2),
            }

        if decision == "SELL":
            return {
                "tp1": round(entry - (atr * DynamicTakeProfit.TP1_MULTIPLIER), 2),
                "tp2": round(entry - (atr * DynamicTakeProfit.TP2_MULTIPLIER), 2),
                "tp3": round(entry - (atr * DynamicTakeProfit.TP3_MULTIPLIER), 2),
            }

        return {
            "tp1": 0.0,
            "tp2": 0.0,
            "tp3": 0.0,
        }
