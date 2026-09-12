from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


API_URL = "https://api.twelvedata.com/time_series"
QUOTE_URL = "https://api.twelvedata.com/quote"
SYMBOL = "XAU/USD"

INTERVALS = {
    "M1": "1min",
    "M5": "5min",
    "M15": "15min",
    "H1": "1h",
    "H4": "4h",
}


class TwelveDataXAU:
    _LAST_REQUEST = 0.0
    _MIN_REQUEST_INTERVAL = 4.0
    """
    Read-only XAU/USD market-data adapter.

    No trading.
    No MT5 dependency.
    No order execution.
    """

    @staticmethod
    def api_key() -> str:
        value = os.getenv("TWELVE_DATA_API_KEY", "").strip()
        if value:
            return value

        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("TWELVE_DATA_API_KEY="):
                    return line.split("=", 1)[1].strip()

        return ""

    @classmethod
    def _request_json(cls, url: str, params: dict) -> dict:
        api_key = cls.api_key()

        if not api_key:
            raise RuntimeError("TWELVE_DATA_API_KEY_NOT_CONFIGURED")

        query = urllib.parse.urlencode(params)

        request = urllib.request.Request(
            f"{url}?{query}",
            headers={
                "Accept": "application/json",
                "User-Agent": "GTI-AI-V2/1.0",
            },
            method="GET",
        )

        elapsed = time.monotonic() - cls._LAST_REQUEST
        if elapsed < cls._MIN_REQUEST_INTERVAL:
            time.sleep(cls._MIN_REQUEST_INTERVAL - elapsed)

        cls._LAST_REQUEST = time.monotonic()

        last_error = None

        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code not in (429, 502, 503, 504) or attempt == 2:
                    raise
                time.sleep(2 ** attempt)
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        else:
            raise last_error

        if not isinstance(payload, dict):
            raise RuntimeError("INVALID_TWELVE_DATA_RESPONSE")

        if payload.get("status") == "error":
            message = payload.get("message", "UNKNOWN_TWELVE_DATA_ERROR")
            raise RuntimeError(f"TWELVE_DATA_ERROR:{message}")

        return payload

    @classmethod
    def get_candles(cls, timeframe: str, count: int = 200) -> list[dict]:
        timeframe = timeframe.upper()
        interval = INTERVALS.get(timeframe)

        if not interval:
            raise ValueError(f"UNSUPPORTED_TIMEFRAME:{timeframe}")

        payload = cls._request_json(
            API_URL,
            {
                "symbol": SYMBOL,
                "interval": interval,
                "outputsize": min(max(int(count) + 5, 1), 5000),
                "apikey": cls.api_key(),
                "format": "JSON",
                "timezone": "UTC",
            },
        )

        values = payload.get("values")

        if not isinstance(values, list) or not values:
            raise RuntimeError("NO_XAUUSD_CANDLES")

        candles = []

        for row in reversed(values):
            try:
                candles.append(
                    {
                        "time": row["datetime"],
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue

        if not candles:
            raise RuntimeError("INVALID_XAUUSD_CANDLES")

        # Only return candles whose full interval has closed.
        interval_seconds = {
            "1min": 60,
            "5min": 300,
            "15min": 900,
            "1h": 3600,
            "4h": 14400,
        }[interval]

        now_utc = int(time.time())
        closed = []

        for candle in candles:
            try:
                dt = datetime.strptime(
                    candle["time"],
                    "%Y-%m-%d %H:%M:%S",
                ).replace(tzinfo=timezone.utc)

                candle_start = int(dt.timestamp())
            except (TypeError, ValueError):
                continue

            if candle_start + interval_seconds <= now_utc:
                closed.append(candle)

        if len(closed) < int(count):
            raise RuntimeError(
                f"INSUFFICIENT_CLOSED_XAUUSD_CANDLES:{len(closed)}"
            )

        return closed[-int(count):]

    @classmethod
    def get_quote(cls) -> dict:
        payload = cls._request_json(
            QUOTE_URL,
            {
                "symbol": SYMBOL,
                "apikey": cls.api_key(),
            },
        )

        try:
            last_quote_at = int(payload["last_quote_at"])
            price = float(payload["close"])
        except (KeyError, TypeError, ValueError):
            raise RuntimeError("INVALID_XAUUSD_QUOTE")

        now_utc = int(time.time())
        age_seconds = now_utc - last_quote_at

        if age_seconds < 0:
            raise RuntimeError("QUOTE_TIMESTAMP_IN_FUTURE")

        return {
            "symbol": payload.get("symbol", SYMBOL),
            "price": price,
            "last_quote_at": last_quote_at,
            "last_quote_utc": datetime.fromtimestamp(
                last_quote_at, timezone.utc
            ).isoformat(),
            "age_seconds": age_seconds,
            "market_open": bool(payload.get("is_market_open", False)),
        }

    @classmethod
    def get_market(cls, count: int = 200) -> dict:
        return {
            timeframe: cls.get_candles(timeframe, count)
            for timeframe in ("H4", "H1", "M15", "M5", "M1")
        }


if __name__ == "__main__":
    print("GTI-AI-V2 XAU/USD DATA ADAPTER")
    print("Mode: READ-ONLY")
    print("Trading: DISABLED")
    print("Provider: Twelve Data")
    print("Symbol: XAU/USD")

    if not TwelveDataXAU.api_key():
        print("STATUS: API KEY NOT CONFIGURED")
        raise SystemExit(0)

    try:
        quote = TwelveDataXAU.get_quote()

        print("STATUS: QUOTE RECEIVED")
        print(f"Price: {quote['price']}")
        print(f"Market Open: {quote['market_open']}")
        print(f"Last Quote UTC: {quote['last_quote_utc']}")
        print(f"Quote Age: {quote['age_seconds']} seconds")

        market = TwelveDataXAU.get_market(count=5)

        print("STATUS: DATA RECEIVED")

        for timeframe, candles in market.items():
            print(f"{timeframe}: {len(candles)} candles")

    except Exception as exc:
        print("STATUS: DATA ERROR")
        print(f"ERROR: {type(exc).__name__}: {exc}")
