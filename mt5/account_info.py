"""
GTI AI
MT5 Account Information
Version 1.0
"""

from __future__ import annotations

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None


class AccountInfo:
    """
    Provides MetaTrader 5 account information.
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

        if mt5 is None:
            return {
                "connected": False,
                "balance": 0.0,
                "equity": 0.0,
                "free_margin": 0.0,
                "margin": 0.0,
                "currency": "",
                "leverage": 0,
            }

        info = mt5.account_info()

        if info is None:
            return {
                "connected": False,
                "balance": 0.0,
                "equity": 0.0,
                "free_margin": 0.0,
                "margin": 0.0,
                "currency": "",
                "leverage": 0,
            }

        return {
            "connected": True,
            "balance": float(info.balance),
            "equity": float(info.equity),
            "free_margin": float(info.margin_free),
            "margin": float(info.margin),
            "currency": info.currency,
            "leverage": int(info.leverage),
        }
