"""
GTI AI
Risk Manager
Version 2.0
"""

from __future__ import annotations

from execution.statistics_engine import StatisticsEngine


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
        daily_loss_percent: float | None = None,
        consecutive_losses: int | None = None,
    ) -> dict:
        """
        Validate whether new trades are allowed.
        """

        stats = StatisticsEngine.summary()

        if consecutive_losses is None:
            consecutive_losses = stats["consecutive_losses"]

        if daily_loss_percent is None:
            gross_profit = stats["gross_profit"]
            gross_loss = stats["gross_loss"]

            if gross_profit == 0:
                daily_loss_percent = gross_loss
            else:
                daily_loss_percent = (
                    gross_loss / gross_profit
                ) * 100

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
            "statistics": stats,
        }
