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

    @classmethod
    def get_market_data(cls, symbol: str = "XAUUSD", timeframe: str = "M15", count: int = 100) -> dict:
        """
        Fetch market data or return mock structure for simulation scanner.
        """
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "prices": [2400.0 + (i * 0.1) for i in range(count)],
            "status": "active",
        }

    def get_current_price(self, symbol: str) -> float:
        """
        Return current price for a given symbol.
        """
        prices = {
            "XAUUSD": 2400.00,
            "EURUSD": 1.0850,
            "GBPUSD": 1.2800,
        }
        return prices.get(symbol, 100.0)
