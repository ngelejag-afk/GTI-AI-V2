"""
GTI AI - Domain Layer
Swing Structure Engine (clean rebuild, Sprint 2)

Contract:
    Input: a sequence of CLOSED candles, oldest first.
    Fractal window: 2 candles left, 2 candles right (5-candle window).

    A candidate candle at index i is a confirmed SWING HIGH if:
        candles[i].high is strictly greater than the high of
        candles[i-2], [i-1], [i+1], [i+2].

    A candidate candle at index i is a confirmed SWING LOW if:
        candles[i].low is strictly lower than the low of
        candles[i-2], [i-1], [i+1], [i+2].

    Strict inequality only. Equal highs/lows do NOT count as a swing.

    Causality / confirmation latency:
        A swing at candle index i cannot be known until candles
        i+1 and i+2 have themselves closed. This engine only
        ever looks at candles that are already in the input
        list, so as long as the caller only passes CLOSED
        candles, this constraint is satisfied automatically —
        a swing at the last two positions of the input can
        never be returned, because there is no i+1/i+2 data
        yet to confirm it.

    Output:
        - "INSUFFICIENT_DATA" if fewer than 5 candles supplied.
        - Otherwise, a list of SwingPoint (possibly empty).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Union

from strategy.domain.models import Candle

SWING_LEFT = 2
SWING_RIGHT = 2
WINDOW = SWING_LEFT + SWING_RIGHT + 1

INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True)
class SwingPoint:
    timestamp: int
    price: float
    type: str  # "HIGH" or "LOW"


class SwingStructureEngine:
    """Detects confirmed fractal swing highs/lows."""

    HIGH = "HIGH"
    LOW = "LOW"
    INSUFFICIENT_DATA = INSUFFICIENT_DATA

    @staticmethod
    def analyze(
        candles: Sequence[Candle],
    ) -> Union[str, List[SwingPoint]]:
        """
        Return INSUFFICIENT_DATA (str) if fewer than WINDOW candles.
        Otherwise return a list of confirmed SwingPoint (may be empty).
        """
        if len(candles) < WINDOW:
            return SwingStructureEngine.INSUFFICIENT_DATA

        swings: List[SwingPoint] = []

        # Only indices that have a full window on both sides
        # can ever be evaluated. Since we only receive CLOSED
        # candles, this naturally enforces the T+2 confirmation
        # latency: the last SWING_RIGHT candles can never be
        # a confirmed swing point given this input alone.
        for i in range(SWING_LEFT, len(candles) - SWING_RIGHT):
            candidate = candles[i]
            left = candles[i - SWING_LEFT:i]
            right = candles[i + 1:i + 1 + SWING_RIGHT]
            neighborhood = list(left) + list(right)

            is_high = all(
                candidate.high > other.high for other in neighborhood
            )
            is_low = all(
                candidate.low < other.low for other in neighborhood
            )

            if is_high:
                swings.append(
                    SwingPoint(
                        timestamp=candidate.timestamp,
                        price=candidate.high,
                        type=SwingStructureEngine.HIGH,
                    )
                )

            if is_low:
                swings.append(
                    SwingPoint(
                        timestamp=candidate.timestamp,
                        price=candidate.low,
                        type=SwingStructureEngine.LOW,
                    )
                )

        return swings
