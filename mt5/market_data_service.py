"""
GTI AI
Market Data Service
"""

from __future__ import annotations

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from account.account_info import AccountInfo


class MarketDataService:
    """
    Service for fetching market data and price information.
    """

    def __init__(self) -> None:
        self.account_info = AccountInfo()

    def get_current_price(self, symbol: str) -> float:
        """
        Return mock/live price for a given symbol.
        """
        # Mock price standard kwa ajili ya simulation/cloud deployment
        prices = {
            "XAUUSD": 2400.00,
            "EURUSD": 1.0850,
            "GBPUSD": 1.2800,
        }
        return prices.get(symbol, 100.0)
