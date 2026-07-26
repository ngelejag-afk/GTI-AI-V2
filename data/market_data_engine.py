"""
GTI AI
Market Data Engine
Version 1.0
"""

from models.market_data import MarketData


class MarketDataEngine:
    """
    Base engine for receiving market data.

    MT5 connection and live candle retrieval
    will be added in the next version.
    """

    def __init__(self):
        self.latest_candle: MarketData | None = None

    def update(self, candle: MarketData) -> None:
        """
        Store the latest market candle.
        """
        self.latest_candle = candle

    def get_latest(self) -> MarketData | None:
        """
        Return the latest market candle.
        """
        return self.latest_candle
