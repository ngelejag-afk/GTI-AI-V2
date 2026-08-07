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
    def get_market_data(
        cls,
        symbol: str = "XAUUSD",
        timeframe: str = "M15",
        count: int = 100,
    ) -> dict:
        """
        Fetch market data or return mock structure for simulation scanner.
        """
        mock_series = [2400.0 + (i * 0.1) for i in range(count)]

        return {
            "symbol": symbol,
            "status": "active",
            "timeframes": {
                "M1": mock_series,
                "M5": mock_series,
                "M15": mock_series,
                "H1": mock_series,
                "H4": mock_series,
                "D1": mock_series,
            },
            "close_prices": {
                "M1": mock_series,
                "M5": mock_series,
                "M15": mock_series,
                "H1": mock_series,
                "H4": mock_series,
                "D1": mock_series,
            },
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
