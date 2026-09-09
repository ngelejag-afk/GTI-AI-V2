from __future__ import annotations

from mt5.bridge_client import BridgeMarketData


class LivePriceService:
    """
    Live price reader for GTI-AI-V2.

    Read-only.
    No order execution.
    """

    @classmethod
    def get_price(cls, symbol: str = "XAUUSD"):
        return BridgeMarketData.price(symbol)
