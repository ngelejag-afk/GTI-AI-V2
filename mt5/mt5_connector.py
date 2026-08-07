from __future__ import annotations
"""
GTI AI
MetaTrader 5 Connector
Version 2.0
"""


try:
    import MetaTrader5 as mt5
except ModuleNotFoundError:
    mt5 = None


class MT5Connector:
    """
    Handles connection to MetaTrader 5.
    """

    def connect(self) -> bool:
        """
        Initialize the MT5 terminal connection.
        """

        if mt5 is None:
            print("MT5 package is not installed.")
            return False

        if self.is_connected():
            return True

        if not mt5.initialize():
            print(f"MT5 initialize failed: {mt5.last_error()}")
            return False

        account = mt5.account_info()

        if account is None:
            print("No MT5 account is logged in.")
            return False

        print("=" * 50)
        print(" MT5 CONNECTED")
        print("=" * 50)
        print(f"Login        : {account.login}")
        print(f"Server       : {account.server}")
        print(f"Balance      : {account.balance}")
        print(f"Equity       : {account.equity}")
        print("=" * 50)

        return True

    def disconnect(self) -> None:
        """
        Close the MT5 terminal connection.
        """

        if mt5 is not None:
            mt5.shutdown()

    def is_connected(self) -> bool:
        """
        Check whether the MT5 terminal is available.
        """

        if mt5 is None:
            return False

        return mt5.terminal_info() is not None

    def ensure_symbol(self, symbol: str = "XAUUSD") -> bool:
        """
        Ensure the requested symbol is available.
        """

        if mt5 is None:
            return False

        symbol_info = mt5.symbol_info(symbol)

        if symbol_info is None:
            print(f"Symbol not found: {symbol}")
            return False

        if symbol_info.visible:
            return True

        if not mt5.symbol_select(symbol, True):
            print(f"Unable to enable symbol: {symbol}")
            return False

        return True

    def account_info(self):
        """
        Return current MT5 account information.
        """

        if mt5 is None:
            return None

        return mt5.account_info()

    def terminal_info(self):
        """
        Return current terminal information.
        """

        if mt5 is None:
            return None

        return mt5.terminal_info()

    def last_error(self):
        """
        Return the latest MT5 error.
        """

        if mt5 is None:
            return None

        return mt5.last_error()
