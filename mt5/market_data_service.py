"""
GTI AI
Market Data Service
Version 3.0
"""

from __future__ import annotations

from account.account_info import AccountInfo
from indicators.atr_engine import ATREngine
from mt5.multi_timeframe_reader import MultiTimeframeReader
from mt5.symbol_service import SymbolService


class MarketDataService:
    """
    Provides a centralized market snapshot for
    simulation, paper trading and live trading.
    """

    DEFAULT_TIMEFRAME = "M15"

    @staticmethod
    def get_market_data(
        symbol: str = "XAUUSD",
        bars: int = 500,
    ) -> dict:
        """
        Return market candles, prices, ATR and account data.

        Backward compatible with previous versions.
        """

        timeframes = MultiTimeframeReader.read(
            symbol=symbol,
            bars=bars,
        )

        close_prices: dict[str, list[float]] = {}

        latest_price: float | None = None

        for timeframe, candles in timeframes.items():
            closes: list[float] = []

            for candle in candles:
                try:
                    closes.append(float(candle["close"]))
                except (KeyError, TypeError, IndexError):
                    continue

            close_prices[timeframe] = closes

            if (
                timeframe == MarketDataService.DEFAULT_TIMEFRAME
                and closes
            ):
                latest_price = closes[-1]

        if latest_price is None:
            for closes in close_prices.values():
                if closes:
                    latest_price = closes[-1]
                    break

        default_candles = timeframes.get(
            MarketDataService.DEFAULT_TIMEFRAME,
            [],
        )

        atr = ATREngine.calculate(default_candles)

        symbol_info = SymbolService.get(symbol)

        if symbol_info:
            bid = float(symbol_info["bid"])
            ask = float(symbol_info["ask"])
            spread = int(symbol_info["spread"])
        else:
            bid = latest_price or 0.0
            ask = latest_price or 0.0
            spread = 0

        account = AccountInfo.get()

        return {
            "symbol": symbol,
            "timeframes": timeframes,
            "close_prices": close_prices,
            "latest_price": latest_price,
            "bid": bid,
            "ask": ask,
            "spread": spread,
            "atr": atr,
            "account_balance": account["balance"],
            "account": account,
        }
