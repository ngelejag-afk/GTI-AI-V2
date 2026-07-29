
"""
GTI AI
Lot Size Engine
Version 1.0
"""

from __future__ import annotations


class LotSizeEngine:
    """
    Calculates position size based on account balance
    and selected risk percentage.
    """

    @staticmethod
    def calculate(
        balance: float,
        risk_percent: float,
        stop_loss_pips: float,
        pip_value: float = 1.0,
        min_lot: float = 0.01,
        max_lot: float = 100.0,
    ) -> float:
        """
        Calculate recommended lot size.

        Returns:
            float: Recommended lot size.
        """

        if balance <= 0:
            return min_lot

        if risk_percent <= 0:
            return min_lot

        if stop_loss_pips <= 0:
            return min_lot

        risk_amount = balance * (risk_percent / 100)

        lot_size = risk_amount / (stop_loss_pips * pip_value)

        lot_size = max(min_lot, lot_size)
        lot_size = min(max_lot, lot_size)

        return round(lot_size, 2)
