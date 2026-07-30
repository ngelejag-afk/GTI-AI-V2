"""
GTI AI
Stop Loss Engine
Version 1.0
"""

from __future__ import annotations


class StopLossEngine:
    """
    Calculates a dynamic stop loss using ATR.
    """

    @staticmethod
    def calculate(
        signal: str,
        entry_price: float,
        atr: float,
        multiplier: float = 1.5,
    ) -> dict:
        """
        Calculate the stop loss level.
        """

        signal = signal.upper()

        if (
            signal not in ("BUY", "SELL")
            or entry_price <= 0
            or atr <= 0
        ):
            return {
                "stop_loss": None,
                "risk_distance": None,
                "valid": False,
            }

        risk_distance = atr * multiplier

        if signal == "BUY":
            stop_loss = entry_price - risk_distance
        else:
            stop_loss = entry_price + risk_distance

        return {
            "stop_loss": round(stop_loss, 2),
            "risk_distance": round(risk_distance, 2),
            "valid": True,
        }
