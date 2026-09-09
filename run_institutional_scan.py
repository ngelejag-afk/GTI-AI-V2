from __future__ import annotations

import json
import os

from mt5.candle_reader import CandleReader
from mt5.live_price import LivePriceService
from strategy.institutional_entry_engine import InstitutionalEntryEngine


SYMBOL = os.getenv("GTI_SYMBOL", "XAUUSD").strip() or "XAUUSD"
DXY_SIGNAL = os.getenv("GTI_DXY_SIGNAL", "NEUTRAL").strip().upper()
NEWS_SAFE = os.getenv("GTI_NEWS_SAFE", "0").strip() == "1"

TIMEFRAMES = ("H4", "H1", "M15", "M5", "M1")


def main() -> None:
    market = {}

    for timeframe in TIMEFRAMES:
        market[timeframe] = CandleReader.read(
            SYMBOL,
            timeframe,
            200,
        )

    price = LivePriceService.get_price(SYMBOL)

    if not price:
        print(
            json.dumps(
                {
                    "status": "NO TRADE",
                    "reason": "MT5_BRIDGE_DATA_MISSING",
                    "symbol": SYMBOL,
                    "message": (
                        "GTI-AI-V2 is waiting for the read-only MT5 Bridge. "
                        "No trade execution is possible."
                    ),
                },
                indent=2,
            )
        )
        return

    if not isinstance(price, dict):
        print(
            json.dumps(
                {
                    "status": "NO TRADE",
                    "reason": "INVALID_LIVE_PRICE",
                    "symbol": SYMBOL,
                },
                indent=2,
            )
        )
        return

    if "bid" not in price or "ask" not in price:
        print(
            json.dumps(
                {
                    "status": "NO TRADE",
                    "reason": "INVALID_LIVE_PRICE",
                    "symbol": SYMBOL,
                    "message": "Bridge response does not contain bid and ask.",
                },
                indent=2,
            )
        )
        return

    try:
        bid = float(price["bid"])
        ask = float(price["ask"])
    except (TypeError, ValueError):
        print(
            json.dumps(
                {
                    "status": "NO TRADE",
                    "reason": "INVALID_LIVE_PRICE",
                    "symbol": SYMBOL,
                },
                indent=2,
            )
        )
        return

    if bid <= 0 or ask <= 0 or ask < bid:
        print(
            json.dumps(
                {
                    "status": "NO TRADE",
                    "reason": "INVALID_LIVE_PRICE",
                    "symbol": SYMBOL,
                    "bid": bid,
                    "ask": ask,
                },
                indent=2,
            )
        )
        return

    result = InstitutionalEntryEngine.scan(
        market,
        bid=bid,
        ask=ask,
        dxy_signal=DXY_SIGNAL,
        news_safe=NEWS_SAFE,
    )

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
