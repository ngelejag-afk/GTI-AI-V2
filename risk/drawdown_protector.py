"""
GTI AI
Drawdown Protector
Version 1.0
"""

from __future__ import annotations


class DrawdownProtector:
    """
    Protects the trading account from excessive drawdown.
    """

    DEFAULT_MAX_DRAWDOWN = 10.0

    @classmethod
    def calculate_drawdown(
        cls,
        starting_balance: float,
        current_balance: float,
    ) -> float:
        """
        Calculate drawdown percentage.
        """

        if starting_balance <= 0:
            return 0.0

        drawdown = (
            (starting_balance - current_balance)
            / starting_balance
        ) * 100

        return round(max(drawdown, 0.0), 2)

    @classmethod
    def is_allowed(
        cls,
        starting_balance: float,
        current_balance: float,
        max_drawdown: float | None = None,
    ) -> bool:
        """
        Check whether trading should continue.
        """

        if max_drawdown is None:
            max_drawdown = cls.DEFAULT_MAX_DRAWDOWN

        drawdown = cls.calculate_drawdown(
            starting_balance,
            current_balance,
        )

        return drawdown < max_drawdown

    @classmethod
    def status(
        cls,
        starting_balance: float,
        current_balance: float,
        max_drawdown: float | None = None,
    ) -> dict:
        """
        Return drawdown protection status.
        """

        if max_drawdown is None:
            max_drawdown = cls.DEFAULT_MAX_DRAWDOWN

        drawdown = cls.calculate_drawdown(
            starting_balance,
            current_balance,
        )

        allowed = drawdown < max_drawdown

        return {
            "starting_balance": starting_balance,
            "current_balance": current_balance,
            "drawdown": drawdown,
            "max_drawdown": max_drawdown,
            "trading_allowed": allowed,
        }
