"""
GTI AI
MetaTrader 5 Connector
Version 1.1
"""

from __future__ import annotations

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
            return False

        return mt5.initialize()

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
