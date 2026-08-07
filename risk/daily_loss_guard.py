from __future__ import annotations
"""
GTI AI
Daily Loss Guard
Version 1.0
"""



class DailyLossGuard:
    """
    Stops trading after reaching the daily loss limit.
    """

    DEFAULT_MAX_DAILY_LOSS = 5.0

    _starting_balance = 0.0
    _current_balance = 0.0

    @classmethod
    def start_day(cls, balance: float) -> None:
        """
        Initialize a new trading day.
        """

        cls._starting_balance = balance
        cls._current_balance = balance

    @classmethod
    def update_balance(cls, balance: float) -> None:
        """
        Update the current account balance.
        """

        cls._current_balance = balance

    @classmethod
    def daily_loss_percent(cls) -> float:
        """
        Calculate today's loss percentage.
        """

        if cls._starting_balance <= 0:
            return 0.0

        loss = (
            (cls._starting_balance - cls._current_balance)
            / cls._starting_balance
        ) * 100

        return round(max(loss, 0.0), 2)

    @classmethod
    def trading_allowed(
        cls,
        max_daily_loss: float | None = None,
    ) -> bool:
        """
        Check whether trading is still allowed.
        """

        if max_daily_loss is None:
            max_daily_loss = cls.DEFAULT_MAX_DAILY_LOSS

        return cls.daily_loss_percent() < max_daily_loss

    @classmethod
    def status(cls) -> dict:
        """
        Return daily risk status.
        """

        return {
            "starting_balance": cls._starting_balance,
            "current_balance": cls._current_balance,
            "daily_loss": cls.daily_loss_percent(),
            "trading_allowed": cls.trading_allowed(),
        }

    @classmethod
    def reset(cls) -> None:
        """
        Reset daily tracking.
        """

        cls._starting_balance = 0.0
        cls._current_balance = 0.0
