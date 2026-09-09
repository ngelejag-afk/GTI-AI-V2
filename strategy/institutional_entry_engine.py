"""GTI-AI-V2 strict institutional SMC entry engine.
Signal calculation only: this module never sends an MT5 order.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Bar:
    t: int
    o: float
    h: float
    l: float
    c: float
    v: float = 0.0


class InstitutionalEntryEngine:
    """H4/H1 bias -> M5 liquidity/CHoCH/displacement -> M1 trigger."""

    MIN_BARS = 80
    LOOKBACK = 20

    @classmethod
    def scan(
        cls,
        market: dict[str, Any],
        *,
        bid: float | None = None,
        ask: float | None = None,
        dxy_signal: str = "NEUTRAL",
        news_safe: bool = False,
    ) -> dict:
        bars = {
            tf: cls._closed(market.get(tf, []))
            for tf in ("H4", "H1", "M15", "M5", "M1")
        }

        missing = [tf for tf in ("H4", "H1", "M5", "M1")
                   if len(bars[tf]) < cls.MIN_BARS]
        if missing:
            return cls._no("INSUFFICIENT_CLOSED_CANDLES", missing=missing)

        # Fail closed: macro/news is a mandatory gate.
        if dxy_signal == "NEUTRAL" or not news_safe:
            return cls._no(
                "MACRO_OR_NEWS_GATE_MISSING",
                dxy_signal=dxy_signal,
                news_safe=news_safe,
            )

        h4 = cls._trend(bars["H4"])
        h1 = cls._trend(bars["H1"])

        if h4 == "NEUTRAL" or h4 != h1:
            return cls._no("HTF_BIAS_CONFLICT", h4_bias=h4, h1_bias=h1)

        if h4 == "BUY" and dxy_signal != "USD_WEAKNESS":
            return cls._no("DXY_DOES_NOT_CONFIRM_BUY")
        if h4 == "SELL" and dxy_signal != "USD_STRENGTH":
            return cls._no("DXY_DOES_NOT_CONFIRM_SELL")

        sweep = cls._sweep(bars["M5"], h4)
        if not sweep:
            return cls._no(
                "WAITING_FOR_M5_LIQUIDITY_SWEEP",
                h4_bias=h4,
                h1_bias=h1,
            )

        choch = cls._choch(bars["M5"], h4)
        displacement = cls._displacement(bars["M5"], h4)
        zone = cls._zone(bars["M5"], h4)
        m1 = cls._m1_trigger(bars["M1"], h4, zone)

        if not (choch and displacement and zone and m1):
            return cls._no(
                "WAITING_FOR_EXECUTION_CONFLUENCE",
                h4_bias=h4,
                h1_bias=h1,
                liquidity_sweep=sweep,
                choch=choch,
                displacement=displacement,
                execution_zone=zone,
                m1_confirmation=m1,
            )

        current = ask if h4 == "BUY" else bid
        if current is None:
            return cls._no("LIVE_PRICE_MISSING", entry_zone=zone)

        zlow, zhigh, zkind = zone
        width = max(zhigh - zlow, 0.01)

        # Do not chase a missed zone.
        if h4 == "BUY" and current > zhigh + width:
            return cls._no("BUY_ZONE_MISSED", current=current, entry_zone=zone)
        if h4 == "SELL" and current < zlow - width:
            return cls._no("SELL_ZONE_MISSED", current=current, entry_zone=zone)

        entry = (zlow + zhigh) / 2.0
        buffer = max(width * 0.15, 0.03)

        if h4 == "BUY":
            sl = sweep["extreme"] - buffer
            risk = entry - sl
            tp1 = entry + 1.5 * risk
            tp2 = entry + 2.5 * risk
        else:
            sl = sweep["extreme"] + buffer
            risk = sl - entry
            tp1 = entry - 1.5 * risk
            tp2 = entry - 2.5 * risk

        if risk <= 0:
            return cls._no("INVALID_RISK_GEOMETRY")

        rr = abs(tp2 - entry) / risk
        if rr < 2.0:
            return cls._no("RISK_REWARD_BELOW_1_TO_2", rr=round(rr, 2))

        confidence = 100  # all required gates passed
        status = "ENTER NOW" if zlow <= current <= zhigh else "WAIT FOR RETEST"

        return {
            "status": status,
            "bias": h4,
            "confidence": confidence,
            "quality": "A+",
            "entry": round(entry, 5),
            "entry_zone": {
                "low": round(zlow, 5),
                "high": round(zhigh, 5),
                "kind": zkind,
            },
            "current_price": float(current),
            "sl": round(sl, 5),
            "tp1": round(tp1, 5),
            "tp2": round(tp2, 5),
            "invalidation": round(sl, 5),
            "rr": round(rr, 2),
            "h4_bias": h4,
            "h1_bias": h1,
            "dxy_signal": dxy_signal,
            "news_safe": news_safe,
            "liquidity_sweep": sweep,
            "choch": choch,
            "displacement": displacement,
            "m1_confirmation": m1,
            "core_thesis": [
                f"{'SSL' if h4 == 'BUY' else 'BSL'} swept at "
                f"{sweep['pool']:.5f}; wick extreme {sweep['extreme']:.5f}.",
                "M5 CHoCH + displacement confirmed; M1 trigger validated.",
                f"Entry anchored to {zkind} {zlow:.5f}-{zhigh:.5f}; no chase.",
            ],
            "failure_catalyst": (
                "Closed M5 invalidation beyond the sweep extreme, "
                "or DXY/news regime flip."
            ),
        }

    @staticmethod
    def _bar(x: Any) -> Bar:
        if isinstance(x, dict):
            return Bar(
                int(x.get("timestamp", x.get("time"))),
                float(x["open"]), float(x["high"]),
                float(x["low"]), float(x["close"]),
                float(x.get("volume", x.get("tick_volume", 0))),
            )
        return Bar(
            int(x["time"]), float(x["open"]), float(x["high"]),
            float(x["low"]), float(x["close"]),
            float(x.get("tick_volume", 0)),
        )

    @classmethod
    def _closed(cls, rows) -> list[Bar]:
        result = [cls._bar(x) for x in list(rows or [])]
        result.sort(key=lambda x: x.t)
        # MT5 position 0 is the still-forming candle.
        return result[:-1] if len(result) > 1 else []

    @staticmethod
    def _trend(x: list[Bar]) -> str:
        q = x[-20:]
        a = sum(z.c for z in q[:10]) / 10
        b = sum(z.c for z in q[10:]) / 10
        hi = max(z.h for z in q[10:]) - max(z.h for z in q[:10])
        lo = min(z.l for z in q[10:]) - min(z.l for z in q[:10])
        if b > a and hi > 0 and lo >= 0:
            return "BUY"
        if b < a and hi < 0 and lo <= 0:
            return "SELL"
        return "NEUTRAL"

    @classmethod
    def _sweep(cls, x: list[Bar], direction: str):
        cur = x[-1]
        prior = x[-(cls.LOOKBACK + 1):-1]

        if direction == "BUY":
            pool = min(z.l for z in prior)
            if cur.l < pool and cur.c > pool:
                return {
                    "direction": "BULLISH",
                    "pool": pool,
                    "extreme": cur.l,
                    "timestamp": cur.t,
                }
        else:
            pool = max(z.h for z in prior)
            if cur.h > pool and cur.c < pool:
                return {
                    "direction": "BEARISH",
                    "pool": pool,
                    "extreme": cur.h,
                    "timestamp": cur.t,
                }
        return None

    @staticmethod
    def _choch(x: list[Bar], direction: str) -> bool:
        q = x[-6:-1]
        c = x[-1]
        if direction == "BUY":
            return c.c > max(z.h for z in q)
        return c.c < min(z.l for z in q)

    @staticmethod
    def _displacement(x: list[Bar], direction: str) -> bool:
        c = x[-1]
        avg = sum(abs(z.c - z.o) for z in x[-6:-1]) / 5
        return (
            abs(c.c - c.o) >= avg * 1.5
            and (c.c > c.o if direction == "BUY" else c.c < c.o)
        )

    @staticmethod
    def _zone(x: list[Bar], direction: str):
        a, b, c = x[-3], x[-2], x[-1]

        if direction == "BUY" and c.l > a.h:
            return (a.h, c.l, "FVG")
        if direction == "SELL" and c.h < a.l:
            return (c.h, a.l, "FVG")

        if direction == "BUY" and b.c < b.o and c.c > b.h:
            return (b.l, b.h, "ORDER_BLOCK")
        if direction == "SELL" and b.c > b.o and c.c < b.l:
            return (b.l, b.h, "ORDER_BLOCK")

        return None

    @staticmethod
    def _m1_trigger(x: list[Bar], direction: str, zone) -> bool:
        if not zone:
            return False
        c, p = x[-1], x[-2]
        touched = c.l <= zone[1] and c.h >= zone[0]
        if not touched:
            return False
        if direction == "BUY":
            return c.c > p.h and c.c > c.o
        return c.c < p.l and c.c < c.o

    @staticmethod
    def _no(reason: str, **extra) -> dict:
        return {
            "status": "NO TRADE",
            "bias": "NEUTRAL",
            "confidence": 0,
            "quality": "C",
            "entry": None,
            "sl": None,
            "tp1": None,
            "tp2": None,
            "invalidation": None,
            "rr": None,
            "reason": reason,
            **extra,
        }
