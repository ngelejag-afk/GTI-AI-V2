class AccountInfo:
    def __init__(self, *args, **kwargs):
        self.balance = 10000.0
        self.equity = 10000.0
        self.margin = 0.0
        self.free_margin = 10000.0

    def __getitem__(self, item):
        return getattr(self, item, None)

    def get_account_info(self, *args, **kwargs):
        return {
            "balance": self.balance,
            "equity": self.equity,
            "free_margin": self.free_margin,
            "margin": self.margin
        }

    @classmethod
    def get(cls, *args, **kwargs):
        return cls()
"""
GTI AI
Account Info Module
"""

from __future__ import annotations
from account.account_engine import AccountEngine


class AccountInfo:
    """
    Wrapper interface for AccountEngine to provide account details.
    """

    def __init__(self) -> None:
        pass

    @property
    def balance(self) -> float:
        return AccountEngine.balance()

    @property
    def equity(self) -> float:
        return AccountEngine.equity()

    @classmethod
    def get_summary(cls) -> dict:
        return AccountEngine.summary()

