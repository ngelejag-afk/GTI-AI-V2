"""
GTI AI
Risk Manager
Version 1.0
"""

from __future__ import annotations


class RiskManager:
    """
    Global trade risk validation.
    """

    MAX_OPEN_TRADES = 3
    MAX_DAILY_LOSS = 5.0
    MAX_CONSECUTIVE_LOSSES = 3

    @staticmethod
    def validate(
        open_trades: int,
        daily_loss_percent: float,
        consecutive_losses: int,
    ) -> dict:
        """
        Validate whether new trades are allowed.
        """

        if open_trades >= RiskManager.MAX_OPEN_TRADES:
            return {
                "valid": False,
                "reason": "Maximum open trades reached.",
            }

        if daily_loss_percent >= RiskManager.MAX_DAILY_LOSS:
            return {
                "valid": False,
                "reason": "Maximum daily loss reached.",
            }

        if (
            consecutive_losses
            >= RiskManager.MAX_CONSECUTIVE_LOSSES
        ):
            return {
                "valid": False,
                "reason": "Maximum consecutive losses reached.",
            }

        return {
            "valid": True,
            "reason": "Risk validation passed.",
        }
