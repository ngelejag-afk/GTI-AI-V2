from __future__ import annotations

from datetime import datetime, timezone
import requests


class BiquoteDXY:
    URL = "https://biquote.io/api/DXY/ohlc"

    @classmethod
    def get_closed_closes(cls, interval: str = "1h", limit: int = 250) -> list[float]:
        response = requests.get(
            cls.URL,
            params={"interval": interval, "limit": limit},
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        bars = data.get("bars", [])

        if not bars:
            raise RuntimeError("NO_DXY_OHLC_BARS")

        closed = [
            bar for bar in bars
            if bar.get("isOpen") is False
            and bar.get("close") is not None
        ]

        closed.sort(key=lambda x: x["openTime"])

        if len(closed) < 200:
            raise RuntimeError(
                f"INSUFFICIENT_DXY_CLOSED_BARS:{len(closed)}"
            )

        return [float(bar["close"]) for bar in closed[-limit:]]
