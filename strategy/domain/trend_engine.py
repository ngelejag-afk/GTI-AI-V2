"""
GTI AI - Domain Layer
Trend Engine (clean rebuild, Sprint 2)

Contract:
    Input: a sequence of CLOSED candles, oldest first.
          The caller is responsible for never including
          a still-forming candle. This engine performs no
          time-based validation of its own; it trusts the
          sequence it is given.
    Output: TrendEngine.Result — one of:
          "BULLISH"           EMA20 > EMA50 > EMA200
          "BEARISH"           EMA20 < EMA50 < EMA200
          "NEUTRAL"           EMAs computed but not aligned
          "INSUFFICIENT_DATA" fewer closed candles than EMA200 needs

    Determinism: pure function of the input sequence.
    No mutation of the input list.
"""

from __future__ import annotations

from typing import List, Sequence

from strategy.domain.models import Candle

EMA_FAST = 20
EMA_MID = 50
EMA_SLOW = 200


def _ema_series(values: Sequence[float], period: int) -> List[float]:
    """Standard EMA series. Returns [] if not enough values."""
    if len(values) < period:
        return []

    multiplier = 2.0 / (period + 1)
    ema = [sum(values[:period]) / period]

    for value in values[period:]:
        ema.append((value - ema[-1]) * multiplier + ema[-1])

    return ema


class TrendEngine:
    """Determines trend using strict EMA20/50/200 alignment."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

    @staticmethod
    def analyze(candles: Sequence[Candle]) -> str:
        """
        Analyze trend from a sequence of CLOSED candles.

        The caller must ensure the last element of `candles`
        is a fully closed candle. This function does not and
        cannot verify that on its own.
        """
        closes = [candle.close for candle in candles]

        if len(closes) < EMA_SLOW:
            return TrendEngine.INSUFFICIENT_DATA

        ema20_series = _ema_series(closes, EMA_FAST)
        ema50_series = _ema_series(closes, EMA_MID)
        ema200_series = _ema_series(closes, EMA_SLOW)

        ema20 = ema20_series[-1]
        ema50 = ema50_series[-1]
        ema200 = ema200_series[-1]

        if ema20 > ema50 > ema200:
            return TrendEngine.BULLISH

        if ema20 < ema50 < ema200:
            return TrendEngine.BEARISH

        return TrendEngine.NEUTRAL
