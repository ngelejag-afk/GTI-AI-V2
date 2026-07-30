"""
GTI AI
Entry Price Engine
Version 1.0
"""

from __future__ import annotations


class EntryPriceEngine:
    """
    Determines the trade entry price.
    """

    @staticmethod
    def calculate(
        signal: str,
        bid: float,
        ask: float,
    ) -> dict:
        """
        Calculate the recommended entry price.
        """

        signal = signal.upper()

        if signal == "BUY":
            return {
                "entry": ask,
                "order_type": "MARKET_BUY",
                "valid": True,
            }

        if signal == "SELL":
            return {
                "entry": bid,
                "order_type": "MARKET_SELL",
                "valid": True,
            }

        return {
            "entry": None,
            "order_type": "NONE",
            "valid": False,
        }
