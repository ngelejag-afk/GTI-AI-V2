"""
GTI AI
Paper Trading Engine
Version 1.0
"""

from __future__ import annotations


class PaperTradingEngine:
    """
    Simulates trade outcomes without sending
    real orders to a broker.
    """

    @staticmethod
    def update(order: dict, current_price: float) -> dict:
        """
        Update a paper trade based on the latest market price.
        """

        decision = order["decision"]

        entry = order["entry"]
        stop_loss = order["stop_loss"]
        take_profit = order["take_profit"]

        status = "OPEN"

        if decision == "BUY":
            if current_price >= take_profit:
                status = "WIN"
            elif current_price <= stop_loss:
                status = "LOSS"

        elif decision == "SELL":
            if current_price <= take_profit:
                status = "WIN"
            elif current_price >= stop_loss:
                status = "LOSS"

        return {
            **order,
            "current_price": current_price,
            "status": status,
        }
