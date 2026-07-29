"""
GTI AI
Account Risk Manager
Version 1.0
"""

from __future__ import annotations

from risk.lot_size_engine import LotSizeEngine


class AccountRiskManager:
    """
    Manages account risk and prepares risk settings
    for trade execution.
    """

    DEFAULT_RISK_PERCENT = 1.0

    @classmethod
    def calculate_position(
        cls,
        balance: float,
        stop_loss_pips: float,
        risk_percent: float | None = None,
    ) -> dict:
        """
        Calculate position sizing information.
        """

        if risk_percent is None:
            risk_percent = cls.DEFAULT_RISK_PERCENT

        risk_amount = round(
            balance * (risk_percent / 100),
            2,
        )

        lot_size = LotSizeEngine.calculate(
            balance=balance,
            risk_percent=risk_percent,
            stop_loss_pips=stop_loss_pips,
        )

        return {
            "balance": balance,
            "risk_percent": risk_percent,
            "risk_amount": risk_amount,
            "stop_loss_pips": stop_loss_pips,
            "lot_size": lot_size,
        }

    @classmethod
    def is_trade_allowed(
        cls,
        balance: float,
        minimum_balance: float = 50.0,
    ) -> bool:
        """
        Verify whether trading is allowed.
        """

        return balance >= minimum_balance
