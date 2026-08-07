from __future__ import annotations
"""
GTI AI
Account Engine
Version 1.0
"""



class AccountEngine:
    """
    Manages the simulated trading account.
    """

    _starting_balance = 1000.0
    _balance = 1000.0
    _equity = 1000.0
    _floating_profit = 0.0
    _closed_profit = 0.0

    @classmethod
    def reset(cls) -> None:
        """
        Reset the paper trading account.
        """

        cls._balance = cls._starting_balance
        cls._equity = cls._starting_balance
        cls._floating_profit = 0.0
        cls._closed_profit = 0.0

    @classmethod
    def balance(cls) -> float:
        return round(cls._balance, 2)

    @classmethod
    def equity(cls) -> float:
        return round(cls._equity, 2)

    @classmethod
    def floating_profit(cls) -> float:
        return round(cls._floating_profit, 2)

    @classmethod
    def closed_profit(cls) -> float:
        return round(cls._closed_profit, 2)

    @classmethod
    def apply_profit(cls, amount: float) -> None:
        """
        Apply a closed trade profit or loss.
        """

        cls._closed_profit += amount
        cls._balance += amount
        cls._equity = cls._balance

    @classmethod
    def update_floating_profit(cls, amount: float) -> None:
        """
        Update floating profit/loss.
        """

        cls._floating_profit = amount
        cls._equity = cls._balance + amount

    @classmethod
    def summary(cls) -> dict:
        """
        Return account information.
        """

        return {
            "starting_balance": round(cls._starting_balance, 2),
            "balance": round(cls._balance, 2),
            "equity": round(cls._equity, 2),
            "floating_profit": round(cls._floating_profit, 2),
            "closed_profit": round(cls._closed_profit, 2),
        }
