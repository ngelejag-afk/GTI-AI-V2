"""
GTI AI
MetaTrader 5 Connector
Version 1.0
"""

from __future__ import annotations

import MetaTrader5 as mt5


class MT5Connector:
    """
    Handles connection to MetaTrader 5.
    """

    def connect(self) -> bool:
        """
        Initialize the MT5 terminal connection.
        """
        return mt5.initialize()

    def disconnect(self) -> None:
        """
        Close the MT5 terminal connection.
        """
        mt5.shutdown()

    def is_connected(self) -> bool:
        """
        Check whether the MT5 terminal is available.
        """
        return mt5.terminal_info() is not None
