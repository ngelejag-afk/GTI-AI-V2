"""
GTI AI
MT5 Account Information
Version 2.0
"""

from __future__ import annotations

from account.account_engine import AccountEngine

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None


class AccountInfo:
    """
    Provides account information from MT5 when available,
    otherwise from the simulated AccountEngine.
    """

    @staticmethod
    def connected() -> bool:
        """
        Check whether MT5 is available and initialized.
        """

        return mt5 is not None and mt5.initialize()

    @staticmethod
    def get() -> dict:
        """
        Return account information.
        """

        if mt5 is not None and mt5.initialize():
            info = mt5.account_info()

            if info is not None:
                return {
                    "connected": True,
                    "balance": float(info.balance),
                    "equity": float(info.equity),
                    "free_margin": float(info.margin_free),
                    "margin": float(info.margin),
                    "currency": info.currency,
                    "leverage": int(info.leverage),
                }

        simulated = AccountEngine.summary()

        return {
            "connected": False,
            "balance": simulated["balance"],
            "equity": simulated["equity"],
            "free_margin": simulated["equity"],
            "margin": 0.0,
            "currency": "USD",
            "leverage": 100,
        }
