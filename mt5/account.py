7
"""
GTI AI
MT5 Account Service
Version 1.0
"""

import MetaTrader5 as mt5


class MT5Account:
    """
    Reads account information from MetaTrader 5.
    """

    @staticmethod
    def get_info() -> dict | None:
        """
        Returns account information.
        """
        account = mt5.account_info()

        if account is None:
            return None

        return {
            "login": account.login,
            "server": account.server,
            "balance": account.balance,
            "equity": account.equity,
            "margin": account.margin,
            "free_margin": account.margin_free,
            "margin_level": account.margin_level,
            "leverage": account.leverage,
            "currency": account.currency,
            "name": account.name,
        }
