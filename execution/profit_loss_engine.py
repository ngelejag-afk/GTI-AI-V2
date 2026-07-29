"""
GTI AI
Profit Loss Engine
Version 1.0
"""


class ProfitLossEngine:
    """
    Calculates floating profit/loss for paper trades.
    """

    XAUUSD_POINT_VALUE = 100.0

    @classmethod
    def calculate(
        cls,
        decision: str,
        entry: float,
        current_price: float,
        lot_size: float,
    ) -> dict:
        """
        Calculate floating profit/loss.
        """

        decision = decision.upper()

        if decision == "BUY":
            price_difference = current_price - entry
        elif decision == "SELL":
            price_difference = entry - current_price
        else:
            price_difference = 0.0

        profit = round(
            price_difference * cls.XAUUSD_POINT_VALUE * lot_size,
            2,
        )

        pips = round(price_difference * 100, 1)

        if profit > 0:
            status = "PROFIT"
        elif profit < 0:
            status = "LOSS"
        else:
            status = "BREAKEVEN"

        return {
            "profit": profit,
            "pips": pips,
            "status": status,
            "price_difference": round(price_difference, 5),
        }
