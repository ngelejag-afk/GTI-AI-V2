"""
GTI AI
Risk Manager
Version 2.0
"""


class RiskManager:
    """
    Calculates position sizing based on account risk.
    """

    @staticmethod
    def calculate_lot_size(
        balance: float,
        risk_percent: float,
        entry: float,
        stop_loss: float,
        pip_value: float = 1.0,
        min_lot: float = 0.01,
    ) -> float:
        """
        Calculate lot size from account balance and stop loss distance.
        """

        risk_amount = balance * (risk_percent / 100)

        stop_distance = abs(entry - stop_loss)

        if stop_distance <= 0:
            return min_lot

        lot = risk_amount / (stop_distance * pip_value)

        return max(round(lot, 2), min_lot)
