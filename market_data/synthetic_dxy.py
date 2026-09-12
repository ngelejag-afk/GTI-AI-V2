from __future__ import annotations

import math
import time
from datetime import datetime, timezone

import requests


class SyntheticDXY:
    """
    Synthetic US Dollar Index using the six ICE-weighted FX components.

    Only fully closed H1 candles are accepted.
    Used for macro bias filtering, not tick-for-tick ICE replication.
    """

    URL = "https://api.twelvedata.com/time_series"

    WEIGHTS = {
        "EUR/USD": -0.576,
        "USD/JPY": 0.136,
        "GBP/USD": -0.119,
        "USD/CAD": 0.091,
        "USD/SEK": 0.042,
        "USD/CHF": 0.036,
    }

    CONSTANT = 50.14348112
    INTERVAL_SECONDS = 3600
    _LAST_REQUEST = 0.0
    _MIN_REQUEST_INTERVAL = 2.0

    @classmethod
    def get_closes(
        cls,
        key: str,
        count: int = 200,
    ) -> dict[str, list[float]]:
        result = {}
        timestamps = {}

        now_utc = int(time.time())

        for symbol in cls.WEIGHTS:
            elapsed = time.monotonic() - cls._LAST_REQUEST
            if elapsed < cls._MIN_REQUEST_INTERVAL:
                time.sleep(cls._MIN_REQUEST_INTERVAL - elapsed)

            cls._LAST_REQUEST = time.monotonic()

            last_error = None

            for attempt in range(4):
                try:
                    response = requests.get(
                        cls.URL,
                        params={
                            "symbol": symbol,
                            "interval": "1h",
                            "outputsize": count + 5,
                            "timezone": "UTC",
                            "apikey": key,
                        },
                        timeout=20,
                    )

                    if response.status_code in (429, 502, 503, 504):
                        if attempt < 3:
                            time.sleep(2 ** attempt)
                            continue
                        response.raise_for_status()

                    response.raise_for_status()
                    data = response.json()
                    break

                except (requests.RequestException, TimeoutError) as exc:
                    last_error = exc
                    if attempt >= 3:
                        raise
                    time.sleep(2 ** attempt)

            if "values" not in data:
                raise RuntimeError(
                    f"DXY_COMPONENT_ERROR:{symbol}:"
                    f"{data.get('message', 'unknown')}"
                )

            closed = []

            for candle in data["values"]:
                try:
                    dt = datetime.strptime(
                        candle["datetime"],
                        "%Y-%m-%d %H:%M:%S",
                    ).replace(tzinfo=timezone.utc)

                    candle_start = int(dt.timestamp())

                    if candle_start + cls.INTERVAL_SECONDS <= now_utc:
                        closed.append(
                            (
                                candle_start,
                                float(candle["close"]),
                            )
                        )

                except (KeyError, TypeError, ValueError):
                    continue

            closed.sort(key=lambda x: x[0])

            if len(closed) < count:
                raise RuntimeError(
                    f"INSUFFICIENT_CLOSED_DXY_COMPONENT:"
                    f"{symbol}:{len(closed)}"
                )

            selected = closed[-count:]
            result[symbol] = [price for _, price in selected]
            timestamps[symbol] = [ts for ts, _ in selected]

        reference = timestamps[next(iter(cls.WEIGHTS))]

        for symbol, ts_list in timestamps.items():
            if ts_list != reference:
                raise RuntimeError(
                    f"DXY_TIMESTAMP_MISMATCH:{symbol}"
                )

        return result

    @classmethod
    def calculate(
        cls,
        components: dict[str, list[float]],
    ) -> list[float]:
        lengths = {len(v) for v in components.values()}

        if len(lengths) != 1:
            raise RuntimeError("DXY_COMPONENT_LENGTH_MISMATCH")

        count = lengths.pop()

        if count < 200:
            raise RuntimeError(
                f"INSUFFICIENT_SYNTHETIC_DXY_BARS:{count}"
            )

        dxy = []

        for i in range(count):
            value = cls.CONSTANT

            for symbol, exponent in cls.WEIGHTS.items():
                price = float(components[symbol][i])

                if price <= 0:
                    raise RuntimeError(
                        f"INVALID_DXY_COMPONENT_PRICE:"
                        f"{symbol}:{price}"
                    )

                value *= math.pow(price, exponent)

            dxy.append(value)

        return dxy

    @classmethod
    def build(
        cls,
        key: str,
        count: int = 200,
    ) -> list[float]:
        components = cls.get_closes(key, count=count)
        return cls.calculate(components)
