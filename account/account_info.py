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

