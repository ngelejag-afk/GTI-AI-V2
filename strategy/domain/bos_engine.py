"""
GTI AI - Domain Layer
Break Of Structure (BOS) Engine (clean rebuild, Sprint 2)

Contract:
    Input:
        candles: sequence of CLOSED candles, oldest first.
        swings:  sequence of confirmed SwingPoint (from
                 SwingStructureEngine), any order.

    State tracked while scanning candles oldest -> newest:
        latest_unbroken_high  (most recent confirmed HIGH swing
                                not yet broken)
        latest_unbroken_low   (most recent confirmed LOW swing
                                not yet broken)

    Eligibility rule:
        A swing may only be used to evaluate a break on candle C
        if swing.timestamp < C.timestamp. A swing confirmed on
        the same candle as the break is NOT eligible.

    Break rule (CLOSE only, wicks never count):
        BULLISH BOS at candle C:
            C.close > latest_unbroken_high.price   (strict)
            -> emits a BOSEvent
            -> that HIGH is consumed; the next BULLISH BOS
               requires a newer confirmed HIGH swing.

        BEARISH BOS at candle C:
            C.close < latest_unbroken_low.price    (strict)
            -> emits a BOSEvent
            -> that LOW is consumed; the next BEARISH BOS
               requires a newer confirmed LOW swing.

    A bullish break only ever consumes the HIGH side; a bearish
    break only ever consumes the LOW side. The two sides are
    independent.

    Output:
        "INSUFFICIENT_DATA" if no swings were supplied at all.
        Otherwise a list of BOSEvent (possibly empty).

    Purity:
        Does not mutate `candles` or `swings`.
        Deterministic given the same inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Union

from strategy.domain.models import Candle
from strategy.domain.swing_structure import SwingPoint

INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True)
class BOSEvent:
    timestamp: int
    direction: str  # "BULLISH" or "BEARISH"
    broken_swing_price: float
    broken_swing_timestamp: int


class BOSEngine:
    """Detects confirmed Break Of Structure events from swing points."""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    INSUFFICIENT_DATA = INSUFFICIENT_DATA

    @staticmethod
    def analyze(
        candles: Sequence[Candle],
        swings: Sequence[SwingPoint],
    ) -> Union[str, List[BOSEvent]]:
        if not swings:
            return BOSEngine.INSUFFICIENT_DATA

        highs = sorted(
            (s for s in swings if s.type == "HIGH"),
            key=lambda s: s.timestamp,
        )
        lows = sorted(
            (s for s in swings if s.type == "LOW"),
            key=lambda s: s.timestamp,
        )

        events: List[BOSEvent] = []

        latest_unbroken_high: SwingPoint | None = None
        latest_unbroken_low: SwingPoint | None = None

        high_idx = 0
        low_idx = 0

        for candle in candles:
            # Admit newly eligible HIGH swings (strictly earlier
            # than this candle). Highs are sorted ascending, so
            # the last one admitted is always the most recent.
            while (
                high_idx < len(highs)
                and highs[high_idx].timestamp < candle.timestamp
            ):
                latest_unbroken_high = highs[high_idx]
                high_idx += 1

            while (
                low_idx < len(lows)
                and lows[low_idx].timestamp < candle.timestamp
            ):
                latest_unbroken_low = lows[low_idx]
                low_idx += 1

            if (
                latest_unbroken_high is not None
                and candle.close > latest_unbroken_high.price
            ):
                events.append(
                    BOSEvent(
                        timestamp=candle.timestamp,
                        direction=BOSEngine.BULLISH,
                        broken_swing_price=latest_unbroken_high.price,
                        broken_swing_timestamp=latest_unbroken_high.timestamp,
                    )
                )
                latest_unbroken_high = None  # consumed

            if (
                latest_unbroken_low is not None
                and candle.close < latest_unbroken_low.price
            ):
                events.append(
                    BOSEvent(
                        timestamp=candle.timestamp,
                        direction=BOSEngine.BEARISH,
                        broken_swing_price=latest_unbroken_low.price,
                        broken_swing_timestamp=latest_unbroken_low.timestamp,
                    )
                )
                latest_unbroken_low = None  # consumed

        return events
