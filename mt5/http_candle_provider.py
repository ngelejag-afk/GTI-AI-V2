from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import requests


API_URL = "https://api.twelvedata.com/time_series"
TIMEOUT = 15

SYMBOL_MAP = {
    "XAUUSD": "XAU/USD",
    "BTCUSD": "BTC/USD",
}

INTERVAL_MAP = {
    "M1": "1min",
    "M5": "5min",
    "M15": "15min",
}

SECONDS = {
    "M1": 60,
    "M5": 300,
    "M15": 900,
    "H1": 3600,
    "H4": 14400,
}

DERIVED_FROM_M15 = {
    "H1": 4,
    "H4": 16,
}

M15_HISTORY_FOR_DERIVED = 1700

CACHE_TTL = {
    "M1": 60,
    "M5": 300,
    "M15": 900,
    "H1": 3600,
    "H4": 14400,
}

RATE_LIMIT_PER_MINUTE = 7
QUOTA_LOCK_SECONDS = 70

CACHE_DIR = Path.home() / ".cache" / "gti_ai_v2"
QUOTA_LOCK = CACHE_DIR / "twelve_data_quota.lock"


@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


class HttpCandleProvider:
    _CANDLE_CACHE: Dict[str, tuple] = {}
    _REQUEST_LOG: List[float] = []

    @classmethod
    def _api_key(cls) -> str:
        key = os.getenv("TWELVE_DATA_API_KEY") or os.getenv("TWELVE_DATA_KEY")
        if not key:
            raise RuntimeError(
                "TWELVE_DATA_API_KEY is not configured. "
                "Live trading data is disabled."
            )
        return key

    @classmethod
    def _cache_key(cls, symbol: str, timeframe: str, count: int) -> str:
        return f"{symbol.upper()}:{timeframe.upper()}:{count}"

    @classmethod
    def _check_quota_lock(cls) -> None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        if QUOTA_LOCK.exists():
            age = time.time() - QUOTA_LOCK.stat().st_mtime
            if age < QUOTA_LOCK_SECONDS:
                remaining = int(QUOTA_LOCK_SECONDS - age)
                raise RuntimeError(
                    f"Twelve Data quota lock active ({remaining}s remaining)."
                )
            try:
                QUOTA_LOCK.unlink()
            except FileNotFoundError:
                pass

    @classmethod
    def _allow_request(cls) -> None:
        now = time.time()

        cls._REQUEST_LOG = [
            t for t in cls._REQUEST_LOG
            if now - t < 60
        ]

        if len(cls._REQUEST_LOG) >= RATE_LIMIT_PER_MINUTE:
            raise RuntimeError(
                "Local Twelve Data rate limiter blocked request. "
                "Failing closed."
            )

        cls._REQUEST_LOG.append(now)

    @staticmethod
    def _symbol(symbol: str) -> str:
        symbol = symbol.upper().replace("/", "")

        if symbol not in SYMBOL_MAP:
            raise ValueError(
                f"Unsupported live symbol: {symbol}. "
                f"Allowed: {', '.join(SYMBOL_MAP)}"
            )

        return SYMBOL_MAP[symbol]

    @staticmethod
    def _parse_timestamp(value: str) -> int:
        from datetime import datetime, timezone

        value = value.strip()

        if value.endswith("Z"):
            value = value[:-1] + "+00:00"

        dt = datetime.fromisoformat(value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return int(dt.timestamp())

    @classmethod
    def _direct_fetch(
        cls,
        symbol: str,
        timeframe: str,
        count: int,
    ) -> List[Candle]:

        symbol = symbol.upper()
        timeframe = timeframe.upper()

        if timeframe not in INTERVAL_MAP:
            raise ValueError(
                f"Direct Twelve Data timeframe not supported: {timeframe}"
            )

        api_symbol = cls._symbol(symbol)
        interval = INTERVAL_MAP[timeframe]

        cls._check_quota_lock()
        cls._allow_request()

        params = {
            "symbol": api_symbol,
            "interval": interval,
            "outputsize": min(max(int(count), 1), 5000),
            "apikey": cls._api_key(),
            "timezone": "UTC",
            "order": "ASC",
        }

        response = requests.get(
            API_URL,
            params=params,
            timeout=TIMEOUT,
        )

        if response.status_code == 429:
            QUOTA_LOCK.parent.mkdir(parents=True, exist_ok=True)
            QUOTA_LOCK.touch()
            raise RuntimeError(
                "Twelve Data returned HTTP 429. "
                "Quota lock activated. Failing closed."
            )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, dict):
            raise RuntimeError(
                "Twelve Data returned invalid response."
            )

        if payload.get("status") == "error":
            message = payload.get("message", "Unknown Twelve Data error")
            raise RuntimeError(
                f"Twelve Data error: {message}"
            )

        values = payload.get("values")

        if not isinstance(values, list):
            raise RuntimeError(
                "Twelve Data response contains no candle values."
            )

        candles: List[Candle] = []

        for row in values:
            try:
                timestamp = cls._parse_timestamp(str(row["datetime"]))

                candle = Candle(
                    timestamp=timestamp,
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume", 0.0) or 0.0),
                )

                if not (
                    candle.low <= candle.open <= candle.high
                    and candle.low <= candle.close <= candle.high
                    and candle.high >= candle.low
                ):
                    continue

                candles.append(candle)

            except (KeyError, TypeError, ValueError):
                continue

        candles.sort(key=lambda c: c.timestamp)

        now = int(time.time())
        seconds = SECONDS[timeframe]

        # CLOSED CANDLES ONLY.
        candles = [
            c for c in candles
            if c.timestamp + seconds <= now
        ]

        if not candles:
            raise RuntimeError(
                f"No completed {timeframe} candles returned for {symbol}."
            )

        return candles[-count:]

    @classmethod
    def _aggregate(
        cls,
        candles: List[Candle],
        bucket_seconds: int,
    ) -> List[Candle]:

        if not candles:
            return []

        buckets: Dict[int, List[Candle]] = {}

        for candle in candles:
            bucket = (candle.timestamp // bucket_seconds) * bucket_seconds
            buckets.setdefault(bucket, []).append(candle)

        result: List[Candle] = []

        for timestamp in sorted(buckets):
            rows = sorted(
                buckets[timestamp],
                key=lambda c: c.timestamp
            )

            if not rows:
                continue

            expected = bucket_seconds // 900

            # Only aggregate complete M15 buckets for H1/H4.
            if bucket_seconds in (3600, 14400):
                if len(rows) != expected:
                    continue

                expected_ts = timestamp
                valid = True

                for row in rows:
                    if row.timestamp != expected_ts:
                        valid = False
                        break
                    expected_ts += 900

                if not valid:
                    continue

            result.append(
                Candle(
                    timestamp=timestamp,
                    open=rows[0].open,
                    high=max(r.high for r in rows),
                    low=min(r.low for r in rows),
                    close=rows[-1].close,
                    volume=sum(r.volume for r in rows),
                )
            )

        return result

    @classmethod
    def get_candles(
        cls,
        symbol: str,
        timeframe: str,
        count: int = 100,
    ) -> List[Candle]:

        symbol = symbol.upper()
        timeframe = timeframe.upper()
        count = int(count)

        if symbol not in SYMBOL_MAP:
            raise ValueError(f"Unsupported symbol: {symbol}")

        if count <= 0:
            raise ValueError("count must be greater than zero")

        key = cls._cache_key(symbol, timeframe, count)
        now = time.time()

        cached = cls._CANDLE_CACHE.get(key)

        if cached:
            cached_at, candles = cached

            if now - cached_at < CACHE_TTL.get(timeframe, 300):
                return list(candles)

        if timeframe in INTERVAL_MAP:
            candles = cls._direct_fetch(
                symbol,
                timeframe,
                count,
            )

        elif timeframe in DERIVED_FROM_M15:
            required = max(
                M15_HISTORY_FOR_DERIVED,
                count * DERIVED_FROM_M15[timeframe] + 32,
            )

            base = cls._direct_fetch(
                symbol,
                "M15",
                required,
            )

            candles = cls._aggregate(
                base,
                SECONDS[timeframe],
            )

            if len(candles) < count:
                raise RuntimeError(
                    f"Insufficient completed {timeframe} candles "
                    f"for {symbol}: {len(candles)} < {count}"
                )

            candles = candles[-count:]

        else:
            raise ValueError(
                f"Unsupported timeframe: {timeframe}"
            )

        if not candles:
            raise RuntimeError(
                f"EMPTY LIVE DATA: {symbol} {timeframe}"
            )

        cls._CANDLE_CACHE[key] = (
            now,
            list(candles),
        )

        return list(candles)


def get_candles(
    symbol: str,
    timeframe: str,
    count: int = 100,
) -> List[Candle]:
    return HttpCandleProvider.get_candles(
        symbol,
        timeframe,
        count,
    )
